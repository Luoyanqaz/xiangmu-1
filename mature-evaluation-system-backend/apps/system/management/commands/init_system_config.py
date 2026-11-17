"""
初始化系统配置
"""
from django.core.management.base import BaseCommand
from apps.system.models import SystemConfig
import json
from apps.assessments.maturity import MATURITY_LEVELS


class Command(BaseCommand):
    help = '初始化系统配置'
    
    def handle(self, *args, **options):
        self.stdout.write('开始初始化系统配置...')
        
        # DeepSeek API配置
        configs = [
            {
                'key': 'deepseek_api_key',
                'value': '',
                'type': 'string',
                'description': 'DeepSeek API密钥'
            },
            {
                'key': 'deepseek_api_endpoint',
                'value': 'https://api.deepseek.com/v1/chat/completions',
                'type': 'string',
                'description': 'DeepSeek API端点'
            },
            {
                'key': 'deepseek_model_name',
                'value': 'deepseek-chat',
                'type': 'string',
                'description': 'DeepSeek模型名称'
            },
            {
                'key': 'llm_enabled',
                'value': 'false',
                'type': 'bool',
                'description': '是否启用大模型评分功能'
            },
            
            # 计分规则权重配置
            {
                'key': 'dimension_weights',
                'value': json.dumps({
                    'literacy': 1.0,
                    'institution': 1.0,
                    'behavior': 1.0,
                    'asset': 1.0,
                    'technology': 1.0
                }),
                'type': 'json',
                'description': '五个维度的权重配置'
            },
            
            # 成熟度等级划分
            {
                'key': 'maturity_levels',
                'value': json.dumps(MATURITY_LEVELS, ensure_ascii=False),
                'type': 'json',
                'description': '成熟度等级划分标准'
            },
            
            # 大模型评分提示词
            {
                'key': 'llm_prompt_management_doc',
                'value': '请从规范性、专业性、完整性、特色化四个维度评价这份数据管理制度文件的质量，满分10分。',
                'type': 'string',
                'description': '数据管理制度文件评分提示词'
            },
            {
                'key': 'llm_prompt_practice_doc',
                'value': '请从规范性、完整性、可操作性、实用性四个维度评价这份数据实践指导文件的质量，满分10分。',
                'type': 'string',
                'description': '数据实践指导文件评分提示词'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for config_data in configs:
            config, created = SystemConfig.objects.update_or_create(
                config_key=config_data['key'],
                defaults={
                    'config_value': config_data['value'],
                    'config_type': config_data['type'],
                    'description': config_data['description']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ 创建配置: {config_data["key"]}'))
            else:
                updated_count += 1
                self.stdout.write(f'  更新配置: {config_data["key"]}')
        
        self.stdout.write(self.style.SUCCESS(f'\n初始化完成！创建 {created_count} 个配置，更新 {updated_count} 个配置。'))
