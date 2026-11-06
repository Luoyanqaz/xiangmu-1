"""Shared, read-only cohorts and report statistics (all scores use the 0–5 scale)."""
from decimal import Decimal, InvalidOperation
from statistics import mean, pstdev

from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce

from apps.assessments.models import Assessment
from apps.assessments.scoring_service import ScoringService
from apps.schools.models import School


DIMENSIONS = (
    ('literacy', '数据素养', (('A1', '教师数据素养'), ('A2', '学生数据素养'))),
    ('institution', '数据制度', (('B1', '数据组织机构'), ('B2', '数据人员配备'), ('B3', '数据管理文件'))),
    ('behavior', '数据行为', (('C1', '数据行为监测'), ('C2', '数据应用成效'))),
    ('asset', '数据资产', (('D1', '数据资产意识'), ('D2', '数据资产积累'))),
    ('technology', '数据技术', (('E1', '数据基础设施'), ('E2', '数据安保水平'))),
)
METRICS = ('total',) + tuple(key for key, _, _ in DIMENSIONS)
SECONDARY_KEYS = tuple(code for _, _, children in DIMENSIONS for code, _ in children)
STATISTICS_NOTE = (
    '每所学校仅计入最近一次已完成评估（完成时间相同取记录编号较大者）；'
    '得分为0—5分，空值及超出范围的值不计入该指标，0分正常计入；'
    '标准差为总体标准差，单校为0，无有效数据时显示“—”；同分并列位次（1、1、3）。'
)


