from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.assessments.models import Assessment
from apps.assessments.scoring_service import ScoringService
from apps.regions.models import Region
from apps.schools.models import School
from .school_type_statistics import ranking_groups, school_type_statistics
from .statistics import DIMENSIONS, SECONDARY_KEYS, region_for_school


class SchoolTypeReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user('type-admin', 'type-admin@test.local', 'test', role='admin')
        cls.region_admin = User.objects.create_user('type-region', 'type-region@test.local', 'test', role='region_admin')
        cls.region = Region.objects.create(code='type-one', name='一区', province='测试省', city='测试市', region_admin=cls.region_admin)
        cls.other_region = Region.objects.create(code='type-two', name='二区', province='测试省', city='测试市')
        cls.first = cls.make_school('School B', cls.region)
        cls.second = cls.make_school('School A', cls.region)
        cls.junior = cls.make_school('Junior', cls.region, 'junior')
        cls.outside = cls.make_school('Outside', cls.other_region)
        cls.add_report(cls.first, 5, days=2)
        cls.current = cls.add_report(cls.first, 3)
        cls.add_report(cls.first, 5, status='draft', days=-1)
        cls.add_report(cls.second, 3)
        cls.add_report(cls.junior, 5)
        cls.add_report(cls.outside, 5)

    @classmethod
    def make_school(cls, name, region, school_type='primary'):
        index = User.objects.count()
        user = User.objects.create_user(f'type-school-{index}', f'type-school-{index}@test.local', 'test')
        return School.objects.create(user=user, name=name, school_type=school_type, region=region,
                                     province=region.province, city=region.city, district=region.name)

    @classmethod
    def add_report(cls, school, score, days=0, status='completed'):
        return Assessment.objects.create(school=school, status=status, total_score=score,
            completed_at=timezone.now() - timedelta(days=days), maturity_level='initial',
            score_details={'version': 1, 'secondary_scores': {key: score for key in SECONDARY_KEYS}},
            **{key + '_score': score for key, _, _ in DIMENSIONS})

    def report(self, school_type='primary'):
        return school_type_statistics(region_for_school(self.first), school_type)

    def test_only_platform_admin_can_access_options_and_statistics(self):
        client = APIClient()
        for endpoint in ['options', 'statistics']:
            path = f'/api/admin/school-type-report/{endpoint}/'
            params = {'region_id': self.region.id, 'school_type': 'primary'}
            self.assertEqual(client.get(path, params).status_code, 401)
            for user in [self.first.user, self.region_admin]:
                client.force_authenticate(user)
                self.assertEqual(client.get(path, params).status_code, 403)
            client.force_authenticate(self.admin)
            self.assertEqual(client.get(path, params).status_code, 200)
            client.force_authenticate(None)

    def test_region_and_type_are_required_and_validated(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        path = '/api/admin/school-type-report/statistics/'
        for params in [{}, {'region_id': self.region.id}, {'school_type': 'primary'},
                       {'region_id': self.region.id, 'school_type': 'invalid'},
                       {'region_id': 'invalid', 'school_type': 'primary'}]:
            self.assertEqual(client.get(path, params).status_code, 400)
        self.assertEqual(client.get(path, {'region_id': 999999, 'school_type': 'primary'}).status_code, 404)
        result = client.get(path, {'region_id': self.region.id, 'school_type': 'junior'}).data['data']
        self.assertEqual(result['summary']['count'], 1)
        self.assertEqual(result['total_ranking']['schools'][0]['school_id'], self.junior.id)

    def test_cohort_is_latest_completed_same_type_same_region_and_snapshot_only(self):
        with patch.object(ScoringService, 'calculate_all_scores', side_effect=AssertionError('Must use snapshots')):
            report = self.report()
        self.assertEqual(report['summary']['count'], 2)
        self.assertEqual(report['summary']['average'], 3)
        self.assertEqual(report['summary']['std_dev'], 0)
        rows = report['total_ranking']['schools']
        self.assertEqual([row['school_name'] for row in rows], ['School A', 'School B'])
        self.assertEqual(rows[1]['assessment_id'], self.current.id)
        self.assertEqual([level['count'] for level in report['levels']], [0, 0, 2, 0])
        self.assertEqual(report['levels'][2]['ratio'], 100)
        self.assertEqual(len(report['dimensions']), 5)
        children = report['dimensions'][0]['secondary_indicators']
        self.assertEqual([row['label'] for row in children], ['教师数据素养', '管理者数据素养', '学生数据素养'])
        self.assertEqual(children[0]['average'], 3)
        self.assertIsNone(children[1]['average'])
        self.assertEqual(children[1]['count'], 0)

    def test_empty_region_type_has_no_fabricated_scores(self):
        report = self.report('senior')
        self.assertEqual(report['summary']['school_count'], 0)
        self.assertEqual(report['summary']['count'], 0)
        self.assertIsNone(report['summary']['average'])
        self.assertEqual(report['total_ranking']['schools'], [])
        self.assertTrue(all(level['ratio'] == 0 for level in report['levels']))
        self.assertTrue(all(row['std_dev'] is None for row in report['dimensions']))

    def test_maturity_boundaries_use_inclusive_lower_bounds(self):
        values = [0, 1.5, 1.5001, 3, 3.0001, 4, 4.0001, 5]
        for index, value in enumerate(values):
            self.add_report(self.make_school(f'Boundary {index}', self.region, 'senior'), value)
        report = self.report('senior')
        self.assertEqual([level['count'] for level in report['levels']], [1, 2, 2, 3])
        self.assertEqual([level['ratio'] for level in report['levels']], [12.5, 25, 25, 37.5])
        self.assertEqual(report['summary']['minimum'], 0)
        self.assertEqual(report['levels'][0]['average'], 0)
        self.assertEqual(report['levels'][0]['std_dev'], 0)

    def test_null_and_invalid_totals_do_not_remove_valid_dimension_scores(self):
        Assessment.objects.filter(pk=self.current.pk).update(total_score=None, technology_score=0)
        invalid = self.make_school('Invalid', self.region)
        self.add_report(invalid, 6)
        report = self.report()
        self.assertEqual(report['summary']['completed_school_count'], 3)
        self.assertEqual(report['summary']['count'], 1)
        self.assertEqual(report['summary']['missing_count'], 2)
        self.assertEqual(report['levels'][2]['ratio'], 100)
        technology = report['dimensions'][-1]
        self.assertEqual(technology['count'], 2)
        self.assertEqual(technology['minimum'], 0)
        self.assertEqual(technology['average'], 1.5)
        self.assertEqual(technology['std_dev'], 1.5)

    def test_top_bottom_order_and_threshold_and_ties_do_not_repeat(self):
        rows = [{'school_id': index, 'school_name': f'School {index:02}', 'score': index / 10} for index in range(11)]
        self.assertEqual(ranking_groups(rows[:10])['display_mode'], 'full')
        groups = ranking_groups(rows)
        self.assertEqual([row['school_id'] for row in groups['top_schools']], [10, 9, 8, 7, 6])
        self.assertEqual([row['school_id'] for row in groups['bottom_schools']], [0, 1, 2, 3, 4])
        tied = ranking_groups([{**row, 'score': 3} for row in rows])
        names = [row['school_name'] for row in tied['top_schools'] + tied['bottom_schools']]
        self.assertEqual(len(set(names)), 10)
        self.assertEqual(names[:5], [f'School {index:02}' for index in range(5)])
        for index in range(11):
            self.add_report(self.make_school(f'Level {index:02}', self.region, 'senior'), 1)
        self.assertEqual(self.report('senior')['levels'][0]['display_mode'], 'top_bottom')

    def test_options_include_legacy_locations_and_stats_resolve_them(self):
        legacy = self.make_school('Legacy', self.region)
        legacy.region = None
        legacy.district = '历史区'
        legacy.save(update_fields=['region', 'district'])
        self.add_report(legacy, 2)
        client = APIClient()
        client.force_authenticate(self.admin)
        options = client.get('/api/admin/school-type-report/options/').data['data']
        self.assertEqual(len(options['school_types']), 5)
        self.assertTrue(any(row['name'] == '历史区' and row['id'] is None for row in options['regions']))
        report = client.get('/api/admin/school-type-report/statistics/', {
            'school_type': 'primary', 'province': legacy.province, 'city': legacy.city, 'district': legacy.district,
        }).data['data']
        self.assertEqual(report['summary']['count'], 1)
        self.assertEqual(report['summary']['std_dev'], 0)
