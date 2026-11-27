"""按选定的学校或区域定稿生成报告，模型逐项补写观测点措施。"""
import json
import logging
import re
from pathlib import Path

from django.conf import settings

from apps.assessments.maturity import MATURITY_LABELS, determine_maturity_level
from .statistics import DIMENSIONS, REGIONAL_OBSERVATIONS, valid_score

VERSIONS = ('20261120', '20261124', '20261126', '20261127')
SOURCE = Path(__file__).parent / 'prompts'
logger = logging.getLogger(__name__)
BANDS = {'leading': '非常优秀', 'mature': '较为优秀', 'growing': '比较良好', 'initial': '有待提升'}
STAGES = {
    'initial': '数据文化建设基础较为薄弱，总体处于起步阶段',
    'growing': '已初步形成数据文化建设基础，总体处于逐步发展阶段',
    'mature': '数据文化建设总体较为成熟，处于巩固与优化阶段',
    'leading': '数据文化建设总体达到较高成熟水平，处于持续创新阶段',
}
# 同一观测点的行动主题，分别由校内岗位或区域主管部门落实。
ACTIONS = {
    'literacy': '组织师生数据素养分层研修', 'institution': '细化数据治理岗位分工与制度清单',
    'behavior': '建立数据应用记录与反馈机制', 'asset': '建立教育数据资源目录与更新制度',
    'technology': '梳理数字基础设施与安全保障需求',
    'B11': '明确数据工作小组成员和责任清单', 'B12': '建立工作例会和任务跟踪台账',
    'B21': '核定数据管理岗位并明确专兼职职责', 'B22': '安排数据管理人员专题研修',
    'B31': '完善数据采集、授权和共享制度', 'B32': '编制典型场景操作指南并组织试用',
    'C11': '将教学数据分析纳入教师集体备课', 'C12': '在学习任务中引导学生记录和解释数据',
    'C21': '遴选并整理可复用的数据应用案例', 'C22': '组织教育数据应用成果交流',
    'C23': '收集教师反馈并跟踪应用改进效果',
    'D11': '通过案例研讨识别教育数据价值', 'D12': '组织资源复用与分析实践',
    'D13': '培训资源归档、授权和共享规范', 'D21': '建立分类型资源清单并定期归集',
    'D22': '核查师生人均资源覆盖并完善资源供给',
    'E11': '盘点教学终端和数据硬件并制定更新计划', 'E12': '梳理平台功能并推进系统互通',
    'E21': '核查等保与认证要求并跟踪整改', 'E22': '建立风险事件台账并开展处置演练',
}
for prefix, who in [('A1', '教师'), ('A3', '学生')]:
    for index, action in enumerate(('识别真实情境中的数据问题', '掌握数据采集和分析工具',
                                    '评价数据质量并交流分析结果', '用数据解决实际问题',
                                    '练习隐私保护与合规使用'), 1):
        ACTIONS[f'{prefix}{index}'] = f'组织{who}{action}'

SCHOOL_ACTORS = dict(zip((row[0] for row in DIMENSIONS),
                         ('教研组', '校办', '教务处', '信息中心', '信息中心')))


def enabled():
    return settings.REPORT_ADVICE_VERSION in VERSIONS


def inputs(data, region):
    if region:
        rows = data.get('dimension_statistics', [])
        dimensions = {r['key']: r.get('average') for r in rows}
        secondary = {g['key']: g.get('average') for r in rows for g in r['secondary_indicators']}
        observations = {p['key']: p.get('average') for r in rows for g in r['secondary_indicators']
                        for p in g.get('observation_indicators', [])}
        return data['summary'].get('avg_score'), dimensions, secondary, observations
    return (data.get('total_score'), data.get('dimension_scores', {}),
            data.get('secondary_scores', {}), data.get('observation_scores', {}))


def classify(pairs, values):
    return [(key, name, valid_score(values.get(key))) for key, name in pairs]


def targets(rows, overall):
    low = sorted((row for row in rows if row[2] is not None and row[2] < 3), key=lambda r: r[2])
    if overall:
        return low[:2]
    return [row for row in low if row[2] == low[0][2]]


