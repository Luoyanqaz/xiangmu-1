"""
区域报告 AI 建议生成服务
用于生成区域报告中的：
1. 初始级学校发展建议
2. 成长级学校发展建议
3. 成熟级学校发展建议
4. 引领级学校发展建议
5. 区域发展建议总述
6. 数据素养发展建议
7. 数据制度发展建议
8. 数据行为发展建议
9. 数据资产发展建议
10. 数据技术发展建议
11. 区域总体结论
"""

import re
import logging
from typing import Dict, Any, List
import json

from apps.assessments.llm_service import LLMService

logger = logging.getLogger(__name__)


class RegionReportAIService:
    """区域报告 AI 建议生成服务"""

    def __init__(self):
        self.llm_service = LLMService()
        self.used_fallback = False

    def _score_5(self, value: Any) -> float:
        """
        将区域报告分数统一转换为 0-5 分制。
        兼容：
        1. 原本就是 0-5；
        2. 维度百分制 0-100；
        3. 总分制 0-500。
        """
        score = self._score(value)

        if score <= 5:
            return score

        # 区域总分如果是 0-500，折算为 0-5
        if score > 100:
            return min(score / 100, 5.0)

        # 维度分如果是 0-100，折算为 0-5
        return min(score / 20, 5.0)

    def generate_all_suggestions(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成区域报告建议：
        1. 四类成熟度等级学校建议：固定文本，不调用大模型；
        2. 区域整体建议：使用你提供的提示语调用大模型；
        3. 后端将 AI 返回内容拆分成 summary / items / conclusion，保持前端原界面不变。
        """
        logger.info("开始生成区域报告建议")

        if (not report_data.get('summary', {}).get('completed_school_count') or
                not any(row.get('count') for row in report_data.get('dimension_statistics', []))):
            return {'level_suggestions': {}, 'dimension_suggestions': {}, 'suggestion_mode': 'no_data',
                    'development': {'summary': '暂无已完成评估，暂不生成发展判断。', 'items': [], 'conclusion': ''}}

        result = {
            "level_suggestions": {
                "initial": self.generate_initial_level_suggestion(report_data),
                "growing": self.generate_growing_level_suggestion(report_data),
                "mature": self.generate_mature_level_suggestion(report_data),
                "leading": self.generate_leading_level_suggestion(report_data),
            },
            "development": self.generate_region_overall_ai_advice(report_data)
        }
        from apps.reports.statistics import DIMENSIONS
        items = result['development'].get('items', [])
        result['dimension_suggestions'] = {
            key: next((item.get('content', '') for item in items if item.get('dimension') == label), '')
            for key, label, _ in DIMENSIONS
        }
        result['suggestion_mode'] = 'fallback' if self.used_fallback else 'ai'

        logger.info("区域报告建议生成完成")
        return result

    # 兼容你之前 view 里可能调用的旧方法名
    def generate_region_report_suggestions(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.generate_all_suggestions(report_data)


    def _participating_school_count(self, report_data: Dict[str, Any]) -> int:
        """
        获取本区域参与评价学校数量。
        优先使用 completed_school_count，其次使用 completed_count，最后使用 school_count。
        """
        summary = report_data.get("summary", {}) or {}

        value = (
            summary.get("completed_school_count")
            or summary.get("completed_count")
            or summary.get("school_count")
            or 0
        )

        try:
            return int(value)
        except Exception:
            return 0

    def _level_count_ratio(self, report_data: Dict[str, Any], level_key: str):
        """
        获取某一成熟度等级的学校数量和占比。
        返回值：
        count: int
        ratio: str，例如 "25.0"
        """
        total = self._participating_school_count(report_data)

        level_distribution = report_data.get("level_distribution", []) or []

        for item in level_distribution:
            if item.get("key") == level_key:
                count = item.get("count", 0)
                ratio = item.get("ratio", None)

                try:
                    count = int(count)
                except Exception:
                    count = 0

                if ratio is None or ratio == "":
                    ratio = (count / total * 100) if total else 0

                try:
                    ratio = float(ratio)
                except Exception:
                    ratio = 0.0

                return count, f"{ratio:.1f}"

        # 如果 level_distribution 里没有，就从 level_analysis 兜底取
        level = self._get_level_analysis(report_data, level_key)
        count = level.get("count", 0)

        try:
            count = int(count)
        except Exception:
            count = 0

        ratio = (count / total * 100) if total else 0

        return count, f"{ratio:.1f}"

    # =========================
    # 一、各成熟度等级学校建议
    # =========================

    def generate_initial_level_suggestion(self, report_data: Dict[str, Any]) -> str:
        """初始级学校固定建议"""
        total = self._participating_school_count(report_data)
        count, ratio = self._level_count_ratio(report_data, "initial")

        return (
            f"本区域参与评价学校共{total}所，其中处于初始级的学校共{count}所，占比{ratio}%，"
            f"表明这些学校数据文化处于起步阶段，成员数据意识正在形成，制度规范、应用场景、"
            f"资源积累和技术支撑尚处基础建设期。\n\n"
            f"为了进一步向成长级发展，建议初始级学校在数据素养方面开展基础培训，提升教师数据意识；"
            f"在数据制度方面明确数据工作牵头部门，建立最基本的数据采集、使用和管理规则；"
            f"在数据行为方面选择教学、评价或管理中的少量场景开展试点应用；"
            f"在数据资产方面梳理学校已有数据资源，建立基础数据台账，明确数据来源和责任人；"
            f"在数据技术方面完善基础平台、账号权限和数据备份机制，优先保障数据可用与安全。"
        )

    def generate_growing_level_suggestion(self, report_data: Dict[str, Any]) -> str:
        """成长级学校固定建议"""
        total = self._participating_school_count(report_data)
        count, ratio = self._level_count_ratio(report_data, "growing")

        return (
            f"本区域参与评价学校共{total}所，其中处于成长级的学校共{count}所，占比{ratio}%，"
            f"表明这些学校数据文化进入规范发展阶段，成员初步具备数据应用能力，制度分工逐渐清晰，"
            f"数据应用和资源管理开始走向常态。\n\n"
            f"为了进一步向成熟级发展，建议成长级学校在数据素养方面围绕常用数据工具和典型应用场景开展分层培训，"
            f"提升教师“会用数据”的能力；在数据制度方面细化岗位分工和流程要求，形成数据采集、审核、应用和反馈的运行机制；"
            f"在数据行为方面推动数据应用从单点试用转向固定流程，形成常规监测和阶段性反馈；"
            f"在数据资产方面建立数据分类、命名和更新规范，提高数据积累的完整性和一致性；"
            f"在数据技术方面推进平台功能整合，提升数据汇聚、查询和可视化分析能力。"
        )

    def generate_mature_level_suggestion(self, report_data: Dict[str, Any]) -> str:
        """成熟级学校固定建议"""
        total = self._participating_school_count(report_data)
        count, ratio = self._level_count_ratio(report_data, "mature")

        return (
            f"本区域参与评价学校共{total}所，其中处于成熟级的学校共{count}所，占比{ratio}%，"
            f"表明这些学校数据文化形成稳定运行状态，成员能够运用数据改进实践，制度运行较为规范，"
            f"数据应用覆盖多类场景，资源共享和技术保障较为完善。\n\n"
            f"为了进一步向创新级发展，建议成熟级学校在数据素养方面培养数据分析骨干，"
            f"引导教师基于数据开展教学改进、学生支持和管理优化；在数据制度方面建立数据质量审核、"
            f"应用评价和持续改进机制，提升制度执行效果；在数据行为方面推动数据应用贯穿教学、教研、"
            f"评价和治理过程，形成“分析—反馈—改进”闭环；在数据资产方面建设可共享、可复用的数据资源库，"
            f"促进跨部门数据协同使用；在数据技术方面加强系统互联互通和安全审计，提升平台稳定性、协同性和风险防控能力。"
        )

    def generate_leading_level_suggestion(self, report_data: Dict[str, Any]) -> str:
        """创新级学校固定建议"""
        total = self._participating_school_count(report_data)
        count, ratio = self._level_count_ratio(report_data, "leading")

        return (
            f"本区域参与评价学校共{total}所，其中处于创新级的学校共{count}所，占比{ratio}%，"
            f"表明这些学校数据文化达到创新引领阶段，成员具备较强的数据创新能力，制度治理精细前瞻，"
            f"数据应用深度融合，资源价值和技术支撑水平较高。\n\n"
            f"为了持续发挥示范引领作用，建议创新级学校在数据素养方面建设数据应用共同体，"
            f"支持教师开展数据驱动的创新实践、案例提炼和经验推广；在数据制度方面完善前瞻性治理规则，"
            f"探索数据伦理、算法应用和智能决策的管理机制；在数据行为方面推进预测性分析、个性化支持和智能化治理，"
            f"形成具有示范意义的应用模式；在数据资产方面推动数据资源深度开发，形成可推广的数据产品、服务模式和实践成果；"
            f"在数据技术方面建设智能化、一体化、安全可信的技术环境，提升数据治理的智能化和韧性水平。"
        )

    def _split_region_overall_advice(self, text: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将 AI 返回的固定格式内容拆成前端需要的 summary / items / conclusion。
        """
        text = self._clean_ai_report_text(text)

        if not text:
            return self._default_region_development_struct(report_data)

        sections = {
            "summary": "",
            "literacy": "",
            "institution": "",
            "behavior": "",
            "asset": "",
            "technology": "",
            "conclusion": ""
        }

        tag_map = {
            "【总体判断】": "summary",
            "【数据素养建议】": "literacy",
            "【数据制度建议】": "institution",
            "【数据行为建议】": "behavior",
            "【数据资产建议】": "asset",
            "【数据技术建议】": "technology",
            "【总体战略目标】": "conclusion",
        }

        current = "summary"

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if line in tag_map:
                current = tag_map[line]
                continue

            # 兼容模型把标题和正文写在同一行的情况
            matched_tag = None
            for tag, key in tag_map.items():
                if line.startswith(tag):
                    matched_tag = tag
                    current = key
                    remain = line.replace(tag, "", 1).strip()
                    if remain:
                        sections[current] += remain + "\n"
                    break

            if matched_tag:
                continue

            sections[current] += line + "\n"

        return {
            "summary": sections["summary"].strip() or self._default_development_summary(report_data),
            "items": [
                {
                    "index": 1,
                    "title": "加强数据素养培养",
                    "dimension": "数据素养",
                    "content": sections["literacy"].strip() or self._default_dimension_advice("literacy")
                },
                {
                    "index": 2,
                    "title": "完善数据治理制度",
                    "dimension": "数据制度",
                    "content": sections["institution"].strip() or self._default_dimension_advice("institution")
                },
                {
                    "index": 3,
                    "title": "推动数据应用落地",
                    "dimension": "数据行为",
                    "content": sections["behavior"].strip() or self._default_dimension_advice("behavior")
                },
                {
                    "index": 4,
                    "title": "提升数据资产意识",
                    "dimension": "数据资产",
                    "content": sections["asset"].strip() or self._default_dimension_advice("asset")
                },
                {
                    "index": 5,
                    "title": "夯实数据技术支撑",
                    "dimension": "数据技术",
                    "content": sections["technology"].strip() or self._default_dimension_advice("technology")
                }
            ],
            "conclusion": sections["conclusion"].strip() or self._default_conclusion()
        }

    def generate_region_overall_ai_advice(self, report_data: Dict[str, Any]) -> str:
        summary = report_data.get("summary", {}) or {}
        dim = report_data.get("dimension_average", {}) or {}

        avg_score = self._score_5(summary.get("avg_score"))

        literacy = self._score_5(dim.get("literacy"))
        institution = self._score_5(dim.get("institution"))
        behavior = self._score_5(dim.get("behavior"))
        asset = self._score_5(dim.get("asset"))
        technology = self._score_5(dim.get("technology"))

        dimension_rows = [
            ("数据素养", literacy),
            ("数据制度", institution),
            ("数据行为", behavior),
            ("数据资产", asset),
            ("数据技术", technology),
        ]

        highest_name, highest_score = max(dimension_rows, key=lambda x: x[1])
        lowest_name, lowest_score = min(dimension_rows, key=lambda x: x[1])

        prompt = f"""
    你好，现在我要生成《区域数据文化评估报告》中“区域整体建议”板块。请你结合区域五个维度的平均得分，围绕数据素养、数据制度、数据行为、数据资产、数据技术五个方面提出区域层面的优化建议。

    本区域整体平均分为 {avg_score:.2f} 分，五个维度平均得分如下：数据素养{literacy:.2f}分、数据制度 {institution:.2f} 分、数据行为 {behavior:.2f} 分、数据资产 {asset:.2f} 分、数据技术 {technology:.2f} 分。其中，得分最高的维度为 {highest_name}，得分最低的维度为 {lowest_name}，各维度之间呈现出……的发展特征。

    请先依据以下分数区间对五个维度的发展水平进行内部判断，但不要在正文中单独写出“依据分数区间判断：……”或逐项罗列判断结果：
    0.0≤得分＜1.5：初始水平；
    1.5≤得分＜3.0：成长水平；
    3.0≤得分＜4.0：成熟水平；
    4.0≤得分≤5.0：创新水平。

    请按照以下要求撰写：

    1. 先对区域五个维度的整体表现进行简要判断。判断时不能只根据五个维度之间的相对高低来简单区分“优势”和“短板”，必须先依据上述绝对分数区间判断每个维度所处的发展水平。

    2. 如果多个维度处于同一分数区间，应将其判断为同一发展水平，不要强行区分为“优势维度”和“薄弱维度”。例如，数据素养 2.6 分、数据制度 2.4 分均属于成长水平，只能表述为“两个维度均处于成长水平，数据素养略高于数据制度”，不能表述为“数据素养表现较好、数据制度较为薄弱”。

    3. 如果不同维度跨越了不同分数区间，可以适度区分发展层次：
       处于初始水平的维度，应作为区域基础建设重点；
       处于成长水平的维度，应作为区域规范提升重点；
       处于成熟水平的维度，应作为区域协同优化重点；
       处于创新水平的维度，应作为区域示范引领重点。

    4. 在整体判断中，应同时说明五个维度是否处于同一发展区间，是否存在跨区间差异，区域数据文化发展是否均衡。如果维度之间分数差距不大，应使用“整体较为接近”“发展水平相对均衡”等表述；如果存在明显跨区间差异，再使用“发展不均衡”“部分维度相对滞后”等表述。

    5. 建议要体现区域整体层面的推进思路，不要重复前面针对初始级、成长级、成熟级、创新级学校的建议。不要写成某一类学校的改进措施，而要从区域统筹、标准建设、资源配置、协同推进、监测反馈、示范引领等角度展开。

    6. 五个维度的建议要根据“该维度得分区间+该维度本身内涵”来写，避免内容交叉重复：
       数据素养方面，重点从区域教师数据能力培养体系、数据应用骨干队伍、校际研修共同体等角度提出建议；
       数据制度方面，重点从区域数据管理标准、责任清单、协同机制、质量监管机制等角度提出建议；
       数据行为方面，重点从区域常态化监测、数据反馈机制、跨校对比分析、决策改进闭环等角度提出建议；
       数据资产方面，重点从区域数据资源目录、数据标准统一、校际数据共享、数据资源开发利用等角度提出建议；
       数据技术方面，重点从区域平台整合、系统互联互通、数据安全防护、智能化支撑能力等角度提出建议。

    7. 每个维度建议控制在一小段内，写作顺序为：“该维度得分及所处区间判断+区域层面优化建议”。语言要简洁、客观、具有报告感，不要使用“严重缺失”“非常薄弱”等过于负面的表述，也不要在分数差距较小时夸大发展差异。

    请严格按照以下格式输出，不要输出任何开场白、解释语、Markdown 标题、序号之外的多余内容，不要使用“好的”“作为专家”等表达。

    【总体判断】
    这里撰写区域五个维度的整体表现判断，只写总体判断内容。
    
    【数据素养建议】
    这里撰写数据素养维度建议。
    
    【数据制度建议】
    这里撰写数据制度维度建议。
    
    【数据行为建议】
    这里撰写数据行为维度建议。
    
    【数据资产建议】
    这里撰写数据资产维度建议。
    
    【数据技术建议】
    这里撰写数据技术维度建议。
    
    【总体战略目标】
    这里撰写区域后续总体推进目标。
    """

        prompt += '\n【一级及二级指标统计】\n' + json.dumps(
            report_data.get('dimension_statistics', []), ensure_ascii=False
        )
        prompt += ('\n逐维度结合最高分、最低分、平均分、总体标准差和所属二级指标提出建议。'
                   '优先关注二级指标中平均分较低的方面，说明如何分层支持学校；'
                   '没有有效样本的指标不作水平判断，不把缺失值当作0分；'
                   '单校标准差为0不代表区域发展均衡，不能从描述统计推断因果或显著性。'
                   '各维度建议控制在120—200字。')
        default_text = self._default_region_overall_advice(report_data)
        result = self._call_ai(prompt, default_text, max_tokens=2000)

        # 区域整体建议一次包含 7 个板块，模型输出被截断时不能把半截内容写入缓存。
        if not self._has_complete_region_overall_advice(result):
            logger.warning("区域报告 AI 建议输出不完整，正在重试")
            result = self._call_ai(prompt, default_text, max_tokens=2500)

        if not self._has_complete_region_overall_advice(result):
            logger.warning("区域报告 AI 建议重试后仍不完整，使用完整默认建议")
            result = default_text
            self.used_fallback = True

        return self._split_region_overall_advice(result, report_data)

    def _has_complete_region_overall_advice(self, text: str) -> bool:
        """检查区域整体建议的 7 个固定板块是否均已完整返回。"""
        cleaned = self._clean_ai_report_text(text)
        tags = [
            "【总体判断】",
            "【数据素养建议】",
            "【数据制度建议】",
            "【数据行为建议】",
            "【数据资产建议】",
            "【数据技术建议】",
            "【总体战略目标】",
        ]
        positions = [cleaned.find(tag) for tag in tags]

        if any(position < 0 for position in positions) or positions != sorted(positions):
            return False

        for index, tag in enumerate(tags):
            start = positions[index] + len(tag)
            end = positions[index + 1] if index + 1 < len(tags) else len(cleaned)
            if not cleaned[start:end].strip():
                return False

        return True


    def _remove_heading(self, text: str, headings: list) -> str:
        """
        删除行首标题，保留标题后面的正文。
        """
        value = str(text or "").strip()

        for heading in headings:
            for sep in ["：", ":", ""]:
                prefix = f"{heading}{sep}"
                if value.startswith(prefix):
                    return value[len(prefix):].strip()

        return value

    def _clean_ai_report_text(self, text: str) -> str:
        """
        清理 AI 返回内容中的 Markdown 标记和开场白。
        保留【总体判断】等结构标签，方便后续拆分。
        """
        text = str(text or "").strip()

        if not text:
            return ""

        replacements = {
            "###": "",
            "##": "",
            "#": "",
            "**": "",
            "__": "",
            "`": "",
            "---": "",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # 去掉 AI 常见开场白，但保留正式标签
        text = re.sub(
            r"^好的[，,].*?(?=【总体判断】|总体判断|【数据素养建议】)",
            "",
            text,
            flags=re.S
        )

        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]

        return "\n".join(lines)

    def _default_region_overall_advice(self, report_data: Dict[str, Any]) -> str:
        dim = report_data.get("dimension_average", {}) or {}
        dimension_names = {
            "literacy": "数据素养",
            "institution": "数据制度",
            "behavior": "数据行为",
            "asset": "数据资产",
            "technology": "数据技术",
        }

        def level_text(value):
            score = self._score_5(value)
            if score < 1.5:
                return "初始水平"
            if score < 3.0:
                return "成长水平"
            if score < 4.0:
                return "成熟水平"
            return "创新水平"

        rows = []
        for key, name in dimension_names.items():
            if dim.get(key) is None:
                rows.append(f'【{name}建议】\n该维度暂无有效得分，建议先完善数据采集和核验，暂不判断发展水平。')
            else:
                rows.append(
                    f'【{name}建议】\n{name}维度平均得分为{self._score_5(dim[key]):.2f}分，处于{level_text(dim[key])}。'
                    f'{self._dimension_statistical_advice(report_data, key)}{self._default_dimension_advice(key)}'
                )

        return (
            f"【总体判断】\n{self._default_development_summary(report_data)}\n\n"
            + "\n\n".join(rows)
            + f"\n\n【总体战略目标】\n{self._default_conclusion()}"
        )

    def _dimension_statistical_advice(self, report_data, key):
        row = next((item for item in report_data.get('dimension_statistics', []) if item['key'] == key), None)
        if not row or not row['count']:
            return '当前缺少有效指标数据，应先补齐数据后再开展发展诊断。'
        text = (f"最高分{row['maximum']:.2f}分、最低分{row['minimum']:.2f}分，"
                f"总体标准差{row['std_dev']:.2f}分。")
        if row['count'] == 1:
            text += '目前仅有1所学校，暂不判断校际差异。'
        elif row['std_dev'] > 0:
            text += '建议结合学校实际分类支持，并推动较高分学校分享具体做法。'
        children = [child for child in row.get('secondary_indicators', []) if child['count']]
        if children:
            lowest = min(child['average'] for child in children)
            names = '、'.join(child['label'] for child in children if child['average'] == lowest)
            text += f'所属二级指标中，{names}平均分相对较低（{lowest:.2f}分），可作为后续改进重点。'
        return text
    # =========================
    # 二、区域发展建议总述
    # =========================

    def generate_development_summary(self, report_data: Dict[str, Any]) -> str:
        """生成区域发展建议开头总结"""
        summary = report_data.get("summary", {})
        dim = report_data.get("dimension_average", {})

        prompt = f"""
你现在是一名中小学数据文化成熟度评估专家，需要为区域报告撰写“区域发展建议”的开头总结。

【区域名称】
{self._region_name(report_data)}

【区域概况】
学校总数：{summary.get("school_count", 0)} 所
已完成评估学校数：{summary.get("completed_school_count", 0)} 所
区域平均分：{self._score(summary.get("avg_score")):.2f}
最高分：{self._score(summary.get("highest_score")):.2f}
最低分：{self._score(summary.get("lowest_score")):.2f}

【五维度平均分】
数据素养：{self._score(dim.get("literacy")):.2f}
数据制度：{self._score(dim.get("institution")):.2f}
数据行为：{self._score(dim.get("behavior")):.2f}
数据资产：{self._score(dim.get("asset")):.2f}
数据技术：{self._score(dim.get("technology")):.2f}

【主要短板】
{self._weak_dimensions_text(dim)}

【写作要求】
1. 面向区域教育管理部门。
2. 概括区域整体表现、优势和短板。
3. 不要写成单个学校报告。
4. 字数控制在 60 到 100 字。
5. 直接输出正文，不要标题。
"""

        return self._call_ai(
            prompt,
            self._default_development_summary(report_data)
        )

    # =========================
    # 三、五类区域发展建议
    # =========================

    def generate_literacy_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据素养发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="literacy",
            dimension_name="数据素养",
            title="加强数据素养培养",
            focus="管理者、教师和学生的数据意识、数据知识、数据应用能力、数据伦理与隐私保护",
            requirement="建议重点围绕分层培训、教师数据应用能力提升、学生数据意识培养和管理者数据决策能力建设展开。"
        )

        return {
            "index": 1,
            "title": "加强数据素养培养",
            "dimension": "数据素养",
            "content": content
        }

    def generate_institution_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据制度发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="institution",
            dimension_name="数据制度",
            title="完善数据治理制度",
            focus="数据组织机构、数据人员配备、数据管理文件、职责分工和制度运行机制",
            requirement="建议重点围绕区域统一规范、学校数据职责、制度文件建设和数据治理运行机制展开。"
        )

        return {
            "index": 2,
            "title": "完善数据治理制度",
            "dimension": "数据制度",
            "content": content
        }

    def generate_behavior_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据行为发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="behavior",
            dimension_name="数据行为",
            title="推动数据应用落地",
            focus="教师数据行为、学生数据行为、管理者数据行为、数据应用成果和应用成效",
            requirement="建议重点围绕教学改进、学生发展分析、管理决策、资源配置和数据应用场景常态化展开。"
        )

        return {
            "index": 3,
            "title": "推动数据应用落地",
            "dimension": "数据行为",
            "content": content
        }

    def generate_asset_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据资产发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="asset",
            dimension_name="数据资产",
            title="提升数据资产意识",
            focus="数据资产价值意识、应用意识、治理意识、数据资源积累和数据复用",
            requirement="建议重点围绕数据资源目录、数据质量管理、数据共享机制和数据资产价值转化展开。"
        )

        return {
            "index": 4,
            "title": "提升数据资产意识",
            "dimension": "数据资产",
            "content": content
        }

    def generate_technology_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据技术发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="technology",
            dimension_name="数据技术",
            title="夯实数据技术支撑",
            focus="数据硬件设施、数据系统平台、数据安全合规、终端配置和基础设施保障",
            requirement="建议重点围绕数据平台建设、数字终端配置、数据安全保障和基础设施持续运维展开。"
        )

        return {
            "index": 5,
            "title": "夯实数据技术支撑",
            "dimension": "数据技术",
            "content": content
        }

    def _generate_dimension_development_content(
        self,
        report_data: Dict[str, Any],
        dimension_key: str,
        dimension_name: str,
        title: str,
        focus: str,
        requirement: str
    ) -> str:
        dim = report_data.get("dimension_average", {})
        score = self._score(dim.get(dimension_key))
        region_name = self._region_name(report_data)

        prompt = f"""
你现在是一名中小学数据文化成熟度评估专家，需要为区域报告撰写一条发展建议。

【区域名称】
{region_name}

【建议标题】
{title}

【关联维度】
{dimension_name}

【该维度区域平均分】
{score:.2f}

【该维度关注内容】
{focus}

【写作要求】
1. 面向区域教育管理部门，不要写成单个学校报告。
2. 建议要体现区域层面的统筹、指导、推进和保障。
3. 内容要可操作，避免空泛表述。
4. 不要出现“根据你提供的数据”等口语化表达。
5. 不要编造具体学校名称。
6. 字数控制在 80 到 120 字。
7. {requirement}

请直接输出建议正文，不要输出标题，不要编号。
"""

        return self._call_ai(
            prompt,
            self._default_dimension_advice(dimension_key)
        )

    # =========================
    # 四、总体结论
    # =========================

    def generate_development_conclusion(self, report_data: Dict[str, Any]) -> str:
        """生成区域总体结论"""
        summary = report_data.get("summary", {})
        dim = report_data.get("dimension_average", {})

        prompt = f"""
你现在是一名中小学数据文化成熟度评估专家，需要为区域报告撰写最终的“总体结论”。

【区域名称】
{self._region_name(report_data)}

【区域平均分】
{self._score(summary.get("avg_score")):.2f}

【五维度平均分】
数据素养：{self._score(dim.get("literacy")):.2f}
数据制度：{self._score(dim.get("institution")):.2f}
数据行为：{self._score(dim.get("behavior")):.2f}
数据资产：{self._score(dim.get("asset")):.2f}
数据技术：{self._score(dim.get("technology")):.2f}

【主要短板】
{self._weak_dimensions_text(dim)}

【写作要求】
1. 用于区域报告结尾。
2. 总结区域整体建设水平、后续改进方向和管理建议。
3. 语言正式、简洁、有总结性。
4. 不要写成单个学校报告。
5. 字数控制在 80 到 120 字。
6. 直接输出正文，不要标题。
"""

        return self._call_ai(
            prompt,
            self._default_conclusion()
        )

    # =========================
    # 五、通用工具函数
    # =========================

    def _call_ai(self, prompt: str, default_text: str, max_tokens: int = 500) -> str:
        """统一调用大模型，失败时返回默认文本"""
        try:
            result = self.llm_service._call_api(prompt, max_tokens=max_tokens)
            result = str(result or "").strip()

            if not result:
                self.used_fallback = True
                return default_text

            # 防止模型返回 Markdown 包裹
            result = result.replace("```text", "").replace("```", "").strip()
            return result

        except Exception as e:
            logger.error(f"区域报告 AI 建议生成失败: {str(e)}")
            self.used_fallback = True
            return default_text

    def _region_name(self, report_data: Dict[str, Any]) -> str:
        region = report_data.get("region", {}) or {}
        return f"{region.get('province', '')}{region.get('city', '')}{region.get('name', '')}" or "当前区域"

    def _score(self, value: Any) -> float:
        try:
            if value is None or value == "":
                return 0.0
            return float(value)
        except Exception:
            return 0.0

    def _get_level_analysis(self, report_data: Dict[str, Any], level_key: str) -> Dict[str, Any]:
        levels = report_data.get("level_analysis", []) or []
        for item in levels:
            if item.get("key") == level_key:
                return item

        return {
            "key": level_key,
            "count": 0,
            "avg_score": 0,
            "dimension_average": {}
        }

    def _weak_dimensions_text(self, dimension_average: Dict[str, Any]) -> str:
        weak = self._weak_dimensions(dimension_average)
        if not weak:
            return "暂无明显短板"

        return "、".join([item["label"] for item in weak[:2]])

    def _weak_dimensions(self, dimension_average: Dict[str, Any]) -> List[Dict[str, Any]]:
        label_map = {
            "literacy": "数据素养",
            "institution": "数据制度",
            "behavior": "数据行为",
            "asset": "数据资产",
            "technology": "数据技术",
        }

        result = []
        for key, label in label_map.items():
            if dimension_average.get(key) is None:
                continue
            result.append({
                "key": key,
                "label": label,
                "score": self._score(dimension_average.get(key))
            })

        result.sort(key=lambda x: x["score"])
        return result

    # =========================
    # 六、默认兜底文本
    # =========================

    def _default_level_suggestion(self, level_key: str) -> str:
        defaults = {
            "initial": "该等级学校整体处于基础建设阶段，应优先完善数据制度、基础平台和数据采集机制，逐步提升师生数据意识与常态化应用能力，为后续数据文化建设奠定基础。",
            "growing": "该等级学校已具备一定数据文化基础，但各维度发展仍不均衡。建议围绕薄弱维度开展专项提升，推动数据应用从零散实践走向稳定运行。",
            "mature": "该等级学校整体发展较为成熟，建议进一步加强跨场景数据应用、成果沉淀和经验总结，形成可复制、可推广的区域示范样板。",
            "leading": "该等级学校具备较好的引领基础，建议发挥示范带动作用，输出制度经验、应用案例和治理方法，带动区域内其他学校共同提升。"
        }
        return defaults.get(level_key, "暂无建议。")

    def _default_development_summary(self, report_data: Dict[str, Any]) -> str:
        dim = report_data.get("dimension_average", {})
        weak = self._weak_dimensions_text(dim)
        return f"从区域整体表现看，当前短板主要集中在{weak}等方面，应围绕薄弱维度开展分类指导，并推动高水平学校发挥示范带动作用。"

    def _default_dimension_advice(self, dimension_key: str) -> str:
        defaults = {
            "literacy": "建议面向管理者、教师和学生开展分层培训，提升数据意识、数据分析能力和数据伦理素养，推动数据素养培养融入日常教学与管理过程。",
            "institution": "建议完善区域数据治理规范，推动学校明确数据职责分工、制度文件和常态化运行机制，提升学校数据管理的规范化水平。",
            "behavior": "建议围绕教学改进、学生发展和管理决策等场景，推动数据应用从零散使用走向稳定实践，形成可持续的数据应用机制。",
            "asset": "建议建立数据资源目录，强化数据质量、共享和复用机制，提升学校数据资产沉淀能力，促进数据资源向教育治理价值转化。",
            "technology": "建议完善数据平台、终端设备和安全保障体系，加强数据系统运维和安全合规管理，为区域数据文化建设提供稳定技术支撑。"
        }
        return defaults.get(dimension_key, "建议结合区域实际情况，围绕薄弱环节开展分类指导和持续改进。")

    def _default_conclusion(self) -> str:
        return "区域后续应坚持分类指导、重点突破和示范带动相结合，针对低分维度开展专项改进，同时总结高分学校经验，推动区域整体数据文化水平持续提升。"
