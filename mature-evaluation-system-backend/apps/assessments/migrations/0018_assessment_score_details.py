from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('assessments', '0017_behaviorassessment_public_account_post_count_and_more')]
    operations = [migrations.AddField(
        model_name='assessment', name='score_details',
        field=models.JSONField('评分明细快照', default=dict, blank=True),
    )]
