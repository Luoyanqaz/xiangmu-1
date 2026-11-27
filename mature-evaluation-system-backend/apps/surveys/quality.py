"""按评估轮次区分历史口径与有效问卷口径。"""
import time
import uuid

from django.core import signing
from django.db.models import Count, Q

from .models import SurveyResponse

ROLES = ('teacher', 'student')
ATTENTION = 'attention'
SALT = 'surveys.displayed-questions.v1'
MIN_MS_PER_QUESTION = 1250


def scored_responses(instance, assessment):
    rows = instance.responses.all()
    return rows.filter(is_valid=True) if assessment.check_survey_quality else rows


def issue_attempt(instance, questions):
    return signing.dumps({
        'link': str(instance.uuid), 'id': str(uuid.uuid4()),
        'start_ms': time.time_ns() // 1_000_000, 'count': len(questions),
        'required': ['q' + str(q['order']) for q in questions if q['is_required']],
    }, salt=SALT, compress=True)


def evaluate(attempt, answers, elapsed_ms):
    duration = max(0, min(elapsed_ms, time.time_ns() // 1_000_000 - attempt['start_ms']))
    reasons = []
    if answers.get('q' + ATTENTION) != '不符合':
        reasons.append('attention')
    if duration < MIN_MS_PER_QUESTION * attempt['count']:
        reasons.append('duration')
    return {'question_count': attempt['count'], 'duration_ms': duration, 'reasons': reasons}


def collection(assessment):
    if assessment.survey_snapshot is not None:
        return assessment.survey_snapshot
    counts = {role: {'received': 0, 'valid': 0 if assessment.check_survey_quality else None} for role in ROLES}
    rows = SurveyResponse.objects.filter(instance__assessment=assessment).values('instance__template__survey_type').annotate(
        received=Count('pk'), valid=Count('pk', filter=Q(is_valid=True)))
    for row in rows:
        role = row['instance__template__survey_type']
        if role in counts:
            counts[role]['received'] = row['received']
            if assessment.check_survey_quality:
                counts[role]['valid'] = row['valid']
    return counts


def regional_collection(assessments):
    totals = {role: {'received': 0, 'valid': 0, 'unjudged': 0} for role in ROLES}
    shortages = {'teacher': 0, 'student': 0, 'both': 0}
    for assessment in assessments:
        counts = collection(assessment)
        missing = []
        for role in ROLES:
            received, valid = counts[role]['received'], counts[role]['valid']
            totals[role]['received'] += received
            if valid is None:
                totals[role]['unjudged'] += received
            else:
                totals[role]['valid'] += valid
                if valid == 0:
                    missing.append(role)
        if missing:
            shortages['both' if len(missing) == 2 else missing[0]] += 1
    for counts in totals.values():
        counts['invalid'] = counts['received'] - counts['valid'] - counts['unjudged']
    return {**totals, 'shortages': shortages}