def describe_nov24(rows, *, mark_uniform_low=False):
    high, low = [], []
    for grade, band in BANDS.items():
        names = [name for _, name, score in rows if determine_maturity_level(score) == grade]
        if names:
            group = high if grade in ('leading', 'mature') else low
            group.append('、'.join(names) + ('均' if len(names) > 1 else '') + '表现' + band)
    parts = high + low
    if high and low:
        parts = high + ['但' + '，'.join(low) + '，仍有改进空间']
    missing = [name for _, name, score in rows if score is None]
    if mark_uniform_low and not missing and not high and len(low) == 1:
        parts[-1] += '，仍有改进空间'
    if missing:
        parts.append('、'.join(missing) + '暂无有效得分')
    return '，'.join(parts) + '。'


def summary_nov24(total, overall, region, *, version):
    subject = '该区域' if region else '该校'
    grade = determine_maturity_level(total)
    if grade:
        actor = '区域内参评学校' if region else '学校'
        if region and grade != 'growing':
            actor += '的'
        intro = f'{subject}数据文化得分为{total:.2f}分，成熟度等级为{MATURITY_LABELS[grade]}。{actor}{STAGES[grade]}。'
    else:
        intro = f'{subject}暂无有效数据文化总分。'
    limit_to_three = version in ('20261126', '20261127')
    summary = intro + '其中，' + describe_nov24(overall, mark_uniform_low=limit_to_three)
    low = [row for row in overall if row[2] is not None and row[2] < 3]
    # 26 日按指标顺序选取；27 日优先最低分，同分沿用指标顺序。
    if version != '20261126':
        low.sort(key=lambda row: row[2])
    if limit_to_three:
        low = low[:3]
    if low:
        names = '、'.join(name for _, name, _ in low)
        if version == '20261127' or (region and version == '20261126'):
            names += '等方面'
        if region:
            return summary + f'当前短板主要集中在{names}，区域教育管理部门可依托实践基础较好的学校，围绕薄弱维度开展分类指导、组织跨校研修，推动高水平学校发挥示范作用。'
        return summary + f'建议优先围绕{names}制定专项改进计划，并按学期跟踪关键指标变化，为持续改进提供依据。'
    if all(score is not None for _, _, score in overall):
        if region:
            return summary + '建议区域教育管理部门支持学校立足各自优势开展数据应用创新，选取成效突出的做法在不同类型学校试行，明确其适用条件与实施要点，形成可供其他地区借鉴的实践模式。'
        return summary + '建议巩固各维度已有的建设成效，梳理校内行之有效的数据应用做法，促进经验共享，并按学期跟踪关键指标变化，为持续改进提供依据。'
    return summary


def describe(rows, selected, overall=False):
    clauses = []
    grades = [(grade, [row for row in rows if determine_maturity_level(row[2]) == grade]) for grade in BANDS]
    grades = [(grade, group) for grade, group in grades if group]
    for index, (grade, group) in enumerate(grades):
        focus = [row for row in group if row in selected]
        ordered = [row for row in group if row not in selected] + focus
        names = '、'.join(row[1] for row in ordered)
        phrase = names + ('均' if len(group) > 1 else '') + '表现' + BANDS[grade]
        if focus:
            if len(grades) > 1 and index == len(grades) - 1:
                phrase = '但' + phrase
            if len(focus) == len(group):
                refer = ''
            elif len(focus) == 1:
                refer = '其中最后一项'
            else:
                refer = f'其中后{len(focus)}项'
            if overall:
                phrase += '，' + refer + ('仍有待改善' if grade == 'initial' else '仍有改进空间') + '，列为优先改进维度'
            elif len(grades) > 1 or refer:
                phrase += '，' + refer + ('仍有待改善' if grade == 'initial' else '仍有改进空间')
        clauses.append(phrase)
    missing = [name for _, name, score in rows if score is None]
    if missing:
        clauses.append('、'.join(missing) + '暂无有效得分')
    return '，'.join(clauses) + '。'


