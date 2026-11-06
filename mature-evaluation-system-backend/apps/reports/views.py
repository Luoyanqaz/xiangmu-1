"""
报告相关API视图
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404
from apps.assessments.models import Assessment
from .tasks import generate_assessment_report
from .report_data_service import ReportDataService

logger = logging.getLogger(__name__)


def can_access_report(user, assessment):
    return (user.is_admin_user() or assessment.school.user_id == user.id or
            (user.role == 'region_admin' and assessment.school.region_id and
             assessment.school.region.region_admin_id == user.id))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request, assessment_id):
    """
    生成评估报告（触发异步任务）
    """
    try:
        # 获取评估记录
        assessment = Assessment.objects.get(id=assessment_id)
        
        # 权限检查：只有学校用户本人或管理员可以生成报告
        if not can_access_report(request.user, assessment):
            return Response({'error': '无权限生成此评估报告'}, status=status.HTTP_403_FORBIDDEN)
        
        # 注意：不检查status状态，因为用户填写完数据后可能还没有提交
        # 报告生成时会自动计算得分并更新状态为completed
        assessment.status = 'collecting'
        assessment.save()
        # 触发异步任务
        task = generate_assessment_report.delay(assessment_id)
        
        logger.info(f"报告生成任务已触发，任务ID: {task.id}")
        
        return Response({
            'message': '报告生成任务已启动，完成后将发送到注册邮箱',
            'task_id': task.id,
            'assessment_id': assessment_id
        }, status=status.HTTP_200_OK)
        
    except Assessment.DoesNotExist:
        return Response(
            {'error': '评估不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"触发报告生成任务失败: {str(e)}", exc_info=True)
        return Response(
            {'error': f'报告生成失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report_data(request, assessment_id):

    """
    获取报告数据（用于前端展示）
    如果得分还没计算，会先计算得分
    """
    try:
        # 获取评估记录
        assessment = Assessment.objects.get(id=assessment_id)
        
        # 权限检查
        if not can_access_report(request.user, assessment):
            return Response({'error': '无权限查看此评估报告'}, status=status.HTTP_403_FORBIDDEN)
        
        # 如果还没有计算得分，先计算得分
        scoring_service = None
        if assessment.total_score is None:
            from apps.assessments.scoring_service import ScoringService
            from django.utils import timezone
            
            logger.info(f"评估 {assessment_id} 尚未计算得分，开始计算...")
            scoring_service = ScoringService(assessment)
            scores = scoring_service.calculate_all_scores()
            
            # 保存得分到数据库
            assessment.literacy_score = scores['literacy_score']
            assessment.institution_score = scores['institution_score']
            assessment.behavior_score = scores['behavior_score']
            assessment.asset_score = scores['asset_score']
            assessment.technology_score = scores['technology_score']
            assessment.total_score = scores['total_score']
            assessment.maturity_level = scores['maturity_level']
            assessment.status = 'completed'
            assessment.completed_at = timezone.now()
            assessment.save()
            
            logger.info(f"评估 {assessment_id} 得分计算完成: 总分={scores['total_score']}")


        # 获取报告数据
        data_service = ReportDataService(assessment, scoring_service=scoring_service)
        report_data = data_service.get_all_report_data()
        print("111")

        # 获取AI建议（优先从数据库读取）
        if assessment.ai_suggestions:
            logger.info(f"使用已缓存的AI建议")
            report_data['suggestions'] = assessment.ai_suggestions
        else:
            logger.info(f"未找到缓存的AI建议，开始实时生成...")
            from .report_ai_service import ReportAIService
            ai_service = ReportAIService()
            suggestions = ai_service.generate_all_suggestions(report_data)
            report_data['suggestions'] = suggestions
            
            # 保存生成的建议到数据库
            assessment.ai_suggestions = suggestions
            assessment.save(update_fields=['ai_suggestions'])
            logger.info(f"AI建议已生成并保存")

        return Response(report_data, status=status.HTTP_200_OK)
        
    except Assessment.DoesNotExist:
        return Response(
            {'error': '评估不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"获取报告数据失败: {str(e)}", exc_info=True)
        return Response(
            {'error': f'获取报告数据失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request, assessment_id):
    """
    下载报告PDF
    """
    try:
        # 获取评估记录
        assessment = Assessment.objects.get(id=assessment_id)
        
        # 权限检查
        if not request.user.is_admin_user():
            if assessment.school.user != request.user:
                return Response(
                    {'error': '无权限下载此评估报告'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # 检查报告文件是否存在
        if not assessment.report_file:
            return Response(
                {'error': '报告文件不存在，请先生成报告'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 返回文件
        try:
            return FileResponse(
                assessment.report_file.open('rb'),
                as_attachment=True,
                filename=f'{assessment.school.name}_评估报告.pdf'
            )
        except FileNotFoundError:
            raise Http404('报告文件不存在')
        
    except Assessment.DoesNotExist:
        return Response(
            {'error': '评估不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"下载报告失败: {str(e)}", exc_info=True)
        return Response(
            {'error': f'下载报告失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

