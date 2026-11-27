"""
问卷相关模型
"""
import uuid
from django.db import models


class SurveyTemplate(models.Model):
    """问卷模板模型"""
    
    SURVEY_TYPE_CHOICES = [
        ('teacher', '教师问卷'),
        ('student', '学生问卷'),
    ]
    
    survey_type = models.CharField('问卷类型', max_length=20, choices=SURVEY_TYPE_CHOICES, unique=True)
    title = models.CharField('问卷标题', max_length=200)
    description = models.TextField('问卷说明')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'survey_template'
        verbose_name = '问卷模板'
        verbose_name_plural = '问卷模板'
    
    def __str__(self):
        return self.title


class SurveyQuestion(models.Model):
    """问卷题目模型"""
    
    QUESTION_TYPE_CHOICES = [
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('scale', '量表题'),
    ]
    
    template = models.ForeignKey(
        SurveyTemplate,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='问卷模板'
    )
    question_text = models.TextField('题目内容')
    question_type = models.CharField('题目类型', max_length=20, choices=QUESTION_TYPE_CHOICES)
    options = models.JSONField('选项内容')
    score_rule = models.JSONField('计分规则', null=True, blank=True)
    order = models.IntegerField('题目顺序', default=0)
    is_required = models.BooleanField('是否必填', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'survey_question'
        verbose_name = '问卷题目'
        verbose_name_plural = '问卷题目'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.template.title} - Q{self.order}"


class SurveyInstance(models.Model):
    """问卷实例模型"""
    
    assessment = models.ForeignKey(
        'assessments.Assessment',
        on_delete=models.CASCADE,
        related_name='survey_instances',
        verbose_name='评估记录'
    )
    template = models.ForeignKey(
        SurveyTemplate,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name='问卷模板'
    )
    uuid = models.UUIDField('唯一标识', default=uuid.uuid4, unique=True, editable=False)
    target_count = models.IntegerField('目标收集数量', default=0)
    collected_count = models.IntegerField('已收集数量', default=0)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    expired_at = models.DateTimeField('过期时间', null=True, blank=True)
    
    class Meta:
        db_table = 'survey_instance'
        verbose_name = '问卷实例'
        verbose_name_plural = '问卷实例'
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['assessment']),
        ]
    
    def __str__(self):
        return f"{self.assessment.school.name} - {self.template.title}"
    
    def get_share_url(self):
        """获取分享链接"""
        return f"/survey/{self.template.survey_type}/{self.uuid}"


class SurveyResponse(models.Model):
    """问卷回答模型"""
    
    instance = models.ForeignKey(
        SurveyInstance,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='问卷实例'
    )
    answers = models.JSONField('答案内容')
    is_valid = models.BooleanField('有效性', null=True, default=None)
    attempt_id = models.UUIDField('作答编号', null=True, unique=True, editable=False)
    quality_details = models.JSONField('题数、用时及无效原因', default=dict, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    submitted_at = models.DateTimeField('提交时间', auto_now_add=True)
    
    class Meta:
        db_table = 'survey_response'
        verbose_name = '问卷回答'
        verbose_name_plural = '问卷回答'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.instance} - {self.submitted_at}"
