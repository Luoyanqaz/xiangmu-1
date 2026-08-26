"""
评估系统视图
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import Assessment, InstitutionAssessment, BehaviorAssessment, AssetAssessment, TechnologyAssessment
from .serializers import (
    AssessmentSerializer, InstitutionAssessmentSerializer,
    BehaviorAssessmentSerializer, AssetAssessmentSerializer, TechnologyAssessmentSerializer
)
from apps.regions.services import get_or_create_region_by_text
from apps.regions.utils.generators import gen_unique_school_username, gen_strong_password
from django.db import transaction
from apps.schools.models import School
import logging
from apps.surveys.models import SurveyInstance, SurveyResponse
from .scoring_service import  ScoringService

from ..accounts.models import User

logger = logging.getLogger(__name__)

ASSESSMENT_DURATION_HOURS = 120


def finalize_expired_draft_assessments(queryset):
    """将超过填报期限仍未提交的评估按 0 分结算。"""
    cutoff = timezone.now() - timedelta(hours=ASSESSMENT_DURATION_HOURS)
    expired_ids = list(
        queryset.filter(status='draft', created_at__lte=cutoff)
        .values_list('id', flat=True)
    )

    if not expired_ids:
        return []

    completed_at = timezone.now()
    with transaction.atomic():
        Assessment.objects.filter(id__in=expired_ids, status='draft').update(
            literacy_score=0,
            institution_score=0,
            behavior_score=0,
            asset_score=0,
            technology_score=0,
            total_score=0,
            maturity_level='initial',
            status='completed',
            completed_at=completed_at,
            ai_suggestions={},
        )
        SurveyInstance.objects.filter(
            assessment_id__in=expired_ids,
            is_active=True,
        ).update(is_active=False)

    logger.info("已将超时未提交评估按 0 分结算: %s", expired_ids)
    return expired_ids


class AssessmentViewSet(viewsets.ModelViewSet):
    """评估记录视图集"""
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # 禁用分页

    # apps/assessments/views.py

    # apps/assessments/views.py
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """
        获取评估详细数据：绕过自动权限检查，直接使用 get_queryset 结果
        """
        try:
            assessment = self.get_queryset().get(pk=pk)
        except Assessment.DoesNotExist:
            return Response(
                {"detail": "未找到评估记录或您没有权限访问"},
                status=403
            )

        # 聚合各模块数据
        institution, _ = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        behavior, _ = BehaviorAssessment.objects.get_or_create(assessment=assessment)
        asset, _ = AssetAssessment.objects.get_or_create(assessment=assessment)
        technology, _ = TechnologyAssessment.objects.get_or_create(assessment=assessment)

        school = assessment.school

        def to_float(value, default=0.0):
            try:
                if value is None:
                    return default
                return float(value)
            except (TypeError, ValueError):
                return default

        # 一级维度得分：优先使用重新计算结果，失败时使用 Assessment 已保存结果
        dimension_scores = {
            'literacy': to_float(assessment.literacy_score),
            'institution': to_float(assessment.institution_score),
            'behavior': to_float(assessment.behavior_score),
            'asset': to_float(assessment.asset_score),
            'technology': to_float(assessment.technology_score),
        }

        secondary_scores = {}
        observation_scores = {}

        # 重新计算报告展示所需的二级指标和观测点得分
        try:
            scoring_service = ScoringService(assessment)

            literacy_score = scoring_service.calculate_literacy_score()
            institution_score = scoring_service.calculate_institution_score()
            behavior_score = scoring_service.calculate_behavior_score()
            asset_score = scoring_service.calculate_asset_score()
            technology_score = scoring_service.calculate_technology_score()

            dimension_scores = {
                'literacy': to_float(literacy_score, dimension_scores['literacy']),
                'institution': to_float(institution_score, dimension_scores['institution']),
                'behavior': to_float(behavior_score, dimension_scores['behavior']),
                'asset': to_float(asset_score, dimension_scores['asset']),
                'technology': to_float(technology_score, dimension_scores['technology']),
            }

            secondary_scores = scoring_service.secondary_scores or {}
            observation_scores = scoring_service.observation_scores or {}

        except Exception as e:
            # 不让计分异常影响报告基础数据返回
            logger.error(f"报告 data 接口重新计算指标得分失败：{str(e)}", exc_info=True)

        # 统计教师、学生问卷参评人数
        participant_counts = {
            'teacher': SurveyResponse.objects.filter(
                instance__assessment=assessment,
                instance__template__survey_type='teacher'
            ).count(),
            'student': SurveyResponse.objects.filter(
                instance__assessment=assessment,
                instance__template__survey_type='student'
            ).count(),
        }

        # 报告页需要展示真实的全库平均分，避免前端长期使用 3.00 兜底值。
        from apps.reports.report_data_service import ReportDataService
        average_scores = ReportDataService(
            assessment,
            scoring_service=scoring_service if 'scoring_service' in locals() else None,
        ).get_average_scores()

        # 正常的大模型建议直接复用；仅对已识别为兜底文案的部分重新调用并更新缓存。
        from apps.reports.report_ai_service import ReportAIService
        suggestion_service = ReportAIService()
        suggestion_report_data = {
            'total_score': to_float(assessment.total_score),
            'maturity_level': assessment.get_maturity_level_display(),
            'dimension_scores': dimension_scores,
            'secondary_scores': secondary_scores,
            'observation_scores': observation_scores,
        }
        suggestions = suggestion_service.normalize_cached_suggestions(
            suggestion_report_data,
            assessment.ai_suggestions or {},
        )
        suggestions = suggestion_service.regenerate_fallback_suggestions(
            suggestion_report_data,
            suggestions,
        )
        if suggestions != (assessment.ai_suggestions or {}):
            assessment.ai_suggestions = suggestions
            assessment.save(update_fields=['ai_suggestions'])

        return Response({
            # 后端生成的 AI 建议
            'suggestions': suggestions,

            # 报告页需要的完整得分
            'dimension_scores': dimension_scores,
            'secondary_scores': secondary_scores,
            'observation_scores': observation_scores,
            'average_scores': average_scores,

            # 问卷参评人数
            'participant_counts': participant_counts,

            # 模块基础数据
            'assessment': AssessmentSerializer(assessment).data,
            'institution': InstitutionAssessmentSerializer(institution).data,
            'behavior': BehaviorAssessmentSerializer(behavior).data,
            'asset': AssetAssessmentSerializer(asset).data,
            'technology': TechnologyAssessmentSerializer(technology).data,

            # 学校基础信息
            'school_name': school.name,
            'school_type': school.school_type,
            'province': school.province,
            'city': school.city,
            'district': school.district,
            'founding_year': school.founding_year,
            'teacher_count': school.teacher_count,
            'student_count': school.student_count,

            # 兼容旧前端 scores 读取
            'scores': {
                'total_score': str(assessment.total_score),
                'maturity_level': assessment.maturity_level,
                'maturity_level_display': assessment.get_maturity_level_display(),
            }
        })


    def get_queryset(self):
        user = self.request.user

        # 针对 Swagger 等工具的保护及未登录拦截
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Assessment.objects.none()

        # 1. 超级管理员 (Admin)：拥有上帝视角，看全校数据
        if hasattr(user, 'is_admin_user') and user.is_admin_user():
            queryset = Assessment.objects.all()
            finalize_expired_draft_assessments(queryset)
            return queryset

        # 2. 区域管理员 (Region Admin)：看自己管辖区域下的学校数据
        # 逻辑：Assessment -> School -> Region -> region_admin (当前用户)
        if hasattr(user, 'role') and user.role == 'region_admin':
            queryset = Assessment.objects.filter(school__region__region_admin=user)
            finalize_expired_draft_assessments(queryset)
            return queryset

        # 3. 学校用户 (School)：只能看到自己学校的数据
        try:
            if hasattr(user, 'school'):
                queryset = Assessment.objects.filter(school=user.school)
                finalize_expired_draft_assessments(queryset)
                return queryset
        except Exception:
            pass

        return Assessment.objects.none()

    def create(self, request, *args, **kwargs):
        """创建新评估 - 允许历史记录"""
        user = request.user
        school = user.school

        # 创建新评估前先结算已超时草稿，避免旧草稿永久阻塞新一轮评估。
        finalize_expired_draft_assessments(Assessment.objects.filter(school=school))

        # 核心逻辑：检查是否【当前】有正在填写的评估
        # 只要状态不是 'completed'，就不允许开新的，必须把手头这份做完
        ongoing = Assessment.objects.filter(school=school).exclude(status='completed').first()

        if ongoing:
            if ongoing.status == 'draft':
                # 如果是草稿，直接返回旧的，让用户继续填
                serializer = self.get_serializer(ongoing)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': '当前已有评估正在处理中，请完成后再发起新评估'}, status=400)

        # 如果之前的都已完成（completed），则创建一份全新的记录
        assessment = Assessment.objects.create(school=school, status='draft')

        # 必须手动初始化子表，否则后面 save_xxx 会报错
        InstitutionAssessment.objects.create(assessment=assessment)
        BehaviorAssessment.objects.create(assessment=assessment)
        AssetAssessment.objects.create(assessment=assessment)
        TechnologyAssessment.objects.create(assessment=assessment)

        serializer = self.get_serializer(assessment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def admin_list(self, request):
        """管理员获取评估列表（带分页和筛选）"""
        if not request.user.is_admin_user():
            return Response(
                {'error': '只有管理员可以访问'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = Assessment.objects.all().order_by('-created_at')
        
        # 筛选
        school_name = request.query_params.get('school_name')
        status_param = request.query_params.get('status')
        
        if school_name:
            queryset = queryset.filter(school__name__icontains=school_name)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # 分页
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def institution(self, request, pk=None):
        """获取数据制度评估数据"""
        try:
            assessment = self.get_queryset().get(pk=pk)  # 修改点
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        institution, created = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        serializer = InstitutionAssessmentSerializer(institution)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def save_institution(self, request, pk=None):
        """保存数据制度评估数据"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许修改
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法修改数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        institution, created = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        serializer = InstitutionAssessmentSerializer(institution, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='institution/upload')
    def upload_institution_file(self, request, pk=None):
        """上传数据制度文件"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许上传
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法上传文件'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        institution, created = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        
        file_type = request.data.get('file_type')  # 'management' or 'practice'
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存文件
        from django.core.files.storage import default_storage
        file_path = f'institutions/{assessment.school.id}/{uploaded_file.name}'
        saved_path = default_storage.save(file_path, uploaded_file)
        
        # 获取URL（适配OSS）
        file_url = default_storage.url(saved_path)
        if not file_url.startswith('http'):
            file_url = request.build_absolute_uri(file_url)
        
        # 更新文件列表
        file_info = {
            'name': uploaded_file.name,
            'path': saved_path,
            'url': file_url,
            'size': uploaded_file.size,
            'uploaded_at': timezone.now().isoformat()
        }
        
        if file_type == 'management':
            files = institution.management_doc_files or []
            files.append(file_info)
            institution.management_doc_files = files
        elif file_type == 'practice':
            files = institution.practice_doc_files or []
            files.append(file_info)
            institution.practice_doc_files = files
        else:
            return Response({'error': '无效的文件类型'}, status=status.HTTP_400_BAD_REQUEST)
        
        institution.save()
        
        return Response({
            'message': '文件上传成功',
            'file': file_info
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='institution/delete-file')
    def delete_institution_file(self, request, pk=None):
        """删除数据制度文件"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许删除
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法删除文件'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        institution, created = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        
        file_type = request.data.get('file_type')  # 'management' or 'practice'
        file_path = request.data.get('file_path')  # 要删除的文件路径
        
        if not file_path:
            return Response({'error': '未指定文件路径'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 从数据库中删除文件记录
            if file_type == 'management':
                files = institution.management_doc_files or []
                # 过滤掉要删除的文件
                updated_files = [f for f in files if f.get('path') != file_path]
                institution.management_doc_files = updated_files
            elif file_type == 'practice':
                files = institution.practice_doc_files or []
                updated_files = [f for f in files if f.get('path') != file_path]
                institution.practice_doc_files = updated_files
            else:
                return Response({'error': '无效的文件类型'}, status=status.HTTP_400_BAD_REQUEST)
            
            institution.save()
            
            # 尝试删除物理文件（可选，失败不影响数据库操作）
            try:
                from django.core.files.storage import default_storage
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                    logger.info(f"已删除物理文件: {file_path}")
            except Exception as e:
                logger.warning(f"删除物理文件失败: {str(e)}")
            
            return Response({
                'message': '文件删除成功',
                'file_path': file_path
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}", exc_info=True)
            return Response(
                {'error': f'删除文件失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def behavior(self, request, pk=None):
        """获取数据行为评估数据"""
        try:
            assessment = self.get_queryset().get(pk=pk)  # 修改点
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        behavior, created = BehaviorAssessment.objects.get_or_create(assessment=assessment)
        serializer = BehaviorAssessmentSerializer(behavior)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def save_behavior(self, request, pk=None):
        """保存数据行为评估数据"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许修改
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法修改数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        behavior, created = BehaviorAssessment.objects.get_or_create(assessment=assessment)
        serializer = BehaviorAssessmentSerializer(behavior, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def asset(self, request, pk=None):
        """获取数据资产评估数据"""
        try:
            assessment = self.get_queryset().get(pk=pk)  # 修改点
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        asset, created = AssetAssessment.objects.get_or_create(assessment=assessment)
        serializer = AssetAssessmentSerializer(asset)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def save_asset(self, request, pk=None):
        """保存数据资产评估数据"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许修改
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法修改数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        asset, created = AssetAssessment.objects.get_or_create(assessment=assessment)
        serializer = AssetAssessmentSerializer(asset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def technology(self, request, pk=None):
        """获取数据技术评估数据"""
        try:
            assessment = self.get_queryset().get(pk=pk)  # 修改点
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        technology, created = TechnologyAssessment.objects.get_or_create(assessment=assessment)
        serializer = TechnologyAssessmentSerializer(technology)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def save_technology(self, request, pk=None):
        """保存数据技术评估数据"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许修改
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法修改数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        technology, created = TechnologyAssessment.objects.get_or_create(assessment=assessment)
        serializer = TechnologyAssessmentSerializer(technology, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        提交评估，触发计分任务
        """
        assessment = self.get_object()
        
        # 检查评估状态
        if assessment.status == 'completed':
            return Response(
                {'error': '评估已完成，无法重复提交'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否有必要的数据
        # TODO: 添加数据完整性检查
        
        # 更新状态为数据收集完成
        assessment.status = 'collecting'
        assessment.save()
        
        # 触发异步计分任务
        from .tasks import calculate_assessment_scores
        task = calculate_assessment_scores.delay(assessment.id)
        
        logger.info(f"评估 {assessment.id} 已提交，任务ID: {task.id}")
        
        return Response({
            'message': '评估已提交，正在计算中',
            'task_id': task.id,
            'assessment_id': assessment.id
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def scores(self, request, pk=None):
        """
        获取评估得分详情
        """
        try:
            assessment = self.get_queryset().get(pk=pk)
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        
        if assessment.status != 'completed':
            return Response({
                'status': assessment.status,
                'message': '评估尚未完成'
            })
        
        return Response({
            'status': 'completed',
            'scores': {
                'literacy_score': str(assessment.literacy_score),
                'institution_score': str(assessment.institution_score),
                'behavior_score': str(assessment.behavior_score),
                'asset_score': str(assessment.asset_score),
                'technology_score': str(assessment.technology_score),
                'total_score': str(assessment.total_score),
                'maturity_level': assessment.maturity_level,
                'maturity_level_display': assessment.get_maturity_level_display()
            },
            'completed_at': assessment.completed_at
        })

class AdminDashboardStatsView(APIView):
    """超级管理员概览统计接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin_user():
            return Response({'error': '权限不足'}, status=403)

        # 1. 顶部 KPI 统计
        kpi = {
            "provinces": School.objects.values('province').distinct().count(),
            "regions": School.objects.values('province', 'city', 'district').distinct().count(),
            "total_schools": School.objects.count(),
            "completed": Assessment.objects.filter(status='completed').count()
        }

        # 2. 中间表格数据：按省份和区县聚合统计学校数量
        # 逻辑：Group By province, district
        distribution = School.objects.values('province', 'district').annotate(
            school_count=Count('id')
        ).order_by('province')

        return Response({
            "success": True,
            "data": {
                "kpi": kpi,
                "distribution": distribution
            }
        })

class AdminAssessmentListView(APIView):
    """管理员专用评估列表（支持区域三级筛选）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin_user():
            return Response({'error': '权限不足'}, status=403)

        queryset = Assessment.objects.select_related('school').all().order_by('-created_at')

        # --- 过滤逻辑 ---
        school_name = request.query_params.get('school_name')
        province = request.query_params.get('province')
        city = request.query_params.get('city')
        district = request.query_params.get('district')
        status = request.query_params.get('status')
        school_type = request.query_params.get('school_type')

        if school_name:
            queryset = queryset.filter(school__name__icontains=school_name)
        if province:
            queryset = queryset.filter(school__province=province)
        if city:
            queryset = queryset.filter(school__city=city)
        if district:
            queryset = queryset.filter(school__district=district)
        if status:
            queryset = queryset.filter(status=status)
        if school_type:
            queryset = queryset.filter(school__school_type=school_type)

        # --- 分页处理 ---
        from django.core.paginator import Paginator
        page_num = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_num)

        # 序列化
        data = []
        for item in page_obj:
            data.append({
                "id": item.id,
                "school_name": item.school.name,
                "school_type_display": item.school.get_school_type_display(),
                "status": item.status,
                "status_display": item.get_status_display(),
                "total_score": float(item.total_score) if item.total_score else 0,
                "maturity_level_display": item.get_maturity_level_display(),
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return Response({
            "success": True,
            "count": paginator.count,
            "results": data
        })


class AdminProvinceSummaryView(APIView):
    """超级管理员专用：按省、市、区县聚合统计"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin_user():
            return Response({'success': False, 'message': '权限不足'}, status=403)

        # 只统计有省份的学校
        school_qs = School.objects.exclude(province__isnull=True).exclude(province='')

        provinces = (
            school_qs
            .values_list('province', flat=True)
            .distinct()
            .order_by('province')
        )

        result_data = []

        for province_name in provinces:
            # 按 city + district + region_id 分组
            district_rows = (
                school_qs
                .filter(province=province_name)
                .values('city', 'district', 'region_id')
                .annotate(school_count=Count('id'))
                .order_by('city', 'district')
            )

            city_map = {}
            total_schools_in_province = 0

            for row in district_rows:
                city_name = row.get('city') or '未知城市'
                district_name = row.get('district') or '未知区县'
                region_id = row.get('region_id')
                school_count = row.get('school_count') or 0

                if city_name not in city_map:
                    city_map[city_name] = {
                        'name': city_name,
                        'school_count': 0,
                        'total_schools': 0,
                        'districts': []
                    }

                city_map[city_name]['districts'].append({
                    'name': district_name,
                    'province': province_name,
                    'city': city_name,
                    'district': district_name,
                    'region_id': region_id,
                    'school_count': school_count,
                    'total_schools': school_count
                })

                city_map[city_name]['school_count'] += school_count
                city_map[city_name]['total_schools'] += school_count
                total_schools_in_province += school_count

            cities = list(city_map.values())

            result_data.append({
                'name': province_name,
                'total_schools': total_schools_in_province,
                'school_count': total_schools_in_province,
                'city_count': len(cities),
                'district_count': sum(len(city.get('districts', [])) for city in cities),
                'cities': cities
            })

        return Response({
            'success': True,
            'data': result_data
        })
