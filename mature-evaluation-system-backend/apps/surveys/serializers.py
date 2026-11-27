"""
问卷系统序列化器
"""
from rest_framework import serializers
from .models import SurveyTemplate, SurveyQuestion, SurveyInstance, SurveyResponse


class SurveyQuestionSerializer(serializers.ModelSerializer):
    """问卷题目序列化器"""
    
    class Meta:
        model = SurveyQuestion
        fields = ['id', 'question_text', 'question_type', 'options', 'order', 'is_required']


class SurveyTemplateSerializer(serializers.ModelSerializer):
    """问卷模板序列化器"""
    questions = SurveyQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = SurveyTemplate
        fields = ['id', 'survey_type', 'title', 'description', 'is_active', 'questions']


class SurveyInstanceSerializer(serializers.ModelSerializer):
    """问卷实例序列化器"""
    template_info = SurveyTemplateSerializer(source='template', read_only=True)
    share_url = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    valid_count = serializers.SerializerMethodField()
    check_survey_quality = serializers.BooleanField(source='assessment.check_survey_quality', read_only=True)

    def get_valid_count(self, obj):
        return obj.responses.filter(is_valid=True).count() if obj.assessment.check_survey_quality else None
    
    class Meta:
        model = SurveyInstance
        fields = [
            'id', 'assessment', 'template', 'template_info', 'uuid', 
            'target_count', 'collected_count', 'is_active', 
            'created_at', 'expired_at', 'share_url', 'completion_rate', 'valid_count', 'check_survey_quality'
        ]
        read_only_fields = ['uuid', 'collected_count']
    
    def get_share_url(self, obj):
        """获取分享链接"""
        return f"/survey/{obj.template.survey_type}/{obj.uuid}"
    
    def get_completion_rate(self, obj):
        """获取完成率"""
        if obj.target_count == 0:
            return 0
        return round(obj.collected_count / obj.target_count * 100, 2)


class SurveyResponseSerializer(serializers.ModelSerializer):
    """问卷回答序列化器"""
    
    class Meta:
        model = SurveyResponse
        fields = ['id', 'instance', 'answers', 'ip_address', 'submitted_at']
        read_only_fields = ['ip_address', 'submitted_at']
    
    def validate_answers(self, value):
        """验证答案格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("答案必须是字典格式")
        return value


class SurveySubmitSerializer(serializers.Serializer):
    """问卷提交序列化器（用于公开接口）"""
    answers = serializers.JSONField()
    attempt = serializers.CharField(required=False)
    elapsed_ms = serializers.IntegerField(required=False, min_value=0)
    
    def validate_answers(self, value):
        """验证答案格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("答案必须是字典格式")
        return value
