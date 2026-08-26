"""
报告AI建议生成服务
负责调用DeepSeek生成各个维度的评估建议
"""
import logging
from typing import Dict, List, Any
from apps.assessments.llm_service import LLMService

logger = logging.getLogger(__name__)


class ReportAIService:
    """报告AI建议生成服务"""

    SUGGESTION_SCHEMA_VERSION = 3
    
    def __init__(self, initialize_llm: bool = True):
        self.llm_service = LLMService() if initialize_llm else None
    
    def generate_all_suggestions(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        生成所有维度的AI建议
        :param report_data: 报告数据
        :return: 包含所有建议的字典
        """
        logger.info("开始生成AI评估建议")
        
        suggestions = {}
        
        # 1. 生成整体评估建议
        suggestions['overall'] = self.generate_overall_suggestion(report_data)
        
        # 2. 生成数据素养建议
        suggestions['literacy'] = self.generate_literacy_suggestion(report_data)
        
        # 3. 生成数据制度建议
        suggestions['institution'] = self.generate_institution_suggestion(report_data)
        
        # 4. 生成数据行为建议
        suggestions['behavior'] = self.generate_behavior_suggestion(report_data)
        
        # 5. 生成数据资产建议
        suggestions['asset'] = self.generate_asset_suggestion(report_data)
        
        # 6. 生成数据技术建议
        suggestions['technology'] = self.generate_technology_suggestion(report_data)

        suggestions['_schema_version'] = self.SUGGESTION_SCHEMA_VERSION
        
        logger.info("AI评估建议生成完成")
        return suggestions

    def generate_overall_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成整体评估建议"""
        total_score = report_data['total_score']
        maturity_level = report_data['maturity_level']
        sec = report_data.get('secondary_scores', {})

        # A 数据素养：新版只包含教师和学生
        a1 = sec.get('A1', 0)  # 教师数据素养
        a2 = sec.get('A2', 0)  # 学生数据素养

        # B 数据制度
        b1 = sec.get('B1', 0)
        b2 = sec.get('B2', 0)
        b3 = sec.get('B3', 0)

        # C 数据行为
        c1 = sec.get('C1', 0)
        c2 = sec.get('C2', 0)

        # D 数据资产
        d1 = sec.get('D1', 0)
        d2 = sec.get('D2', 0)

        # E 数据技术
        e1 = sec.get('E1', 0)
        e2 = sec.get('E2', 0)

        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议。

    学校所获的分值：
    该校的整体数据文化得分为{total_score:.2f}分，所处等级为{maturity_level}。

    每个维度的得分是：
    数据素养：教师数据素养（{a1:.2f}分）、学生数据素养（{a2:.2f}分）
    数据制度：数据组织机构（{b1:.2f}分）、数据人员配备（{b2:.2f}分）、数据管理文件（{b3:.2f}分）
    数据行为：数据行为监测（{c1:.2f}分）、数据应用成效（{c2:.2f}分）
    数据资产：数据资产意识（{d1:.2f}分）、数据资产积累（{d2:.2f}分）
    数据技术：数据基础设施（{e1:.2f}分）、数据安全水平（{e2:.2f}分）

    你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
    1. 评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
    2. 表现较为优秀[3.0~4.0]和表现非常优秀[4.0~5.0]的分数段，不需要回复“应……”。只呈现“表现……”。分数区间判断必须准确。
    3. 必须按照下面格式回复，不呈现分值，字数控制在130字左右。

    该校数据文化处于……（等级），整体……（正面评价），但部分维度的表现……（提到一些不足）。（断行）

    其中，数据素养在教师数据素养表现……；在学生数据素养表现……；应……（给出符合中小学校的可操作建议）。（断行）

    数据制度在数据组织机构表现……；在数据人员配备表现……；在数据管理文件表现……；应……（给出符合中小学校的可操作建议）。（断行）

    数据行为在数据行为监测表现……；在数据应用成效表现……；应……（给出符合中小学校的可操作建议）。（断行）

    数据资产在数据资产意识表现……；在数据资产积累表现……；应……（给出符合中小学校的可操作建议）。（断行）

    数据技术在数据基础设施表现……；在数据安全水平表现……；应……（给出符合中小学校的可操作建议）。
    """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成整体建议失败: {str(e)}")
            return self._get_default_overall_suggestion(
                total_score,
                maturity_level,
                report_data.get('dimension_scores', {})
            )

    def generate_literacy_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据素养建议"""
        dimension_score = report_data['dimension_scores']['literacy']
        obs = report_data.get('observation_scores', {})

        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议。

    学校所获的分值：
    该校的数据素养得分为{dimension_score:.2f}分。每个观测点的得分是：

    教师数据素养：
    教师数据意识与思维（{obs.get('A11', 0):.2f}分）、
    教师数据知识与技能（{obs.get('A12', 0):.2f}分）、
    教师数据评价与交流（{obs.get('A13', 0):.2f}分）、
    教师数据应用与创新（{obs.get('A14', 0):.2f}分）、
    教师数据伦理与隐私（{obs.get('A15', 0):.2f}分）。

    学生数据素养：
    学生数据意识与思维（{obs.get('A31', 0):.2f}分）、
    学生数据知识与技能（{obs.get('A32', 0):.2f}分）、
    学生数据评价与交流（{obs.get('A33', 0):.2f}分）、
    学生数据应用与创新（{obs.get('A34', 0):.2f}分）、
    学生数据伦理与隐私（{obs.get('A35', 0):.2f}分）。

    你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
    1. 评价每个观测点的四个分数区间分为：表现有待提升[大于0且小于等于1.5]，表现比较良好[大于1.5且小于等于3.0]，表现较为优秀[大于3.0且小于等于4.0]，表现非常优秀[大于4.0且小于等于5.0]。
    2. 表现较为优秀和表现非常优秀的观测点，不需要回复“应……”。只呈现“表现……”。分数区间判断必须准确。
    3. 必须按照下面格式回复，不呈现分值，字数110字左右。

    该校数据素养得分为{dimension_score:.2f}分，整体……（正面评价）。（断行）

    其中，教师数据素养在教师数据意识与思维表现……；在教师数据知识与技能表现……；在教师数据评价与交流表现……；在教师数据应用与创新表现……；在教师数据伦理与隐私表现……；应注重……（给出符合中小学校的可操作建议）。（断行）

    学生数据素养在学生数据意识与思维表现……；在学生数据知识与技能表现……；在学生数据评价与交流表现……；在学生数据应用与创新表现……；在学生数据伦理与隐私表现……；应注重……（给出符合中小学校的可操作建议）。
    """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据素养建议失败: {str(e)}")
            return self._get_default_literacy_suggestion(dimension_score, obs)

    def generate_institution_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据制度建议"""
        dimension_score = report_data['dimension_scores']['institution']
        secondary_scores = report_data.get('secondary_scores', {})
        # 获取观测点具体分数（5分制）
        obs = report_data.get('observation_scores', {})

        # 核心修改：将真实的观测点分值（5分制）填入提示词，替换掉 (X分)
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的数据制度得分为{dimension_score:.2f}分。每个维度的得分是：
        数据组织机构：数据领导/工作小组（{obs.get('B11', 0):.2f}分）、数据组织运行情况（{obs.get('B12', 0):.2f}分）
        数据人员配备：数据专职/兼职管理人员（{obs.get('B21', 0):.2f}分）、数据人员进修与培训情况（{obs.get('B22', 0):.2f}分）
        数据管理文件：数据管理制度类文件（{obs.get('B31', 0):.2f}分）、数据实践指导类文件（{obs.get('B32', 0):.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数150字左右。
        该校数据制度得分为{dimension_score:.2f}分，整体……（正面评价）。（断行）
        其中，数据组织机构在数据领导/工作小组表现……（根据四个分数区间匹配）；在数据组织运行情况表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据人员配备在数据专职/兼职管理人员当中表现……（根据四个分数区间匹配）；在数据人员进修与培训情况当中表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据管理文件在数据管理制度类文件表现……（根据四个分数区间匹配）；在数据实践指导类文件表现……（根据四个分数区间匹配）应注重……（给出符合中小学校的可操作的建议）。
        """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据制度建议失败: {str(e)}")
            return self._get_default_institution_suggestion(dimension_score, obs)

    def generate_behavior_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据行为建议"""
        dimension_score = report_data['dimension_scores']['behavior']
        obs = report_data.get('observation_scores', {})

        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议。

    学校所获的分值：
    该校的数据行为得分为{dimension_score:.2f}分。每个观测点的得分是：
    数据行为监测：教师数据行为（{obs.get('C11', 0):.2f}分）、学生数据行为（{obs.get('C12', 0):.2f}分）
    数据应用成效：数据应用特色成果（{obs.get('C21', 0):.2f}分）、数据应用社会影响（{obs.get('C22', 0):.2f}分）、教师对数据应用效果的主观评价（{obs.get('C23', 0):.2f}分）

    你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
    1. 评价每个观测点的四个分数区间分为：表现有待提升[大于0且小于等于1.5]，表现比较良好[大于1.5且小于等于3.0]，表现较为优秀[大于3.0且小于等于4.0]，表现非常优秀[大于4.0且小于等于5.0]。
    2. 表现较为优秀和表现非常优秀的观测点，不需要回复“应……”。只呈现“表现……”。分数区间判断必须准确。
    3. 必须按照下面格式回复，不呈现分值，字数110字左右。

    该校数据行为得分为{dimension_score:.2f}分，整体……（正面评价）。（断行）

    其中，数据行为监测在教师数据行为表现……；在学生数据行为表现……；应注重……（给出符合中小学校的可操作建议）。（断行）

    数据应用成效在数据应用特色成果表现……；在数据应用社会影响表现……；在教师对数据应用效果的主观评价表现……；应注重……（给出符合中小学校的可操作建议）。
    """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据行为建议失败: {str(e)}")
            return self._get_default_behavior_suggestion(dimension_score, obs)

    def generate_asset_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据资产建议"""
        dimension_score = report_data['dimension_scores']['asset']
        # 获取具体的观测点分数（5分制）
        obs = report_data.get('observation_scores', {})

        # 核心修改：将真实的观测点分值填入提示词，替换掉 (X分)
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的数据资产得分为{dimension_score:.2f}分。每个维度的得分是：
        数据资产意识：数据资产价值意识（{obs.get('D11', 0):.2f}分）、数据资产应用意识（{obs.get('D12', 0):.2f}分）、数据资产治理意识（{obs.get('D13', 0):.2f}分）
        数据资产积累：数据资产总量（{obs.get('D21', 0):.2f}分）、人均数据资产量（{obs.get('D22', 0):.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数110字左右。
        该校数据资产得分为{dimension_score:.2f}分，整体……（正面评价）。
        其中，数据资产意识在数据资产价值意识表现……（根据四个分数区间匹配）；在数据资产应用意识表现……（根据四个分数区间匹配）；在数据资产治理意识表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据资产积累在数据资产总量表现……（根据四个分数区间匹配）；在人均数据资产量表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。
        """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据资产建议失败: {str(e)}")
            return self._get_default_asset_suggestion(dimension_score, obs)

    def generate_technology_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据技术建议"""
        dimension_score = report_data['dimension_scores']['technology']
        # 获取具体的观测点分数（5分制）
        obs = report_data.get('observation_scores', {})

        # 核心修改：将真实的观测点分值（5分制）填入提示词，替换掉 (X分)
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的数据技术得分为{dimension_score:.2f}分。每个维度的得分是：
        数据基础设施：数据硬件设施（{obs.get('E11', 0):.2f}分）、数据系统平台（{obs.get('E12', 0):.2f}分）
        数据安全水平：数据安全合规与认证（{obs.get('E21', 0):.2f}分）、数据风险事件记录（{obs.get('E22', 0):.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数110字左右。
        该校数据技术得分为{dimension_score:.2f}分，整体……（正面评价）。
        其中数据基础设施在数据硬件设施表现……（根据四个分数区间匹配）；在数据系统平台表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据安全水平在数据安全合规与认证表现……（根据四个分数区间匹配）；在数据风险事件记录表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。
        """


        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据技术建议失败: {str(e)}")
            return self._get_default_technology_suggestion(dimension_score, obs)
    
    def normalize_cached_suggestions(self, report_data: Dict[str, Any], cached: Dict[str, Any]) -> Dict[str, Any]:
        """升级旧版建议缓存，修复已知的通用兜底文案和标点问题。"""
        result = dict(cached or {})
        if result.get('_schema_version') == self.SUGGESTION_SCHEMA_VERSION:
            return result

        total_score = float(report_data.get('total_score') or 0)
        maturity_level = report_data.get('maturity_level') or '初始级'
        dimensions = report_data.get('dimension_scores', {}) or {}
        observations = report_data.get('observation_scores', {}) or {}

        overall = str(result.get('overall') or '')
        if not overall or '建议重点针对薄弱环节加强投入' in overall:
            result['overall'] = self._get_default_overall_suggestion(
                total_score,
                maturity_level,
                dimensions,
            )

        literacy = str(result.get('literacy') or '')
        if not literacy or '数据素养维度表现均衡' in literacy:
            result['literacy'] = self._get_default_literacy_suggestion(
                float(dimensions.get('literacy') or 0),
                observations,
            )

        institution = str(result.get('institution') or '')
        if not institution or '数据制度维度表现均衡' in institution:
            result['institution'] = self._get_default_institution_suggestion(
                float(dimensions.get('institution') or 0),
                observations,
            )

        detailed_defaults = {
            'behavior': self._get_default_behavior_suggestion,
            'asset': self._get_default_asset_suggestion,
            'technology': self._get_default_technology_suggestion,
        }
        dimension_names = {
            'behavior': '数据行为',
            'asset': '数据资产',
            'technology': '数据技术',
        }
        for key, generator in detailed_defaults.items():
            content = str(result.get(key) or '')
            name = dimension_names[key]
            legacy_markers = (
                f'该校{name}维度表现均衡',
                f'该校{name}维度目前表现较差',
                f'该校{name}维度表现优秀',
            )
            if not content or any(marker in content for marker in legacy_markers):
                result[key] = generator(
                    float(dimensions.get(key) or 0),
                    observations,
                )

        if result.get('technology'):
            result['technology'] = str(result['technology']).replace('数据安全水平在：', '数据安全水平在')

        result['_schema_version'] = self.SUGGESTION_SCHEMA_VERSION
        return result

    def regenerate_fallback_suggestions(self, report_data: Dict[str, Any], cached: Dict[str, Any]) -> Dict[str, Any]:
        """仅重新生成已识别为兜底文案的建议，正常的大模型缓存保持不变。"""
        result = dict(cached or {})
        dimensions = report_data.get('dimension_scores', {}) or {}
        observations = report_data.get('observation_scores', {}) or {}
        total_score = float(report_data.get('total_score') or 0)
        maturity_level = report_data.get('maturity_level') or '初始级'

        fallbacks = {
            'overall': self._get_default_overall_suggestion(total_score, maturity_level, dimensions),
            'literacy': self._get_default_literacy_suggestion(
                float(dimensions.get('literacy') or 0), observations
            ),
            'institution': self._get_default_institution_suggestion(
                float(dimensions.get('institution') or 0), observations
            ),
            'behavior': self._get_default_behavior_suggestion(
                float(dimensions.get('behavior') or 0), observations
            ),
            'asset': self._get_default_asset_suggestion(
                float(dimensions.get('asset') or 0), observations
            ),
            'technology': self._get_default_technology_suggestion(
                float(dimensions.get('technology') or 0), observations
            ),
        }
        generators = {
            'overall': self.generate_overall_suggestion,
            'literacy': self.generate_literacy_suggestion,
            'institution': self.generate_institution_suggestion,
            'behavior': self.generate_behavior_suggestion,
            'asset': self.generate_asset_suggestion,
            'technology': self.generate_technology_suggestion,
        }

        regenerated = []
        for key, generator in generators.items():
            content = str(result.get(key) or '')
            fallback = fallbacks[key]
            if not self._is_cached_fallback(key, content, fallback):
                continue

            generated = str(generator(report_data) or '').strip()
            # 调用失败时 generate_* 会返回同一条兜底文案；此时不把它误标为正常 AI 结果。
            if generated and generated != fallback:
                result[key] = generated
                regenerated.append(key)

        if regenerated:
            logger.info("已重新生成学校报告兜底建议: %s", regenerated)

        result['_schema_version'] = self.SUGGESTION_SCHEMA_VERSION
        return result

    def _is_cached_fallback(self, key: str, content: str, current_fallback: str) -> bool:
        """识别旧版通用兜底和新版详细兜底，不把正常大模型内容重复送审。"""
        if not content or content == current_fallback:
            return True

        markers = {
            'overall': (
                '建议重点针对薄弱环节加强投入',
                '制定专项改进计划，并按学期跟踪关键指标变化',
            ),
            'literacy': (
                '数据素养维度表现均衡',
                '建议通过校本研修和真实教学任务强化数据分析',
            ),
            'institution': (
                '数据制度维度表现均衡',
                '建议明确牵头部门、岗位责任和例会机制',
            ),
            'behavior': (
                '数据行为维度表现均衡',
                '数据行为维度目前表现较差',
                '数据行为维度表现优秀',
                '建议完善师生数据使用记录和常态化反馈机制',
            ),
            'asset': (
                '数据资产维度表现均衡',
                '数据资产维度目前表现较差',
                '数据资产维度表现优秀',
                '建议通过校内培训和典型应用场景强化数据价值',
            ),
            'technology': (
                '数据技术维度表现均衡',
                '数据技术维度目前表现较差',
                '数据技术维度表现优秀',
                '建议落实网络安全等级保护、日常运维和风险事件处置机制',
            ),
        }
        return any(marker in content for marker in markers.get(key, ()))

    def _performance_label(self, score: Any) -> str:
        try:
            value = float(score or 0)
        except (TypeError, ValueError):
            value = 0

        if value <= 1.5:
            return '有待提升'
        if value <= 3.0:
            return '比较良好'
        if value <= 4.0:
            return '较为优秀'
        return '非常优秀'

    def _get_default_literacy_suggestion(self, dimension_score: float, obs: Dict[str, Any]) -> str:
        teacher_items = [
            ('数据意识与思维', obs.get('A11', 0)),
            ('数据知识与技能', obs.get('A12', 0)),
            ('数据评价与交流', obs.get('A13', 0)),
            ('数据应用与创新', obs.get('A14', 0)),
            ('数据伦理与隐私', obs.get('A15', 0)),
        ]
        student_items = [
            ('数据意识与思维', obs.get('A31', 0)),
            ('数据知识与技能', obs.get('A32', 0)),
            ('数据评价与交流', obs.get('A33', 0)),
            ('数据应用与创新', obs.get('A34', 0)),
            ('数据伦理与隐私', obs.get('A35', 0)),
        ]

        def summary(items):
            return '；'.join(f'{name}表现{self._performance_label(score)}' for name, score in items)

        return (
            f'该校数据素养得分为{dimension_score:.2f}分，整体处于{self._performance_label(dimension_score)}水平。\n'
            f'其中，教师数据素养在{summary(teacher_items)}；建议通过校本研修和真实教学任务强化数据分析、评价与应用。\n'
            f'学生数据素养在{summary(student_items)}；建议把数据判断、隐私保护和创新应用融入学科项目与综合实践。'
        )

    def _get_default_institution_suggestion(self, dimension_score: float, obs: Dict[str, Any]) -> str:
        groups = [
            ('数据组织机构', [('数据领导/工作小组', obs.get('B11', 0)), ('数据组织运行情况', obs.get('B12', 0))]),
            ('数据人员配备', [('专职/兼职管理人员', obs.get('B21', 0)), ('人员进修与培训', obs.get('B22', 0))]),
            ('数据管理文件', [('管理制度类文件', obs.get('B31', 0)), ('实践指导类文件', obs.get('B32', 0))]),
        ]
        paragraphs = [
            f'该校数据制度得分为{dimension_score:.2f}分，整体处于{self._performance_label(dimension_score)}水平。'
        ]
        advice = {
            '数据组织机构': '建议明确牵头部门、岗位责任和例会机制',
            '数据人员配备': '建议补齐专兼职人员并制定年度培训计划',
            '数据管理文件': '建议完善覆盖采集、使用、共享、安全和操作指导的制度文件',
        }
        for group_name, items in groups:
            detail = '；'.join(f'{name}表现{self._performance_label(score)}' for name, score in items)
            paragraphs.append(f'{group_name}在{detail}；{advice[group_name]}。')
        return '\n'.join(paragraphs)

    def _get_default_behavior_suggestion(self, dimension_score: float, obs: Dict[str, Any]) -> str:
        monitoring = [
            ('教师数据行为', obs.get('C11', 0)),
            ('学生数据行为', obs.get('C12', 0)),
        ]
        outcomes = [
            ('数据应用特色成果', obs.get('C21', 0)),
            ('数据应用社会影响', obs.get('C22', 0)),
            ('教师对数据应用效果的主观评价', obs.get('C23', 0)),
        ]

        def summary(items):
            return '；'.join(f'{name}表现{self._performance_label(score)}' for name, score in items)

        return (
            f'该校数据行为得分为{dimension_score:.2f}分，整体处于{self._performance_label(dimension_score)}水平。\n'
            f'其中，数据行为监测在{summary(monitoring)}；建议完善师生数据使用记录和常态化反馈机制，推动数据应用融入教学与学习过程。\n'
            f'数据应用成效在{summary(outcomes)}；建议加强成果提炼、应用评价和经验推广，形成“分析—反馈—改进”闭环。'
        )

    def _get_default_asset_suggestion(self, dimension_score: float, obs: Dict[str, Any]) -> str:
        awareness = [
            ('数据资产价值意识', obs.get('D11', 0)),
            ('数据资产应用意识', obs.get('D12', 0)),
            ('数据资产治理意识', obs.get('D13', 0)),
        ]
        accumulation = [
            ('数据资产总量', obs.get('D21', 0)),
            ('人均数据资产量', obs.get('D22', 0)),
        ]

        def summary(items):
            return '；'.join(f'{name}表现{self._performance_label(score)}' for name, score in items)

        return (
            f'该校数据资产得分为{dimension_score:.2f}分，整体处于{self._performance_label(dimension_score)}水平。\n'
            f'其中，数据资产意识在{summary(awareness)}；建议通过校内培训和典型应用场景强化数据价值、应用与治理意识。\n'
            f'数据资产积累在{summary(accumulation)}；建议建立数据资源目录和质量管理机制，持续沉淀、共享并复用教育教学数据。'
        )

    def _get_default_technology_suggestion(self, dimension_score: float, obs: Dict[str, Any]) -> str:
        infrastructure = [
            ('数据硬件设施', obs.get('E11', 0)),
            ('数据系统平台', obs.get('E12', 0)),
        ]
        security = [
            ('数据安全合规与认证', obs.get('E21', 0)),
            ('数据风险事件记录', obs.get('E22', 0)),
        ]

        def summary(items):
            return '；'.join(f'{name}表现{self._performance_label(score)}' for name, score in items)

        return (
            f'该校数据技术得分为{dimension_score:.2f}分，整体处于{self._performance_label(dimension_score)}水平。\n'
            f'其中，数据基础设施在{summary(infrastructure)}；建议结合教学和管理需求持续完善终端设备、数据平台及系统互联能力。\n'
            f'数据安全水平在{summary(security)}；建议落实网络安全等级保护、日常运维和风险事件处置机制，提升技术环境的安全性与稳定性。'
        )

    def _get_default_overall_suggestion(self, total_score: float, maturity_level: str, dimension_scores: Dict[str, Any] = None) -> str:
        """获取默认的整体建议（当AI调用失败时使用，基于5分制）"""
        labels = {
            'literacy': '数据素养',
            'institution': '数据制度',
            'behavior': '数据行为',
            'asset': '数据资产',
            'technology': '数据技术',
        }
        scores = dimension_scores or {}
        ordered = sorted(labels, key=lambda key: float(scores.get(key) or 0))
        weak = '、'.join(labels[key] for key in ordered[:2])
        targeted = f'建议优先围绕{weak}制定专项改进计划，并按学期跟踪关键指标变化。'

        # total_score 预期为 0.0 - 5.0 之间
        if total_score >= 4.0:
            return f"该校数据文化得分为{total_score:.2f}分，处于创新级，整体表现优秀。{targeted}同时总结可复制的制度和应用经验，发挥示范引领作用。"
        elif total_score >= 3.0:
            return f"该校数据文化得分为{total_score:.2f}分，处于成熟级，已建立较完善的数据管理与应用基础。{targeted}推动数据应用形成持续改进闭环。"
        elif total_score >= 1.5:
            return f"该校数据文化得分为{total_score:.2f}分，处于成长级，已初步建立数据文化基础，但各维度仍需协同提升。{targeted}"
        else:
            return f"该校数据文化得分为{total_score:.2f}分，处于初始级，数据文化建设处于起步阶段。{targeted}同步完善基础制度、人员分工和技术保障。"

    def _get_default_dimension_suggestion(self, dimension_score: float, dimension_name: str) -> str:
        """获取默认的维度建议（当AI调用失败时使用，基于5分制）"""
        # 基于提示词标准：[0-1.5]较差，(1.5-4]均衡，(4-5]优秀
        if dimension_score > 4.0:
            return f"该校{dimension_name}维度表现优秀，得分为{dimension_score:.2f}分。建议总结优秀经验并在校内推广，维持高水平发展。"
        elif dimension_score > 1.5:
            return f"该校{dimension_name}维度表现均衡，得分为{dimension_score:.2f}分。虽然已具备一定基础，但在细节落实和深度应用上仍有提升空间，建议针对性加强建设。"
        else:
            return f"该校{dimension_name}维度目前表现较差，得分为{dimension_score:.2f}分。建议学校高度重视该维度的建设，从制度、人员或技术投入上寻找突破点，尽快补齐短板。"