def read_actions(response):
    """每行是独立的 JSON 对象；同时兼容模型一次返回完整对象。"""
    body = re.sub(r'^\x60\x60\x60(?:jsonl?|ndjson)?\s*|\s*\x60\x60\x60$', '', response.strip())
    try:
        obj = json.loads(body)
    except json.JSONDecodeError:
        obj = {}
        for line in body.splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                obj.update(row)
    return obj if isinstance(obj, dict) else {}


def join_actor_actions(selected, actors, actions):
    grouped = {}
    for code, _, _ in selected:
        grouped.setdefault(actors[code], []).append(actions[code])
    clauses = []
    for actor, steps in grouped.items():
        phrase = '，'.join(steps[:-1]) + '，并' + steps[-1] if len(steps) > 1 else steps[0]
        clauses.append(f'由{actor}{phrase}')
    return '；'.join(clauses)


def generate(data, llm, *, region=False):
    version = settings.REPORT_ADVICE_VERSION
    actor_actions = version in ('20261126', '20261127')
    revised = version == '20261124' or actor_actions
    scope = 'region' if region else 'school'
    subject = '该区域' if region else '该校'
    total, dims, secondary, obs = inputs(data, region)
    overall = classify([(key, name) for key, name, _ in DIMENSIONS], dims)
    groups = {'overall': overall}
    owners = {key: key for key, _, _ in DIMENSIONS}
    for key, _, children in DIMENSIONS:
        for child, _ in children:
            points = REGIONAL_OBSERVATIONS[child]
            pairs = [(code, cfg['name'].removeprefix('教师').removeprefix('学生')
                      if key in ('literacy', 'asset') else cfg['name']) for code, cfg in points.items()]
            if actor_actions and child == 'C2':
                pairs = [(code, '应用效果主观评价' if code == 'C23' else label) for code, label in pairs]
            groups[child] = classify(pairs, obs)
            owners.update(dict.fromkeys(points, key))
    if revised:
        # 11 月 24 日总评使用指定结语，模型只为低于 3 分的观测点写措施。
        selections = {key: [row for row in rows if row[2] is not None and row[2] < 3]
                      for key, rows in groups.items() if key != 'overall'}
    else:
        selections = {key: targets(rows, key == 'overall') for key, rows in groups.items()}
    actions = {}
    actors = {}
    for selected in selections.values():
        for code, _, _ in selected:
            if actor_actions:
                actors[code] = '区域教育管理部门' if region else SCHOOL_ACTORS[owners[code]]
                actions[code] = ('指导参评学校' if region else '') + ACTIONS[code]
            else:
                actions[code] = ('区域教育管理部门可指导参评学校' if region else
                                 f'由{SCHOOL_ACTORS[owners[code]]}') + ACTIONS[code]
    sources = dict.fromkeys(actions, 'fallback')
    if actions and llm and settings.LLM_ALLOW_NETWORK:
        brief = {key: [{'编号': code, '名称': name} for code, name, _ in selected]
                 for key, selected in selections.items() if selected}
        prompt = (SOURCE / version / f'{scope}.txt').read_text(encoding='utf-8') + '\n' + json.dumps({
            '对象': '区域' if region else '学校', '总分': total, '一级维度': dims, '二级指标': secondary,
            '观测点': obs, '本次选中的改进项': brief,
        }, ensure_ascii=False, default=str)
        if actor_actions:
            role = '区域教育管理部门或区域内的教研、技术支持机构' if region else '该校的校内部门或岗位'
            if version == '20261127':
                role += '，如区域教师发展中心、教育行政部门' if region else '，如教务处、学科教研组、年级组'
            prompt += (f'\n本次报告的实施主体须为{role}。程序负责得分、判档、总评和段落衔接。'
                       '仅为选中的每个观测点编号返回一行 JSON，例如 '
                       '{"E21":{"actor":"实施主体名称","action":"核验平台认证材料并登记整改事项"}}。'
                       'actor 仅填名称，不加“由”，同一主体使用一致的名称。action 从动词起笔，'
                       '结合对应观测点写具体场景中的措施，不重复主体、分值、表现或预期效果。'
                       '同一维度的正文约250字，措施用简明短句。')
        else:
            prompt += ('\n程序负责按上述定稿拼接所有得分、表现、分段和专项计划。'
                   '为每个选中的编号单独输出一行JSON，每行只有一对键值，例如 {"E21":"由信息中心核验认证材料"}。'
                   '只输出本次选中的编号，键必须逐字使用编号，'
                   '值为一句不超过50字的措施，不复述得分、档次和指标名称，不加“建议”前缀。'
                   + ('每条写明区域部门能采取的行动。' if region else '每条写明校内实施主体和可执行行动。'))
        if version == '20261124':
            prompt += '请用连贯自然的短句写明由谁在什么场景落实措施，同一维度的完整分析以约250字为宜。'
        try:
            parsed = read_actions(llm._call_api(prompt, max_tokens=max(2200, len(actions) * 110)))
            for code in actions:
                value = parsed.get(code)
                if actor_actions:
                    if not isinstance(value, dict) or not isinstance(value.get('actor'), str):
                        continue
                    actor = value['actor'].strip().removeprefix('由').strip()
                    if not actor or len(actor) > 30 or re.search(r'[\r\n。，；]', actor):
                        continue
                    value = value.get('action')
                if isinstance(value, str):
                    content = value.strip().rstrip('。').strip()
                    if actor_actions and ('\n' in content or '\r' in content):
                        continue
                    if content and len(value.strip()) <= 85 and not re.search(r'\d+(?:\.\d+)?\s*分', content):
                        actions[code] = content
                        sources[code] = 'ai'
                        if actor_actions:
                            actors[code] = actor
            failed = [code for code in sources if sources[code] == 'fallback']
            if failed:
                logger.warning('定稿建议逐项采用本地文案，编号：%s', ', '.join(failed))
        except Exception as exc:
            logger.warning('定稿建议使用本地规则：%s', type(exc).__name__)
    modes = set(sources.values())
    mode = 'mixed' if len(modes) > 1 else next(iter(modes), 'rules')

    def measures(selected):
        if actor_actions:
            return join_actor_actions(selected, actors, actions)
        return '，'.join(actions[code] for code, _, _ in selected)

    if revised:
        summary = summary_nov24(valid_score(total), overall, region, version=version)
    else:
        grade = determine_maturity_level(total)
        intro = (f'{subject}数据文化得分为{float(total):.2f}分，成熟度等级为{MATURITY_LABELS[grade]}。'
                 + ('区域内参评学校' if region else subject) + STAGES[grade] + '。'
                 if grade else f'{subject}暂无有效数据文化总分。')
        chosen = selections['overall']
        summary = intro + '其中，' + describe(overall, chosen, overall=True)
        if chosen:
            if region:
                summary += f'针对上述短板，建议{measures(chosen)}，并推动高水平学校发挥示范作用。'
            else:
                summary += f'建议围绕上述重点制定专项改进计划，{measures(chosen)}，并按学期跟踪关键指标变化。'
    result = {'overall': summary}
    for key, name, children in DIMENSIONS:
        value = valid_score(dims.get(key))
        paragraphs = [f'{subject}{name}得分为{value:.2f}分，整体表现{BANDS[determine_maturity_level(value)]}。'
                      if value is not None else f'{subject}{name}暂无有效得分。']
        for child, label in children:
            selected = selections[child]
            points = groups[child]
            text = label + '方面，' + (describe_nov24(points) if revised else describe(points, selected))
            if selected:
                text += '建议' + measures(selected) + '。'
            elif revised and all(score is not None and score >= 3 for _, _, score in points):
                text += ('可继续组织校际交流，推广已有做法。' if region else '可在日常工作中延续已有做法。')
            paragraphs.append(text)
        if actor_actions:
            result[key] = paragraphs[0] + '其中，' + ''.join(paragraphs[1:])
        else:
            result[key] = '\n'.join(paragraphs)
    return result, mode, sources
