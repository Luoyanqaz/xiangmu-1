"""Read-only reports for one school type within an explicitly selected district."""
from django.utils import timezone

from apps.schools.models import School
from apps.assessments.maturity import MATURITY_LEVELS, MATURITY_LABELS, determine_maturity_level
from .statistics import (DIMENSIONS, describe_scores, latest_completed, score_details,
                         schools_in_region, valid_score)


def ranking_groups(rows):
    """List sequence numbers are not competition ranks; ties use name then school ID."""
    descending = sorted(rows, key=lambda row: (-row['score'], row['school_name'], row['school_id']))
    if len(rows) <= 10:
        return {'display_mode': 'full', 'schools': descending, 'top_schools': [], 'bottom_schools': []}
    ascending = sorted(rows, key=lambda row: (row['score'], row['school_name'], row['school_id']))
    top = descending[:5]
    # Do not repeat a school across the two lists, even when every score is equal.
    top_ids = {row['school_id'] for row in top}
    bottom = [row for row in ascending if row['school_id'] not in top_ids][:5]
    return {'display_mode': 'top_bottom', 'schools': [], 'top_schools': top, 'bottom_schools': bottom}


def school_type_statistics(region, school_type):
    schools = schools_in_region(region).filter(school_type=school_type)
    assessments = list(latest_completed().filter(school__in=schools)
                       .select_related('school', 'institution', 'behavior', 'asset', 'technology')
                       .order_by('school_id'))
    details = {item.id: score_details(item) for item in assessments}
    rows = []
    for item in assessments:
        score = valid_score(item.total_score)
        if score is None:
            continue
        key = determine_maturity_level(score)
        rows.append({'assessment_id': item.id, 'school_id': item.school_id,
                     'school_name': item.school.name, 'score': float(score),
                     'maturity_level': key, 'maturity_label': MATURITY_LABELS[key]})
    levels = []
    for level in MATURITY_LEVELS:
        key = level['level']
        members = [row for row in rows if row['maturity_level'] == key]
        levels.append({'key': key, 'label': level['name'], 'score_range': level['range'],
                       'ratio': round(len(members) / len(rows) * 100, 1) if rows else 0,
                       **describe_scores([row['score'] for row in members]), **ranking_groups(members)})

    dimensions = []
    for key, label, children in DIMENSIONS:
        secondary = []
        for code, name in children:
            values = [details[item.id].get('secondary_scores', {}).get(code) for item in assessments]
            secondary.append({'key': code, 'label': name, **describe_scores(values)})
        if key == 'literacy':
            # Manager literacy is not an indicator in the current scoring configuration.
            # Keep the requested reference row without reusing the student A2 score.
            secondary.insert(1, {'key': 'manager_literacy', 'label': '管理者数据素养',
                                 **describe_scores([None] * len(assessments)),
                                 'unavailable_reason': '现行评分体系未设置该项得分，暂不统计。'})
        dimensions.append({'key': key, 'label': label,
                           **describe_scores([getattr(item, key + '_score') for item in assessments]),
                           'secondary_indicators': secondary})
    total = describe_scores([item.total_score for item in assessments])
    return {
        'region': region, 'school_type': school_type,
        'school_type_label': dict(School.SCHOOL_TYPE_CHOICES)[school_type],
        'generated_at': timezone.localtime().isoformat(),
        'scope_note': '统计范围为所选区域内的同类型学校，每校取最近一次已完成评估；'
                      '总分排序按得分排列，同分按学校名称升序、同名按学校编号排序，列表数字为序号。'
                      '不足11所时展示完整名单，达到11所时展示前后5所且名单不重复。'
                      '各等级占比以有效总分学校数为分母，等级按总分区间划分。'
                      '均值与总体标准差按学校得分计算，0分正常计入，缺失及超出0—5范围的值不计入；'
                      '单校标准差为0，无有效数据时显示“—”。',
        'secondary_note': '二级指标采用评分明细快照；历史记录仅重建可确定得分，缺少材料质量原始分的'
                          '“数据管理文件”不以估算值补齐。管理者数据素养尚未纳入现行评分体系，显示“—”。',
        'legacy_assessment_count': sum(detail.get('version') != 1 for detail in details.values()),
        'summary': {'school_count': schools.count(), 'completed_school_count': len(assessments), **total},
        'total_ranking': ranking_groups(rows), 'levels': levels, 'dimensions': dimensions,
    }
