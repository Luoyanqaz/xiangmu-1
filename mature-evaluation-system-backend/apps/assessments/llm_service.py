"""
大模型服务
用于调用DeepSeek API进行文件质量评分
"""
import logging
from typing import Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMService:
    """大模型服务类"""
    
    def __init__(self):
        """初始化大模型服务"""
        # 从配置中获取API信息（优先从数据库读取，其次从settings读取）
        from apps.admin_panel.models import SystemConfig
        
        # 获取API密钥（优先级：数据库 > settings）
        db_api_key = SystemConfig.get_config('llm_api_key', None)
        if db_api_key:
            self.api_key = db_api_key
        else:
            self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        
        # 获取API端点（OpenAI SDK需要的是base_url，不包含具体的endpoint路径）
        db_endpoint = SystemConfig.get_config('llm_api_endpoint', None)
        if db_endpoint:
            self.api_endpoint = db_endpoint
        else:
            self.api_endpoint = getattr(settings, 'DEEPSEEK_API_ENDPOINT', 'https://api.deepseek.com')
        
        # 获取模型名称
        db_model = SystemConfig.get_config('llm_model_name', None)
        if db_model:
            self.model_name = db_model
        else:
            self.model_name = getattr(settings, 'DEEPSEEK_MODEL_NAME', 'deepseek-chat')
        
        logger.info(f"LLM服务初始化: endpoint={self.api_endpoint}, model={self.model_name}, api_key={'已配置' if self.api_key else '未配置'}")
    
    def score_management_document(self, document_content: str, max_score: float = 10.0) -> Dict:
        """
        评分数据管理制度类文件（B31）
        从规范性、专业性、完整性、特色化四个维度分析

        :param document_content: 文件内容
        :param max_score: 满分（默认10分，B31为20分）
        :return: 包含得分和分析的字典
        """
        prompt = f"""你是一个专业的教育数据管理文件评审专家。请根据以下标准评价这份数据管理制度类文件的质量，满分{max_score}分。

评分维度（每个维度0-5分，共4个维度）：
1. 规范性：文件结构、语言是否符合行业标准与教育规范，内容是否符合相关法律法规和政策。
2. 专业性：是否使用准确的专业术语和技术方法，能否有效指导学校数据管理工作。
3. 完整性：是否涵盖数据采集、存储、管理、保护、使用、共享、销毁等完整环节。
4. 特色化：是否结合学校实际情况，具有校本特色和创新性，能否解决学校具体问题。

文件内容：
{document_content}

请给出评分和简要分析。注意：请使用纯文本格式回复，不要使用任何markdown语法（如**加粗**、#标题、-列表等）。

输出格式：
规范性：X分
专业性：X分
完整性：X分
特色化：X分
总评分：X分
分析：（用一段话简要说明文件的优点和不足，50-100字）
"""

        try:
            result = self._call_api(prompt)
            score = self._extract_score(result, max_score)
            return {
                'score': score,
                'analysis': result,
                'success': True
            }
        except Exception as e:
            logger.error(f"大模型评分失败: {str(e)}")
            return {
                'score': max_score / 2.0,  # 失败时给默认分数（满分的一半）
                'analysis': f'评分失败: {str(e)}',
                'success': False
            }

    def score_practice_document(self, document_content: str, max_score: float = 10.0) -> Dict:
        """
        评分数据实践指导类文件（B32）
        从规范性、完整性、可操作性、实用性四个维度分析

        :param document_content: 文件内容
        :param max_score: 满分（默认10分，B32为20分）
        :return: 包含得分和分析的字典
        """
        prompt = f"""你是一个专业的教育数据管理文件评审专家。请根据以下标准评价这份数据实践指导类文件的质量，满分{max_score}分。

评分维度（每个维度0-5分，共4个维度）：
1. 规范性：文件结构、语言是否符合行业标准与教育规范，术语使用是否准确。
2. 完整性：是否涵盖数据采集、存储、管理、共享、使用等完整环节，并提供完整的操作步骤。
3. 可操作性：是否提供具体、清晰、易执行的实施步骤和操作指南。
4. 实用性：是否能解决实际工作中的具体问题，指导效果是否显著。

文件内容：
{document_content}

请给出评分和简要分析。注意：请使用纯文本格式回复，不要使用任何markdown语法（如**加粗**、#标题、-列表等）。

输出格式：
规范性：X分
完整性：X分
可操作性：X分
实用性：X分
总评分：X分
分析：（用一段话简要说明文件的优点和不足，50-100字）
"""

        try:
            result = self._call_api(prompt)
            score = self._extract_score(result, max_score)
            return {
                'score': score,
                'analysis': result,
                'success': True
            }
        except Exception as e:
            logger.error(f"大模型评分失败: {str(e)}")
            return {
                'score': max_score / 2.0,  # 失败时给默认分数（满分的一半）
                'analysis': f'评分失败: {str(e)}',
                'success': False
            }
    
    def _call_api(self, prompt: str, max_tokens: int = 500) -> str:
        """
        调用DeepSeek API（使用OpenAI SDK）
        
        :param prompt: 提示词
        :return: API返回的文本
        """
        if not self.api_key:
            raise ValueError("未配置DeepSeek API密钥")
        
        try:
            from openai import OpenAI
            import httpx
        except ImportError:
            raise ImportError("请先安装依赖: pip install openai httpx")
        
        logger.info(f"调用DeepSeek API: {self.api_endpoint}")
        
        # 创建httpx客户端（兼容旧版本）
        try:
            http_client = httpx.Client(timeout=30.0)
        except TypeError:
            # 如果httpx版本太旧，不传参数
            http_client = None
        
        # 创建OpenAI客户端，指向DeepSeek API
        try:
            if http_client:
                client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_endpoint,
                    http_client=http_client
                )
            else:
                client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_endpoint
                )
        except Exception as e:
            logger.error(f"创建OpenAI客户端失败: {str(e)}")
            # 尝试不使用http_client
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_endpoint
            )
        
        # 调用API
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的教育数据管理文件评审专家。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            stream=False
        )
        
        # 提取返回的文本
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            raise ValueError("API返回格式错误")
    
    def _extract_score(self, text: str, max_score: float = 10.0) -> float:
        """
        从返回文本中提取分数

        :param text: API返回的文本
        :param max_score: 满分（用于限制分数范围）
        :return: 提取的分数
        """
        import re

        # 尝试匹配不同格式的分数
        patterns = [
            r'总评分[：:]\s*(\d+(?:\.\d+)?)\s*分',  # 优先匹配"总评分"
            r'总分[：:]\s*(\d+(?:\.\d+)?)\s*分',
            r'评分[：:]\s*(\d+(?:\.\d+)?)\s*分',
            r'得分[：:]\s*(\d+(?:\.\d+)?)\s*分',
            r'(\d+(?:\.\d+)?)\s*分',  # 最后尝试匹配任意数字+分
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                score = float(match.group(1))
                # 确保分数在0-max_score之间
                return max(0.0, min(max_score, score))

        # 如果无法提取，返回默认分数（满分的一半）
        logger.warning(f"无法从文本中提取分数: {text}")
        return max_score / 2.0
    
    def test_connection(self) -> Dict:
        """
        测试API连接
        
        :return: 测试结果
        """
        try:
            result = self._call_api("你好，请简单回复'连接成功'")
            return {
                'success': True,
                'message': '连接成功',
                'response': result
            }
        except Exception as e:
            logger.error(f"API连接测试失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'连接失败: {str(e)}'
            }
