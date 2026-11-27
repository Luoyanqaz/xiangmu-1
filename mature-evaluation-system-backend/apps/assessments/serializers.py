"""
评估系统序列化器
"""
from rest_framework import serializers
from .models import Assessment, InstitutionAssessment, BehaviorAssessment, AssetAssessment, TechnologyAssessment
from apps.assessments.services.module_status import compute_module_status
from apps.surveys.quality import collection


class AssessmentSerializer(serializers.ModelSerializer):
    """评估记录序列化器"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    maturity_level_display = serializers.CharField(source='get_maturity_level_display', read_only=True)

    # 进度百分比字段
    progress_rate = serializers.SerializerMethodField()
    # 模块详细状态字段
    module_status = serializers.SerializerMethodField()
    survey_collection = serializers.SerializerMethodField()

    def get_survey_collection(self, obj):
        return collection(obj)

    def get_module_status(self, obj):
        # 假设 compute_module_status 返回类似 {'literacy': True, 'institution': False, ...}
        return compute_module_status(obj)

    def get_progress_rate(self, obj):
        """
        根据模块完成情况计算总进度 (每个维度占 20%)
        """
        if obj.status == 'completed':
            return 100

        status_dict = self.get_module_status(obj)
        # 计算 True 的个数
        done_count = sum(1 for status in status_dict.values() if status is True)

        return done_count * 20

    class Meta:
        model = Assessment
        fields = [
            'id', 'school', 'school_name', 'status', 'status_display',
            'literacy_score', 'institution_score', 'behavior_score',
            'asset_score', 'technology_score', 'total_score',
            'maturity_level', 'maturity_level_display', 'report_file',
            'started_at', 'completed_at', 'created_at', 'updated_at',
            'module_status', 'progress_rate', 'survey_collection', 'check_survey_quality'
        ]
        read_only_fields = [
            'school', 'literacy_score', 'institution_score', 'behavior_score',
            'asset_score', 'technology_score', 'total_score', 'maturity_level',
            'report_file', 'started_at', 'completed_at'
        ]


class InstitutionAssessmentSerializer(serializers.ModelSerializer):
    """数据制度评估序列化器"""
    
    class Meta:
        model = InstitutionAssessment
        fields = [
            'id', 'assessment',

            # 数据组织机构
            'has_leadership_group',
            'leadership_group_type',
            'meeting_activity_count',

            # 数据人员配备
            'has_data_staff',
            'fulltime_staff_count',
            'parttime_staff_count',
            'has_clear_responsibilities',

            # 数据培训
            'has_training',
            'training_count',
            'national_cert_count',
            'provincial_cert_count',
            'city_cert_count',

            # 数据管理文件
            'has_management_doc',
            'management_doc_status',
            'management_doc_count',
            'management_doc_files',
            'management_doc_analysis',

            # 数据实践指导文件
            'has_practice_doc',
            'practice_doc_status',
            'practice_doc_count',
            'practice_doc_files',
            'practice_doc_analysis',

            # 其他
            'auto_crawled_data',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['assessment', 'auto_crawled_data', 'management_doc_analysis', 'practice_doc_analysis', 'created_at', 'updated_at']


class BehaviorAssessmentSerializer(serializers.ModelSerializer):
    """数据行为评估序列化器"""
    
    class Meta:
        model = BehaviorAssessment
        fields = [
            'id', 'assessment',

            # 数据行为监测
            'teacher_login_freq', 'student_login_freq', 'manager_login_freq',
            'teacher_device_use_freq', 'teacher_platform_use_freq',
            'teacher_data_behavior_items', 'teacher_data_behavior_other',
            'student_device_provision', 'student_account_status',
            'student_data_behavior_items', 'student_data_behavior_other',
            'visit_count',

            # 数据应用成效
            'published_paper_count', 'published_book_count',
            'case_national_count', 'case_provincial_count', 'case_city_count',
            'award_national_count', 'award_provincial_count', 'award_city_count',
            'media_national_count', 'media_provincial_count', 'media_city_count',
            'conference_national_count', 'conference_provincial_count', 'conference_city_count',
            'public_account_post_count',

            # 其他
            'auto_crawled_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['assessment', 'auto_crawled_data', 'created_at', 'updated_at']


class AssetAssessmentSerializer(serializers.ModelSerializer):
    """数据资产评估序列化器"""
    
    class Meta:
        model = AssetAssessment
        fields = '__all__'
        read_only_fields = ['assessment', 'auto_crawled_data', 'created_at', 'updated_at']


class TechnologyAssessmentSerializer(serializers.ModelSerializer):
    """数据技术评估序列化器"""
    
    class Meta:
        model = TechnologyAssessment
        fields = '__all__'
        read_only_fields = ['assessment', 'auto_crawled_data', 'created_at', 'updated_at']


class RegionAssessmentListSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name')
    school_id = serializers.IntegerField(source='school.id')

    class Meta:
        model = Assessment
        fields = [
            'id',
            'school_id',
            'school_name',
            'status',
            'total_score',
            'maturity_level',
            'completed_at',
        ]
