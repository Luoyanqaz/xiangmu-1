"""
问卷系统视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core import signing
from django.db.models import F
from django.utils import timezone
from datetime import timedelta

from .models import SurveyTemplate, SurveyQuestion, SurveyInstance, SurveyResponse
from .serializers import (
    SurveyTemplateSerializer, SurveyInstanceSerializer, 
    SurveyResponseSerializer, SurveySubmitSerializer
)
from apps.assessments.models import Assessment
from . import quality

from django.conf import settings
from .utils.qrcode_utils import generate_qrcode_and_save



class SurveyInstanceViewSet(viewsets.ModelViewSet):
    """问卷实例视图集"""
    serializer_class = SurveyInstanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户学校的问卷实例"""
        user = self.request.user
        if user.is_admin_user():
            return SurveyInstance.objects.all()
        
        # 学校用户只能看到自己学校的问卷实例
        return SurveyInstance.objects.filter(
            assessment__school__user=user
        ).select_related('template', 'assessment__school')
    
    def create(self, request, *args, **kwargs):
        """创建问卷实例"""
        assessment_id = request.data.get('assessment_id')
        survey_type = request.data.get('survey_type')
        if survey_type not in ['teacher', 'student']:
            return Response(
                {'error': '当前仅支持创建教师问卷和学生问卷'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证评估记录
        assessment = get_object_or_404(Assessment, id=assessment_id)
        
        # 验证权限：只能为自己学校的评估创建问卷
        if not request.user.is_admin_user():
            if assessment.school.user != request.user:
                return Response(
                    {'error': '无权限为其他学校创建问卷'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # 获取问卷模板
        template = get_object_or_404(SurveyTemplate, survey_type=survey_type, is_active=True)
        
        # 检查是否已存在该类型的问卷实例
        existing_instance = SurveyInstance.objects.filter(
            assessment=assessment,
            template=template
        ).first()
        
        if existing_instance:
            # 如果已存在，直接返回现有实例
            serializer = self.get_serializer(existing_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # 计算截止时间：学校用户创建时间 + 120小时
        school_user = assessment.school.user
        expired_at = timezone.now() + timedelta(hours=120)
        
        # 创建问卷实例（不需要设置目标数量）
        instance = SurveyInstance.objects.create(
            assessment=assessment,
            template=template,
            target_count=0,  # 不限制数量
            expired_at=expired_at
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def regenerate_link(self, request, pk=None):
        """重新生成分享链接（生成新的UUID）"""
        instance = self.get_object()
        
        # 验证权限
        if not request.user.is_admin_user():
            if instance.assessment.school.user != request.user:
                return Response(
                    {'error': '无权限操作此问卷'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # 生成新的UUID
        import uuid
        instance.uuid = uuid.uuid4()
        instance.save(update_fields=['uuid'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取问卷统计信息"""
        instance = self.get_object()
        
        # 验证权限
        if not request.user.is_admin_user():
            if instance.assessment.school.user != request.user:
                return Response(
                    {'error': '无权限查看此问卷统计'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # 获取所有回答
        responses = instance.responses.all()
        
        # 统计数据
        stats = {
            'total_responses': responses.count(),
        'valid_count': responses.filter(is_valid=True).count() if instance.assessment.check_survey_quality else None,
            'target_count': instance.target_count,
            'completion_rate': round(responses.count() / instance.target_count * 100, 2) if instance.target_count > 0 else 0,
            'is_active': instance.is_active,
            'created_at': instance.created_at,
            'expired_at': instance.expired_at
        }
        
        return Response(stats)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_survey_by_uuid(request, uuid):
    """通过UUID获取问卷内容（公开接口）"""
    instance = get_object_or_404(SurveyInstance, uuid=uuid, is_active=True)
    if instance.assessment.check_survey_quality and instance.assessment.status != 'draft':
        return Response({'error': '本轮评估已提交，问卷已停止收集'}, status=403)
    
    # 检查是否过期
    if instance.expired_at and timezone.now() > instance.expired_at:
        return Response(
            {'error': '问卷已过期'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 获取问卷模板和题目
    template = instance.template
    questions = template.questions.all().order_by('order')
    
    data = {
        'title': template.title,
        'description': template.description,
        'survey_type': template.survey_type,
        'questions': [
            {
                'id': q.id,
                'question_text': q.question_text,
                'question_type': q.question_type,
                'options': q.options,
                'order': q.order,
                'is_required': q.is_required
            }
            for q in questions
        ]
    }
    
    if instance.assessment.check_survey_quality and template.survey_type in quality.ROLES:
        data['questions'].append({
            'id': quality.ATTENTION, 'order': quality.ATTENTION, 'is_required': True,
            'question_type': 'single_choice', 'options': ['非常不符合', '不符合', '一般', '符合', '非常符合'],
            'question_text': '为确认您已阅读题目，请在本题选择“不符合”。',
        })
        data['attempt'] = quality.issue_attempt(instance, data['questions'])
    response = Response(data)
    response['Cache-Control'] = 'no-store'
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_survey(request, uuid):
    """提交问卷答案（公开接口）"""
    instance = get_object_or_404(SurveyInstance, uuid=uuid, is_active=True)
    
    # 验证数据
    serializer = SurveySubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    answers = serializer.validated_data['answers']
    
    # 获取客户端IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    # 保存问卷回答
    with transaction.atomic():
        assessment = Assessment.objects.select_for_update().get(pk=instance.assessment_id)
        instance = get_object_or_404(SurveyInstance.objects.select_for_update(), pk=instance.pk, uuid=uuid, is_active=True)
        fields = {}
        if assessment.check_survey_quality and instance.template.survey_type in quality.ROLES:
            try:
                attempt = signing.loads(serializer.validated_data.get('attempt', ''), salt=quality.SALT)
            except signing.BadSignature:
                return Response({'error': '作答记录无效，请刷新问卷后重新填写'}, status=400)
            if attempt['link'] != str(instance.uuid) or 'elapsed_ms' not in serializer.validated_data:
                return Response({'error': '作答记录与问卷不匹配，请重新打开问卷'}, status=400)
            previous = SurveyResponse.objects.filter(instance=instance, attempt_id=attempt['id']).first()
            if previous:
                return Response({'message': '提交成功', 'response_id': previous.pk})
            if any(answers.get(key) in (None, '', []) for key in attempt['required']):
                return Response({'error': '请先完成全部必答题'}, status=400)
            details = quality.evaluate(attempt, answers, serializer.validated_data['elapsed_ms'])
            valid = not details['reasons']
            fields = {'is_valid': valid, 'quality_details': details, 'attempt_id': attempt['id']}
            answers = {key: value for key, value in answers.items() if key != 'q' + quality.ATTENTION} if valid else {}
        if assessment.status != 'draft':
            return Response({'error': '该评估已提交，无法继续提交问卷'}, status=403)
        if instance.expired_at and timezone.now() > instance.expired_at:
            return Response({'error': '问卷已过期'}, status=400)
        response = SurveyResponse.objects.create(
            instance=instance,
            answers=answers,
            ip_address=ip_address, **fields
        )
        
        # 更新已收集数量
        SurveyInstance.objects.filter(pk=instance.pk).update(collected_count=F('collected_count') + 1)
    
    return Response(
        {'message': '提交成功', 'response_id': response.id},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assessment_surveys(request, assessment_id):
    """获取某个评估的所有问卷实例"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # 验证权限
    if not request.user.is_admin_user():
        if assessment.school.user != request.user:
            return Response(
                {'error': '无权限查看此评估的问卷'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    instances = SurveyInstance.objects.filter(assessment=assessment).select_related('template')
    serializer = SurveyInstanceSerializer(instances, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def publish_literacy_surveys(request, assessment_id):
    """
    数据素养（A维度）问卷发布：teacher/manager/student 三份
    - 若实例不存在：自动创建
    - 返回：每份问卷的公开链接（uuid） + 二维码图片地址
    """
    assessment = get_object_or_404(Assessment, id=assessment_id)

    # 权限校验：学校用户只能操作自己学校
    if not request.user.is_admin_user():
        if assessment.school.user != request.user:
            return Response(
                {'error': '无权限操作此评估的问卷'},
                status=status.HTTP_403_FORBIDDEN
            )

    # 两类问卷
    survey_types = ['teacher', 'student']

    expired_at = timezone.now() + timedelta(hours=120)

    instances = {}
    with transaction.atomic():
        for s_type in survey_types:
            template = get_object_or_404(SurveyTemplate, survey_type=s_type, is_active=True)

            inst = SurveyInstance.objects.filter(
                assessment=assessment,
                template=template
            ).first()

            if not inst:
                inst = SurveyInstance.objects.create(
                    assessment=assessment,
                    template=template,
                    target_count=0,
                    expired_at=expired_at
                )
            instances[s_type] = inst

    # 生成公开填写链接（用 uuid 的公开接口）
    # 你前端实际填写页路由若不是 /survey/{uuid}，就在这里改成你的路由
    base = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')

    def build_public_url(inst: SurveyInstance) -> str:
        return f"{base}/survey/{inst.uuid}"  # 例如：前端页面通过 uuid 拉取问卷内容

    data = {}
    for s_type, inst in instances.items():
        url = build_public_url(inst)
        qr = generate_qrcode_and_save(url, prefix=s_type)
        data[s_type] = {
            "instance_id": inst.id,
            "uuid": str(inst.uuid),
            "url": url,
            "qrcode": qr,
            "expired_at": inst.expired_at,
        }

    return Response({
        "success": True,
        "assessment_id": assessment.id,
        "data": data
    }, status=status.HTTP_200_OK)
