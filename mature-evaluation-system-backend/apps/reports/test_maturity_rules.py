from decimal import Decimal
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import patch

from django.apps import apps
from django.db import connection
from django.test import SimpleTestCase, TestCase

from apps.accounts.models import User
from apps.assessments.maturity import determine_maturity_level
from apps.assessments.models import Assessment
from apps.assessments.scoring_service import ScoringService
from apps.assessments import scoring_config
from apps.schools.models import School
from .report_ai_service import ReportAIService
from .report_data_service import ReportDataService
from .statistics import region_ai_payload, region_for_school, region_statistics


class MaturityBoundaryTests(SimpleTestCase):
    def test_boundaries_and_invalid_scores(self):
        cases = [
            (0, 'initial'), ('1.4999', 'initial'), (1.5, 'growing'),
            ('2.9999', 'growing'), (3, 'mature'), ('3.9999', 'mature'),
            (4, 'leading'), (5, 'leading'),
        ]
        service = ScoringService.__new__(ScoringService)
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(determine_maturity_level(value), expected)
                self.assertEqual(service.determine_maturity_level(Decimal(str(value))), expected)
        for value in [None, '', True, -0.0001, 5.0001, 'NaN', 'Infinity', 'invalid']:
            with self.subTest(value=value):
                self.assertEqual(determine_maturity_level(value), '')

    def test_classification_uses_the_persisted_four_decimal_score(self):
        service = ScoringService(SimpleNamespace(id=1, school=None), read_only=True)
        methods = {f'calculate_{key}_score': lambda: 1.49999
                   for key in ['literacy', 'institution', 'behavior', 'asset', 'technology']}
        with patch.multiple(service, **methods), patch.dict(
            scoring_config.DIMENSION_WEIGHTS, {key: 0.2 for key in 'ABCDE'}, clear=True
        ):
            scores = service.calculate_all_scores()
        self.assertEqual(scores['total_score'], Decimal('1.5000'))
        self.assertEqual(scores['maturity_level'], 'growing')

    def test_advice_uses_the_same_boundaries(self):
        service = ReportAIService(initialize_llm=False)
        for value, label in [(0, '有待提升'), (1.5, '比较良好'), (3, '较为优秀'), (4, '非常优秀'), (5, '非常优秀')]:
            with self.subTest(value=value):
                self.assertEqual(service._performance_label(value), label)


class StoredMaturityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('maturity-test', 'maturity@test.local', role='school')
        cls.school = School.objects.create(user=user, name='边界测试学校', school_type='primary',
                                          province='测试省', city='测试市', district='测试区')

    def test_data_migration_reclassifies_without_rescoring(self):
        values = [None, -1, 0, 1.4999, 1.5, 2.9999, 3, 3.9999, 4, 5, 6]
        records = [Assessment.objects.create(
            school=self.school, total_score=value, maturity_level='initial',
            score_details={'version': 1, 'secondary_scores': {'A1': 2}},
            ai_suggestions={'overall': '旧规则建议'}, report_file='reports/old.pdf',
        ) for value in values]
        migration = import_module('apps.assessments.migrations.0019_unify_maturity_intervals')
        with connection.schema_editor(atomic=False) as editor:
            migration.reclassify_assessments(apps, editor)
        for old in records:
            new = Assessment.objects.get(pk=old.pk)
            self.assertEqual(new.maturity_level, determine_maturity_level(old.total_score))
            self.assertEqual(new.total_score, Decimal(str(old.total_score)) if old.total_score is not None else None)
            self.assertEqual(new.score_details, old.score_details)
            self.assertEqual(new.updated_at, old.updated_at)
            self.assertEqual(new.ai_suggestions, {})
            self.assertFalse(new.report_file)

    def test_school_and_region_reports_classify_a_stale_saved_level_from_score(self):
        assessment = Assessment.objects.create(
            school=self.school, status='completed', total_score=3, maturity_level='growing',
            score_details={'version': 1, 'secondary_scores': {}},
        )
        self.assertEqual(ReportDataService(assessment).get_maturity_level_display(), '成熟级')
        report = region_statistics(region_for_school(self.school))
        self.assertEqual(report['assessments'][0]['maturity_level'], 'mature')
        levels = region_ai_payload(report)['level_distribution']
        self.assertEqual([level['count'] for level in levels], [0, 0, 1, 0])