def valid_score(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
        return number if number.is_finite() and 0 <= number <= 5 else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def latest_completed():
    latest = (Assessment.objects.filter(school_id=OuterRef('school_id'), status='completed')
              .order_by(Coalesce('completed_at', 'created_at').desc(), '-id').values('id')[:1])
    return Assessment.objects.filter(status='completed', pk=Subquery(latest))


def schools_in_region(region):
    """Prefer the authoritative FK; include legacy unbound schools only by complete location."""
    criteria = Q(pk__in=[])
    if region.get('id'):
        criteria |= Q(region_id=region['id'])
    if all(region.get(key) for key in ('province', 'city', 'name')):
        criteria |= Q(region__isnull=True, province=region['province'], city=region['city'], district=region['name'])
        if not region.get('id'):
            criteria |= Q(region__province=region['province'], region__city=region['city'], region__name=region['name'])
    return School.objects.filter(criteria)


def region_for_school(school):
    if school.region_id:
        region = school.region
        return {'id': region.id, 'code': region.code, 'province': region.province,
                'city': region.city, 'name': region.name}
    return {'id': None, 'province': school.province, 'city': school.city, 'name': school.district}


def school_rankings(assessment):
    school = assessment.school
    all_latest = latest_completed()
    eligible = assessment.status == 'completed' and all_latest.filter(pk=assessment.pk).exists()
    region = region_for_school(school)
    region_known = bool(region.get('id') or all(region.get(key) for key in ('province', 'city', 'name')))
    regional_latest = all_latest.filter(school__in=schools_in_region(region)) if region_known else all_latest.none()
    cohorts = {
        'same_type': regional_latest.filter(school__school_type=school.school_type) if school.school_type else all_latest.none(),
        'region': regional_latest,
    }
    output = {
        'scope_note': '同类型位次：平台内同区域内的同类型学校；区域位次：所属区县全部学校。' + STATISTICS_NOTE,
        'available': eligible,
        'unavailable_reason': '' if eligible else '仅最新一次已完成评估参与当前位次；历史或未完成报告不参与。',
    }
    for metric in METRICS:
        output[metric] = {}
    for scope, queryset in cohorts.items():
        aggregates = {}
        for metric in METRICS:
            field = metric + '_score'
            score = valid_score(getattr(assessment, field))
            valid = Q(**{field + '__gte': 0, field + '__lte': 5})
            aggregates[metric + '_count'] = Count('id', filter=valid)
            aggregates[metric + '_above'] = Count('id', filter=valid & Q(**{field + '__gt': score if score is not None else 5}))
        values = queryset.aggregate(**aggregates)
        for metric in METRICS:
            count = values[metric + '_count']
            score = valid_score(getattr(assessment, metric + '_score'))
            available = eligible and score is not None and count > 0
            output[metric][scope] = {'rank': values[metric + '_above'] + 1 if available else None, 'total': count}
    return output


def score_details(assessment):
    snapshot = assessment.score_details or {}
    if snapshot.get('version') == 1:
        return snapshot
    # Reconstruct deterministic legacy indicators only. Reading a report must not score documents.
    scoring = ScoringService(assessment, read_only=True)
    scoring.calculate_all_scores()
    secondary = dict(scoring.secondary_scores)
    observations = dict(scoring.observation_scores)
    if scoring.unavailable_points:
        secondary.pop('B3', None)
        for key in scoring.unavailable_points:
            observations.pop(key, None)
    return {'version': 0, 'secondary_scores': secondary, 'observation_scores': observations}


def describe_scores(values):
    scores = [float(score) for value in values if (score := valid_score(value)) is not None]
    return {
        'count': len(scores), 'missing_count': len(values) - len(scores),
        'average': round(mean(scores), 4) if scores else None,
        'maximum': max(scores) if scores else None,
        'minimum': min(scores) if scores else None,
        'std_dev': round(pstdev(scores), 4) if scores else None,
    }


def description(label, stats):
    if not stats['count']:
        return f'{label}暂无有效得分，暂不作统计判断。'
    return (f"{label}共有{stats['count']}所学校具备有效得分，平均分为{stats['average']:.2f}分，"
            f"最高分为{stats['maximum']:.2f}分，最低分为{stats['minimum']:.2f}分，"
            f"总体标准差为{stats['std_dev']:.2f}分。")


def ranked_schools(assessments, field):
    valid = [(item, valid_score(getattr(item, field))) for item in assessments]
    valid = [(item, score) for item, score in valid if score is not None]
    valid.sort(key=lambda pair: (-pair[1], pair[0].school_id))
    rows, previous, rank = [], None, 0
    for index, (item, score) in enumerate(valid, 1):
        if score != previous:
            rank = index
        rows.append({'assessment_id': item.id, 'school_id': item.school_id,
                     'school_name': item.school.name, 'score': float(score), 'rank': rank})
        previous = score
    return rows


def region_statistics(region):
    schools = schools_in_region(region)
    assessments = list(latest_completed().filter(school__in=schools)
                       .select_related('school', 'institution', 'behavior', 'asset', 'technology')
                       .order_by('school_id'))
    details = {item.id: score_details(item) for item in assessments}
    dimensions = []
    for key, label, children in DIMENSIONS:
        stats = describe_scores([getattr(item, key + '_score') for item in assessments])
        ranked = ranked_schools(assessments, key + '_score')
        secondary = []
        for code, name in children:
            child = describe_scores([details[item.id].get('secondary_scores', {}).get(code) for item in assessments])
            secondary.append({'key': code, 'label': name, **child, 'description': description(name, child)})
        dimensions.append({
            'key': key, 'label': label, **stats, 'description': description(label, stats),
            'highest_schools': [row['school_name'] for row in ranked if row['score'] == stats['maximum']],
            'lowest_schools': [row['school_name'] for row in ranked if row['score'] == stats['minimum']],
            'top_schools': ranked[:5], 'bottom_schools': ranked[-5:], 'secondary_indicators': secondary,
        })
    total = describe_scores([item.total_score for item in assessments])
    return {
        'region': region, 'statistics_note': STATISTICS_NOTE,
        'secondary_note': '新评估采用评分时保存的明细。历史记录按现有填报重建可计算指标；缺少材料质量原始分的“数据管理文件”不计入统计，未使用估算分补齐。',
        'legacy_assessment_count': sum(detail.get('version') != 1 for detail in details.values()),
        'summary': {'school_count': schools.count(), 'completed_school_count': len(assessments),
                    'assessment_count': len(assessments), 'avg_score': total['average'],
                    'highest_score': total['maximum'], 'lowest_score': total['minimum']},
        'dimension_statistics': dimensions,
        'dimension_average': {row['key']: row['average'] for row in dimensions},
        'assessments': [{
            'id': item.id, 'status': item.status, 'maturity_level': item.maturity_level,
            'school': {'id': item.school_id, 'name': item.school.name, 'school_type': item.school.school_type},
            'scores': {metric + '_score': float(value) if (value := valid_score(getattr(item, metric + '_score'))) is not None else None for metric in METRICS},
            'times': {'created_at': item.created_at.isoformat(), 'completed_at': item.completed_at.isoformat() if item.completed_at else None},
        } for item in assessments],
    }


def region_ai_payload(statistics):
    """Rebuild AI inputs from authorized database results, never browser-provided scores."""
    levels = []
    rows = statistics['assessments']
    for key, label in [('initial', '初始级'), ('growing', '成长级'), ('mature', '成熟级'), ('leading', '创新级')]:
        group = [item for item in rows if item['maturity_level'] == key]
        stats = describe_scores([item['scores']['total_score'] for item in group])
        levels.append({'key': key, 'label': label, 'count': len(group),
                       'ratio': len(group) / len(rows) * 100 if rows else 0,
                       'avg_score': stats['average'],
                       'dimension_average': {dim: describe_scores([item['scores'][dim + '_score'] for item in group])['average']
                                             for dim, _, _ in DIMENSIONS}})
    return {'region': statistics['region'], 'summary': statistics['summary'],
            'dimension_average': statistics['dimension_average'],
            'dimension_statistics': statistics['dimension_statistics'],
            'level_distribution': levels, 'level_analysis': levels,
            'statistics_note': statistics['statistics_note'],
            '_hash_base': statistics}
