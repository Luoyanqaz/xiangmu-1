"""
报告数据聚合服务
负责从数据库查询和聚合报告所需的所有数据
"""
import logging
from decimal import Decimal
from typing import Dict, List, Any
from django.db.models import Avg, Count, Case, When, F, FloatField
from apps.assessments.models import Assessment, InstitutionAssessment, BehaviorAssessment, AssetAssessment, TechnologyAssessment
from apps.surveys.models import SurveyResponse, SurveyInstance
from apps.assessments import scoring_config as config
from apps.assessments.scoring_service import ScoringService
from .statistics import school_rankings, score_details

logger = logging.getLogger(__name__)


class ReportDataService:
    """报告数据聚合服务"""

    def __init__(self, assessment: Assessment, scoring_service: ScoringService = None):
        self.assessment = assessment
        self.school = assessment.school
        if scoring_service:
            self.scoring_service = scoring_service
        else:
            self.scoring_service = ScoringService(assessment)

    def get_average_scores(self) -> Dict[str, float]:
        """获取全库平均分（增加脏数据防御，确保返回五分制）"""
        completed = Assessment.objects.filter(status='completed')
        if not completed.exists():
            return {k: 3.0 for k in ['literacy', 'institution', 'behavior', 'asset', 'technology']}

        # 定义一个内部处理函数，防止 None 且强制限制在 0-5 之间
        def normalize_aggregate(field_name):
            # 逻辑：如果分数 > 5，则取其 1/20，否则取原值；如果为 None 则取 3.0
            return Avg(
                Case(
                    When(**{f"{field_name}__gt": 5.0}, then=F(field_name) / 20.0),
                    default=F(field_name),
                    output_field=FloatField()
                )
            )

        aggs = completed.aggregate(
            l=normalize_aggregate('literacy_score'),
            i=normalize_aggregate('institution_score'),
            b=normalize_aggregate('behavior_score'),
            a=normalize_aggregate('asset_score'),
            t=normalize_aggregate('technology_score')
        )

        # 格式化返回，并增加兜底值 3.0
        return {
            'literacy': round(float(aggs['l'] or 3.0), 2),
            'institution': round(float(aggs['i'] or 3.0), 2),
            'behavior': round(float(aggs['b'] or 3.0), 2),
            'asset': round(float(aggs['a'] or 3.0), 2),
            'technology': round(float(aggs['t'] or 3.0), 2),
        }

    def get_all_report_data(self) -> Dict[str, Any]:
        """
        获取报告所需的所有数据
        :return: 包含所有报告数据的字典
        """
        logger.info(f"开始聚合评估 {self.assessment.id} 的报告数据")
        
        data = {
            # 基本信息
            'school_name': self.school.name,
            'report_date': self.assessment.completed_at or self.assessment.updated_at,
            
            # 总体得分（5分制和百分制都提供）
            'total_score': float(self.assessment.total_score or 0),  # 5分制
            'total_score_percent': float(self.assessment.total_score or 0) * 20,  # 百分制
            'maturity_level': self.get_maturity_level_display(),
            
            # 五个维度得分
            'dimension_scores': self.get_dimension_scores(),
            
            # 平均得分
            'average_scores': self.get_average_scores(),
            'rankings': school_rankings(self.assessment),
            
            # 二级指标得分
            'secondary_scores': self.get_secondary_scores(),
            
            # 观测点得分
            'observation_scores': self.get_observation_scores(),
            
            # 问卷参评人数
            'participant_counts': self.get_participant_counts(),
            
            # 数据制度详细数据
            'institution_details': self.get_institution_details(),
            
            # 数据行为详细数据
            'behavior_details': self.get_behavior_details(),
            
            # 数据资产详细数据
            'asset_details': self.get_asset_details(),
            
            # 数据技术详细数据
            'technology_details': self.get_technology_details(),
        }
        
        logger.info(f"报告数据聚合完成")
        return data
    
    def get_maturity_level_display(self) -> str:
        """获取成熟度等级的中文显示"""
        level_map = {
            'initial': '初始级',
            'growing': '成长级',
            'mature': '成熟级',
            'leading': '创新级',
        }
        return level_map.get(self.assessment.maturity_level, '未知')
    
    def get_dimension_scores(self) -> Dict[str, float]:
        """
        获取五个维度的得分（百分制，0-100分）
        数据库中存储的是5分制得分，转换为百分制：score * 20
        """

        return {
            'literacy': self.assessment.literacy_score,
            'institution': self.assessment.institution_score,
            'behavior': self.assessment.behavior_score,
            'asset': self.assessment.asset_score,
            'technology': self.assessment.technology_score,
        }
    
    def get_secondary_scores(self) -> Dict[str, float]:
        """
        获取二级指标得分（百分制，5分制×20）
        """
        return self._get_score_details().get('secondary_scores', {})

    def get_observation_scores(self) -> Dict[str, float]:
        """
        获取观测点得分（百分制，5分制×20）
        """
        return self._get_score_details().get('observation_scores', {})

    def _get_score_details(self):
        if not hasattr(self, '_details'):
            self._details = score_details(self.assessment)
        return self._details
    
    def get_participant_counts(self) -> Dict[str, int]:
        """获取各类问卷的参评人数"""
        instances = SurveyInstance.objects.filter(assessment=self.assessment)
        
        counts = {}
        for instance in instances:
            survey_type = instance.template.survey_type
            count = SurveyResponse.objects.filter(instance=instance).count()
            counts[survey_type] = count
        
        return {
            'teacher': counts.get('teacher', 0),
            'student': counts.get('student', 0),
            'manager': counts.get('manager', 0),
        }
    
    def get_institution_details(self) -> Dict[str, Any]:
        """获取数据制度的详细数据"""
        try:
            institution = InstitutionAssessment.objects.get(assessment=self.assessment)
            return {
                # 数据组织机构
                'has_leadership_group': institution.has_leadership_group,
                'meeting_activity_count': institution.meeting_activity_count,
                # 数据人员配备
                'has_data_staff': institution.has_data_staff,
                'fulltime_staff_count': institution.fulltime_staff_count,
                'parttime_staff_count': institution.parttime_staff_count,
                'has_clear_responsibilities': institution.has_clear_responsibilities,
                # 数据培训
                'has_training': institution.has_training,
                'training_count': institution.training_count,
                'national_cert_count': institution.national_cert_count,
                'provincial_cert_count': institution.provincial_cert_count,
                'city_cert_count': institution.city_cert_count,
                # 数据管理文件
                'has_management_doc': institution.has_management_doc,
                'management_doc_count': institution.management_doc_count,
                'management_doc_files': institution.management_doc_files,
                'management_doc_analysis': getattr(institution, 'management_doc_analysis', ''),
                # 数据实践指导文件
                'has_practice_doc': institution.has_practice_doc,
                'practice_doc_count': institution.practice_doc_count,
                'practice_doc_files': institution.practice_doc_files,
                'practice_doc_analysis': getattr(institution, 'practice_doc_analysis', ''),
            }
        except InstitutionAssessment.DoesNotExist:
            return {}

    def get_behavior_details(self) -> Dict[str, Any]:
        """获取数据行为的详细数据"""
        try:
            behavior = BehaviorAssessment.objects.get(assessment=self.assessment)
            return {
                # 数据行为监测
                'teacher_login_freq': behavior.teacher_login_freq,
                'student_login_freq': behavior.student_login_freq,
                'manager_login_freq': behavior.manager_login_freq,
                'visit_count': behavior.visit_count,
                # 数据应用成效
                'published_paper_count': behavior.published_paper_count,
                'published_book_count': behavior.published_book_count,
                'case_national_count': behavior.case_national_count,
                'case_provincial_count': behavior.case_provincial_count,
                'case_city_count': behavior.case_city_count,
                'award_national_count': behavior.award_national_count,
                'award_provincial_count': behavior.award_provincial_count,
                'award_city_count': behavior.award_city_count,
                'media_national_count': behavior.media_national_count,
                'media_provincial_count': behavior.media_provincial_count,
                'media_city_count': behavior.media_city_count,
                'conference_national_count': behavior.conference_national_count,
                'conference_provincial_count': behavior.conference_provincial_count,
                'conference_city_count': behavior.conference_city_count,
            }
        except BehaviorAssessment.DoesNotExist:
            return {}

    def get_asset_details(self) -> Dict[str, Any]:
        """获取数据资产的详细数据"""
        try:
            asset = AssetAssessment.objects.get(assessment=self.assessment)
            management = float(asset.management_data_volume or 0)
            resource = float(asset.resource_data_volume or 0)
            service = float(asset.service_data_volume or 0)
            other = float(asset.other_data_volume or 0)
            student_count = getattr(self.school, 'student_count', 0) or 0
            staff_count = getattr(self.school, 'teacher_count', 0) or 0  #
            return {
                'management_data_volume': management,
                'resource_data_volume': resource,
                'service_data_volume': service,
                'other_data_volume': other,
                'total_data_volume': management + resource + service + other,
                'student_count': student_count,
                'staff_count': staff_count,
            }
        except AssetAssessment.DoesNotExist:
            return {}

    def get_technology_details(self) -> Dict[str, Any]:
        """获取数据技术的详细数据"""
        try:
            technology = TechnologyAssessment.objects.get(assessment=self.assessment)
            return {
                # 数据基础设施
                'has_independent_data_center':technology.has_data_platform,
                'data_center_standard': technology.data_center_standard,
                'data_center_standard_display': technology.get_data_center_standard_display() if technology.data_center_standard else '',
                'student_device_ratio': technology.student_device_ratio,
                'student_device_ratio_display': technology.get_student_device_ratio_display() if technology.student_device_ratio else '',
                'teacher_device_ratio': technology.teacher_device_ratio,
                'teacher_device_ratio_display': technology.get_teacher_device_ratio_display() if technology.teacher_device_ratio else '',
                # 数据安全水平
                'security_certified_count': technology.security_certified_count,
                'security_certified_ratio': technology.security_certified_ratio,
                'security_certified_ratio_display': technology.get_security_certified_ratio_display() if technology.security_certified_ratio else '',
                'has_security_incident': technology.has_security_incident,
            }
        except TechnologyAssessment.DoesNotExist:
            return {}

