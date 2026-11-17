"""
初始化系统配置
"""
from django.core.management.base import BaseCommand
from apps.admin_panel.models import SystemConfig
from apps.assessments.maturity import MATURITY_LEVELS
import json


class Command(BaseCommand):
    help = '初始化系统配置'
    
    def handle(self, *args, **options):
        self.stdout.write('开始初始化系统配置...')
        
        configs = [
            # 大模型配置
            {
                'config_key': 'llm_enabled',
                'config_value': 'false',
                'config_type': 'bool',
                'description': '是否启用大模型评分功能'
            },
            {
                'config_key': 'llm_api_key',
                'config_value': '',
                'config_type': 'string',
                'description': 'DeepSeek API密钥'
            },
            {
                'config_key': 'llm_api_endpoint',
                'config_value': 'https://api.deepseek.com',
                'config_type': 'string',
                'description': 'DeepSeek API端点'
            },
            {
                'config_key': 'llm_model_name',
                'config_value': 'deepseek-chat',
                'config_type': 'string',
                'description': 'DeepSeek模型名称'
            },
            # 成熟度等级划分
            {
                'config_key': 'maturity_levels',
                'config_value': json.dumps(MATURITY_LEVELS, ensure_ascii=False),
                'config_type': 'json',
                'description': '成熟度等级划分标准（分数阈值）'
            },
            # 评分提示词
            {
                'config_key': 'llm_prompt_management_doc',
                'config_value': '请从规范性、专业性、完整性、特色化四个维度评价这份数据管理制度文件的质量，满分10分。',
                'config_type': 'string',
                'description': '管理制度文件评分提示词'
            },
            {
                'config_key': 'llm_prompt_practice_doc',
                'config_value': '请从规范性、完整性、可操作性、实用性四个维度评价这份数据实践指导文件的质量，满分10分。',
                'config_type': 'string',
                'description': '实践指导文件评分提示词'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for config_data in configs:
            config, created = SystemConfig.objects.update_or_create(
                config_key=config_data['config_key'],
                defaults={
                    'config_value': config_data['config_value'],
                    'config_type': config_data['config_type'],
                    'description': config_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ 创建配置: {config.config_key}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'○ 更新配置: {config.config_key}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n初始化完成！创建 {created_count} 个配置，更新 {updated_count} 个配置。'
        ))
