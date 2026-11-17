"""Reclassify stored scores and invalidate report text generated under the old boundaries."""
import json

from django.db import migrations, models


def reclassify_assessments(apps, schema_editor):
    assessment = apps.get_model('assessments', 'Assessment')
    database = schema_editor.connection.alias
    # Keep these rules frozen so replaying this migration always produces the same result.
    assessment.objects.using(database).update(
        maturity_level=models.Case(
            models.When(total_score__gte=0, total_score__lt=1.5, then=models.Value('initial')),
            models.When(total_score__gte=1.5, total_score__lt=3, then=models.Value('growing')),
            models.When(total_score__gte=3, total_score__lt=4, then=models.Value('mature')),
            models.When(total_score__gte=4, total_score__lte=5, then=models.Value('leading')),
            default=models.Value(''), output_field=models.CharField(),
        ),
        ai_suggestions={},
        report_file='',
    )
    config = apps.get_model('admin_panel', 'SystemConfig')
    config.objects.using(database).update_or_create(
        config_key='maturity_levels',
        defaults={
            'config_type': 'json',
            'config_value': json.dumps([
                {'level': 'initial', 'name': '初始级', 'min': 0.0, 'max': 1.5, 'range': '[0.0, 1.5)'},
                {'level': 'growing', 'name': '成长级', 'min': 1.5, 'max': 3.0, 'range': '[1.5, 3.0)'},
                {'level': 'mature', 'name': '成熟级', 'min': 3.0, 'max': 4.0, 'range': '[3.0, 4.0)'},
                {'level': 'leading', 'name': '创新级', 'min': 4.0, 'max': 5.0, 'range': '[4.0, 5.0]'},
            ], ensure_ascii=False),
            'description': '成熟度等级划分标准，左闭右开，创新级包含5分',
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('assessments', '0018_assessment_score_details'),
        ('admin_panel', '0003_alter_systemconfig_options_systemconfig_is_active_and_more'),
    ]
    operations = [migrations.RunPython(reclassify_assessments, atomic=True)]
