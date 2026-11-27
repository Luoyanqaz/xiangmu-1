from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.assessments.models import Assessment, AssetAssessment, BehaviorAssessment, InstitutionAssessment, TechnologyAssessment
from apps.assessments.scoring_service import ScoringService
from apps.assessments.services.submission import submit_round
from apps.schools.models import School
from .models import SurveyInstance, SurveyQuestion, SurveyResponse, SurveyTemplate
from .quality import collection, regional_collection


class SurveyQualityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('school', 'school@test.local', 'pw')
        cls.school = School.objects.create(user=user, name='测试学校', contact_email=user.email)
        cls.round = Assessment.objects.create(school=cls.school)
        cls.instances = {}
        for role, order in [('teacher', 6), ('student', 4)]:
            template = SurveyTemplate.objects.create(survey_type=role, title=role)
            SurveyQuestion.objects.create(template=template, question_type='scale', order=order,
                                          question_text='测试题', options=['符合', '不符合'])
            cls.instances[role] = SurveyInstance.objects.create(template=template, assessment=cls.round)

    def answer(self, role, attention, elapsed, repeat=False):
        api = APIClient()
        instance = self.instances[role]
        with patch('apps.surveys.quality.time.time_ns', return_value=100_000_000_000):
            form = api.get(reverse('survey-public-get', args=[instance.uuid])).data
        self.assertEqual(len(form['questions']), 2)
        answers = {'q' + str(q['order']): '符合' for q in form['questions']}
        answers['qattention'] = attention
        payload = {'attempt': form['attempt'], 'elapsed_ms': elapsed, 'answers': answers}
        url = reverse('survey-public-submit', args=[instance.uuid])
        with patch('apps.surveys.quality.time.time_ns', return_value=(100_000 + elapsed) * 1_000_000):
            result = api.post(url, payload, format='json')
            self.assertEqual(result.status_code, 201, result.data)
            if repeat:
                self.assertEqual(api.post(url, payload, format='json').data, result.data)
        return SurveyResponse.objects.get(id=result.data['response_id'])

    def test_one_valid_group_filters_answers_and_freezes_counts(self):
        good = self.answer('teacher', '不符合', 2500, repeat=True)
        self.assertTrue(good.is_valid)
        self.assertNotIn('qattention', good.answers)
        self.assertEqual(self.answer('teacher', '符合', 2500).quality_details['reasons'], ['attention'])
        bad = self.answer('student', '不符合', 2499)
        self.assertEqual(bad.quality_details['reasons'], ['duration'])
        self.assertEqual(bad.answers, {})
        submit_round(self.round, Mock())
        self.round.refresh_from_db()
        counts = collection(self.round)
        self.assertEqual(counts, {'teacher': {'valid': 1, 'received': 2}, 'student': {'valid': 0, 'received': 1}})
        scoring = ScoringService(self.round)
        scoring.calculate_all_scores()
        self.assertEqual(scoring.observation_scores['A11'], 0.5)
        self.assertEqual(scoring.secondary_scores['A2'], 0)
        self.assertEqual(regional_collection([self.round])['shortages']['student'], 1)
        self.assertIsNone(submit_round(self.round, Mock()))
        self.assertEqual(APIClient().get(reverse('survey-public-get', args=[self.instances['teacher'].uuid])).status_code, 403)

    def test_only_student_and_both_groups(self):
        self.answer('student', '不符合', 2501)
        scoring = ScoringService(self.round)
        scoring.calculate_all_scores()
        self.assertGreater(scoring.secondary_scores['A2'], 0)
        self.assertEqual(scoring.secondary_scores['A1'], 0)
        self.assertEqual(regional_collection([self.round])['shortages']['teacher'], 1)
        self.answer('teacher', '不符合', 2500)
        submit_round(self.round, Mock())
        self.round.refresh_from_db()
        self.assertEqual(collection(self.round)['teacher']['valid'], 1)
        self.assertEqual(regional_collection([self.round])['shortages'], {'both': 0, 'teacher': 0, 'student': 0})

    def test_both_groups_without_valid_responses_keep_non_survey_scores(self):
        bad = self.answer('student', '符合', 2499)
        self.assertEqual(bad.quality_details['reasons'], ['attention', 'duration'])
        InstitutionAssessment.objects.create(assessment=self.round, management_doc_status='follow_policy')
        TechnologyAssessment.objects.create(assessment=self.round, has_independent_data_center=True,
                                            data_center_standard='fully_compliant', student_device_ratio='low',
                                            teacher_device_ratio='low')
        BehaviorAssessment.objects.create(assessment=self.round, published_paper_count=2)
        AssetAssessment.objects.create(assessment=self.round)
        submit_round(self.round, Mock())
        self.round.refresh_from_db()
        scoring = ScoringService(self.round)
        scores = scoring.calculate_all_scores()
        points = self.round.score_details['observation_scores']
        for key in ('A11', 'A31', 'C23', 'D11', 'D12', 'D13'):
            self.assertEqual(points[key], 0)
        self.assertEqual(scores['literacy_score'], 0)
        self.assertEqual(points['E11'], 5)
        self.assertGreater(points['B31'], 0)
        self.assertGreater(points['C21'], 0)
        self.assertGreater(scores['total_score'], 0)
        self.assertEqual(regional_collection([self.round])['shortages']['both'], 1)

    def test_legacy_links_and_expired_links(self):
        self.round.check_survey_quality = False
        self.round.save()
        api = APIClient()
        instance = self.instances['teacher']
        form = api.get(reverse('survey-public-get', args=[instance.uuid])).data
        self.assertNotIn('attempt', form)
        url = reverse('survey-public-submit', args=[instance.uuid])
        self.assertEqual(api.post(url, {'answers': {'q6': '符合'}}, format='json').status_code, 201)
        self.assertEqual(collection(self.round)['teacher'], {'received': 1, 'valid': None})
        self.assertEqual(regional_collection([self.round])['teacher']['unjudged'], 1)
        instance.expired_at = timezone.now()
        instance.save()
        self.assertEqual(api.post(url, {'answers': {}}, format='json').status_code, 400)
