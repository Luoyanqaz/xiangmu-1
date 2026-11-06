from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.assessments.models import Assessment, InstitutionAssessment
from apps.assessments.scoring_service import ScoringService
from apps.regions.models import Region, RegionReportSuggestionCache
from apps.regions.region_report_ai_service import RegionReportAIService
from apps.schools.models import School
from .statistics import (DIMENSIONS, SECONDARY_KEYS, describe_scores, latest_completed,
                         region_for_school, region_statistics, school_rankings, score_details)


class ReportStatisticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user('admin', 'admin@test.local', 'test-password', role='admin')
        cls.region_user = User.objects.create_user('region', 'region@test.local', 'test-password', role='region_admin')
        cls.region = Region.objects.create(code='test-one', name='一区', province='测试省', city='测试市', region_admin=cls.region_user)
        cls.other_region = Region.objects.create(code='test-two', name='二区', province='测试省', city='测试市')
        cls.school = cls.make_school('本校', 'primary', cls.region)
        cls.peer = cls.make_school('同类同区', 'primary', cls.region)
        cls.junior = cls.make_school('同区初中', 'junior', cls.region)
        cls.national = cls.make_school('全国同类', 'primary', cls.other_region)
        cls.target = cls.assessment(cls.school, 3, secondary=3)
        cls.old_peer = cls.assessment(cls.peer, 5, days=4, secondary=5)
        cls.peer_latest = cls.assessment(cls.peer, 3, secondary=3)
        cls.assessment(cls.peer, 5, status='draft', days=-1)
        cls.junior_report = cls.assessment(cls.junior, 4, secondary=4)
        cls.national_report = cls.assessment(cls.national, 5, secondary=5)

    @classmethod
    def make_school(cls, name, school_type, region=None):
        index = User.objects.count()
        user = User.objects.create_user(f'school-{index}', f'school-{index}@test.local', 'test-password')
        return School.objects.create(user=user, name=name, school_type=school_type, region=region,
                                     province=region.province if region else '', city=region.city if region else '',
                                     district=region.name if region else '', contact_email=user.email)

    @classmethod
    def assessment(cls, school, score, days=0, status='completed', secondary=None):
        fields = {key + '_score': score for key, _, _ in DIMENSIONS}
        snapshot = {} if secondary is None else {
            'version': 1, 'secondary_scores': {key: secondary for key in SECONDARY_KEYS}, 'observation_scores': {}}
        return Assessment.objects.create(school=school, status=status, total_score=score,
                                         maturity_level='mature', completed_at=timezone.now() - timedelta(days=days),
                                         score_details=snapshot, **fields)

    def test_same_type_is_limited_to_region_and_preserves_competition_rank(self):
        ranks = school_rankings(self.target)
        self.assertIn('同类型位次：平台内同区域内的同类型学校', ranks['scope_note'])
        for metric in ['total', 'literacy', 'institution', 'behavior', 'asset', 'technology']:
            self.assertEqual(ranks[metric]['same_type'], {'rank': 1, 'total': 2})
            self.assertEqual(ranks[metric]['region'], {'rank': 2, 'total': 3})
        # The peer is tied, so a zero-scoring school has rank 4, not 3.
        zero = self.assessment(self.make_school('零分', 'primary', self.region), 0, secondary=0)
        self.assertEqual(school_rankings(zero)['total']['region'], {'rank': 4, 'total': 4})
        self.assertEqual(school_rankings(zero)['total']['same_type'], {'rank': 3, 'total': 3})

    def test_latest_completed_excludes_newer_draft_and_old_report(self):
        ids = set(latest_completed().values_list('id', flat=True))
        self.assertIn(self.peer_latest.id, ids)
        self.assertNotIn(self.old_peer.id, ids)
        ranks = school_rankings(self.old_peer)
        self.assertFalse(ranks['available'])
        self.assertIsNone(ranks['total']['region']['rank'])

    def test_equal_completion_timestamp_uses_highest_id(self):
        newer = self.assessment(self.school, 2)
        Assessment.objects.filter(pk=newer.pk).update(completed_at=self.target.completed_at)
        self.assertEqual(latest_completed().get(school=self.school).id, newer.id)

    def test_null_invalid_and_zero_have_distinct_meanings(self):
        stats = describe_scores([0, 2, 4, None, 100, 'NaN'])
        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['missing_count'], 3)
        self.assertEqual(stats['average'], 2)
        self.assertEqual(stats['minimum'], 0)
        self.assertAlmostEqual(stats['std_dev'], 1.6330)
        self.assertEqual(describe_scores([0])['std_dev'], 0)
        self.assertIsNone(describe_scores([])['average'])
        self.peer_latest.literacy_score = None
        self.peer_latest.save(update_fields=['literacy_score'])
        ranks = school_rankings(self.target)
        self.assertEqual(ranks['literacy']['same_type'], {'rank': 1, 'total': 1})
        self.assertEqual(ranks['total']['same_type']['total'], 2)

    def test_school_with_unknown_region_has_neither_rank(self):
        target = self.assessment(self.make_school('未绑定', 'primary'), 2)
        ranks = school_rankings(target)
        for metric in ['total', 'literacy', 'institution', 'behavior', 'asset', 'technology']:
            self.assertEqual(ranks[metric]['same_type'], {'rank': None, 'total': 0})
            self.assertEqual(ranks[metric]['region'], {'rank': None, 'total': 0})

    def test_same_type_region_uses_binding_or_complete_legacy_location(self):
        legacy = self.make_school('未绑定但地址完整', 'primary', self.region)
        legacy.region = None
        legacy.save(update_fields=['region'])
        self.assessment(legacy, 5, secondary=5)
        other_province = self.make_school('同名区县不同省', 'primary', self.region)
        other_province.region = None
        other_province.province = '其他省'
        other_province.save(update_fields=['region', 'province'])
        self.assessment(other_province, 5, secondary=5)
        # An explicit region binding takes precedence over legacy location text.
        self.national.district = self.region.name
        self.national.save(update_fields=['district'])
        ranks = school_rankings(self.target)
        self.assertEqual(ranks['total']['same_type'], {'rank': 2, 'total': 3})
        self.assertEqual(ranks['total']['region'], {'rank': 3, 'total': 4})
        legacy_rank = school_rankings(latest_completed().get(school=legacy))
        self.assertEqual(legacy_rank['total']['same_type'], {'rank': 1, 'total': 3})

    def test_region_statistics_uses_same_latest_cohort_and_snapshots(self):
        with patch.object(ScoringService, 'calculate_all_scores', side_effect=AssertionError('Snapshot should not recalculate')):
            report = region_statistics(region_for_school(self.school))
        self.assertEqual(report['summary']['completed_school_count'], 3)
        self.assertEqual(len(report['dimension_statistics']), 5)
        self.assertEqual(sum(len(row['secondary_indicators']) for row in report['dimension_statistics']), 11)
        row = report['dimension_statistics'][0]
        self.assertEqual(row['maximum'], 4)
        self.assertEqual(row['minimum'], 3)
        self.assertAlmostEqual(row['average'], 3.3333)
        self.assertAlmostEqual(row['std_dev'], 0.4714)
        self.assertEqual(row['secondary_indicators'][0]['average'], row['average'])
        self.assertEqual([item['rank'] for item in row['top_schools']], [1, 2, 2])

    def test_empty_and_single_school_regions(self):
        region = {'id': None, 'province': '无', 'city': '无', 'name': '无'}
        empty = region_statistics(region)
        self.assertEqual(empty['summary']['completed_school_count'], 0)
        self.assertTrue(all(row['average'] is None for row in empty['dimension_statistics']))
        single = region_statistics(region_for_school(self.national))
        self.assertEqual(single['dimension_statistics'][0]['std_dev'], 0)

    def test_legacy_document_quality_is_missing_without_llm_or_database_writes(self):
        InstitutionAssessment.objects.create(assessment=self.target, management_doc_status='clear_required',
            management_doc_count=1, management_doc_files=[{'path': 'never-read.pdf'}], management_doc_analysis='旧分析')
        self.target.score_details = {}
        self.target.save(update_fields=['score_details'])
        with patch('apps.assessments.llm_service.LLMService._call_api', side_effect=AssertionError('No LLM during statistics')):
            details = score_details(self.target)
        self.assertNotIn('B3', details['secondary_scores'])
        self.target.refresh_from_db()
        self.assertEqual(self.target.score_details, {})
        self.assertEqual(self.target.total_score, Decimal('3'))
        self.assertEqual(self.target.institution.management_doc_analysis, '旧分析')

    def test_new_scoring_captures_secondary_snapshot(self):
        fresh = self.assessment(self.school, None, status='draft')
        service = ScoringService(fresh)
        service.calculate_all_scores()
        fresh.save(update_fields=['score_details'])
        fresh.refresh_from_db()
        self.assertEqual(fresh.score_details['version'], 1)
        self.assertEqual(set(fresh.score_details['secondary_scores']), set(SECONDARY_KEYS))

    def test_statistics_endpoint_access_and_scope(self):
        client = APIClient()
        path = '/api/region-admin/region-report/statistics/'
        self.assertEqual(client.get(path).status_code, 401)
        client.force_authenticate(self.school.user)
        self.assertEqual(client.get(path).status_code, 403)
        client.force_authenticate(self.region_user)
        response = client.get(path, {'region_id': self.other_region.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['region']['id'], self.region.id)
        client.force_authenticate(self.admin)
        self.assertEqual(client.get('/api/admin/region-report/statistics/').status_code, 400)
        response = client.get('/api/admin/region-report/statistics/', {'region_id': self.other_region.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['summary']['completed_school_count'], 1)

    def test_ai_uses_server_statistics_and_cache_includes_secondary_scores(self):
        client = APIClient()
        client.force_authenticate(self.region_user)
        path = '/api/region-admin/region-report/ai-suggestions/'
        self.assertEqual(client.post(path, {'region': {'id': self.other_region.id}}, format='json').status_code, 403)
        fake = {'development': {'items': []}, 'dimension_suggestions': {'literacy': '测试建议'}}
        with patch.object(RegionReportAIService, 'generate_all_suggestions', return_value=fake) as generate:
            payload = {'region': {'id': self.region.id}, 'dimension_average': {'literacy': 999}}
            first = client.post(path, payload, format='json')
            self.assertEqual(first.status_code, 200)
            self.assertAlmostEqual(generate.call_args.args[0]['dimension_average']['literacy'], 3.3333)
            self.assertTrue(client.post(path, payload, format='json').data['cache_hit'])
            self.target.score_details['secondary_scores']['A1'] = 1
            self.target.save(update_fields=['score_details'])
            self.assertFalse(client.post(path, payload, format='json').data['cache_hit'])
            self.assertEqual(generate.call_count, 2)
        self.assertEqual(RegionReportSuggestionCache.objects.count(), 1)

    def test_fallback_suggestions_include_actual_statistics(self):
        from .statistics import region_ai_payload
        payload = region_ai_payload(region_statistics(region_for_school(self.school)))
        service = RegionReportAIService()
        with patch.object(service.llm_service, '_call_api', side_effect=RuntimeError('offline')):
            result = service.generate_all_suggestions(payload)
        self.assertEqual(result['suggestion_mode'], 'fallback')
        self.assertEqual(len(result['dimension_suggestions']), 5)
        self.assertIn('总体标准差0.47', result['dimension_suggestions']['literacy'])
        self.assertIn('教师数据素养', result['dimension_suggestions']['literacy'])

    def test_school_report_endpoints_return_rankings_without_rescoring(self):
        client = APIClient()
        client.force_authenticate(self.school.user)
        with patch.object(ScoringService, 'calculate_all_scores', side_effect=AssertionError('Must not rescore')):
            for suffix in ['data', 'report-detail']:
                response = client.get(f'/api/assessments/{self.target.id}/{suffix}/')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['rankings']['total']['same_type'], {'rank': 1, 'total': 2})
                self.assertEqual(float(response.data['dimension_scores']['literacy']), 3)
        client.force_authenticate(self.region_user)
        self.assertEqual(client.get(f'/api/assessments/{self.national_report.id}/report-detail/').status_code, 403)

    def test_zero_report_is_not_recalculated(self):
        zero = self.assessment(self.school, 0, secondary=0)
        client = APIClient()
        client.force_authenticate(self.school.user)
        with patch.object(ScoringService, 'calculate_all_scores', side_effect=AssertionError('Zero is a valid score')):
            response = client.get(f'/api/assessments/{zero.id}/report-detail/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_score'], 0)
