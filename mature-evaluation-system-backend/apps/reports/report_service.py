"""
报告生成核心服务
负责协调整个报告生成流程
"""
import logging
from typing import Dict, Any
from django.utils import timezone
from apps.assessments.models import Assessment
from apps.assessments.scoring_service import ScoringService
from .report_data_service import ReportDataService
from .report_ai_service import ReportAIService

logger = logging.getLogger(__name__)


class ReportService:
    """报告生成核心服务"""

    def __init__(self, assessment: Assessment):
        self.assessment = assessment
        self.scoring_service = ScoringService(assessment)
        self.data_service = ReportDataService(assessment)
        self.ai_service = ReportAIService()
    
    def generate_report(self) -> Dict[str, Any]:
        """
        生成完整的评估报告数据（供前端使用）
        :return: 报告数据
        """
        logger.info(f"开始生成评估 {self.assessment.id} 的报告数据")

        try:
            # 第一步：计算得分（如果还没有计算）
            if self.assessment.total_score is None:
                logger.info("步骤1: 计算评估得分")
                scores = self.scoring_service.calculate_all_scores()

                # 保存得分到数据库
                self.assessment.literacy_score = scores['literacy_score']
                self.assessment.institution_score = scores['institution_score']
                self.assessment.behavior_score = scores['behavior_score']
                self.assessment.asset_score = scores['asset_score']
                self.assessment.technology_score = scores['technology_score']
                self.assessment.total_score = scores['total_score']
                self.assessment.maturity_level = scores['maturity_level']
                self.assessment.completed_at = timezone.now()
                self.assessment.save()

                logger.info(f"得分计算完成: 总分={scores['total_score']}, 等级={scores['maturity_level']}")

            # 第二步：聚合报告数据
            logger.info("步骤2: 聚合报告数据")
            report_data = self.data_service.get_all_report_data()

            # 第三步：生成AI建议
            logger.info("步骤3: 生成AI建议")
            if self.assessment.ai_suggestions:
                logger.info("使用已缓存的AI建议")
                suggestions = self.assessment.ai_suggestions
            else:
                logger.info("未找到缓存建议，开始实时生成")
                suggestions = self.ai_service.generate_all_suggestions(report_data)
                self.assessment.ai_suggestions = suggestions
                self.assessment.save(update_fields=['ai_suggestions'])
            
            report_data['suggestions'] = suggestions

            logger.info(f"报告数据生成完成")

            return {
                'success': True,
                'assessment_id': self.assessment.id,
                'report_data': report_data,
                'message': '报告数据生成成功'
            }

        except Exception as e:
            logger.error(f"报告数据生成失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'assessment_id': self.assessment.id,
                'error': str(e),
                'message': '报告数据生成失败'
            }
    
    def send_report_email(self) -> bool:
        """
        发送报告邮件（暂时保留接口，实际功能待实现）
        :return: 是否发送成功
        """
        logger.warning("邮件发送功能暂未实现")
        return False

