from django.db import transaction

from apps.assessments.models import Assessment
from apps.surveys.quality import collection


def submit_round(assessment, task):
    # 与答卷提交锁定同一行，先写入的答卷才进入本轮快照。
    with transaction.atomic():
        current = Assessment.objects.select_for_update().get(pk=assessment.pk)
        if current.status != 'draft':
            return None
        current.survey_snapshot = collection(current)
        current.status = 'collecting'
        current.save(update_fields=['survey_snapshot', 'status', 'updated_at'])
    try:
        return task.delay(current.pk)
    except Exception:
        Assessment.objects.filter(pk=current.pk, status='collecting').update(status='draft', survey_snapshot=None)
        raise
