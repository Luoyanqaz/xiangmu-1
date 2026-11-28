from unittest.mock import Mock

from django.test import SimpleTestCase, override_settings

from . import final_advice
from .report_ai_service import ReportAIService
from .statistics import DIMENSIONS, REGIONAL_OBSERVATIONS


@override_settings(REPORT_ADVICE_VERSION='20261120', LLM_ALLOW_NETWORK=False)
class FinalAdviceTests(SimpleTestCase):
    def setUp(self):
        self.data = {
            'total_score': 3, 'maturity_level': '成熟级', 'dimension_scores': {key: 3 for key, _, _ in DIMENSIONS},
            'observation_scores': {code: 4 for group in REGIONAL_OBSERVATIONS.values() for code in group},
        }

    def test_high_scores_are_grouped_and_do_not_generate_actions(self):
        llm = Mock()
        self.data['total_score'] = 5
        result, mode, sources = final_advice.generate(self.data, llm)
        self.assertEqual((mode, sources), ('rules', {}))
        self.assertIn('创新级', result['overall'])
        self.assertNotIn('建议', ''.join(result.values()))
        self.assertIn('数据硬件设施、数据系统平台均表现非常优秀', result['technology'])
        llm._call_api.assert_not_called()

    @override_settings(REPORT_ADVICE_VERSION='20261128')
    def test_nov28_school_and_region_actions_online_and_offline(self):
        self.data['observation_scores'] = dict.fromkeys(self.data['observation_scores'], 2)
        regional = {'summary': {'avg_score': 2}, 'dimension_statistics': [
            {'key': key, 'average': 2, 'secondary_indicators': [
                {'key': child, 'average': 2, 'observation_indicators': [
                    {'key': code, 'average': 2} for code in REGIONAL_OBSERVATIONS[child]]}
                for child, _ in children]} for key, _, children in DIMENSIONS]}
        for region, data in ((False, self.data), (True, regional)):
            with self.subTest(region=region):
                model = Mock()
                result, mode, sources = final_advice.generate(data, model, region=region)
                model._call_api.assert_not_called()
                self.assertEqual(mode, 'fallback')
                self.assertEqual(set(sources), set(self.data['observation_scores']))
                self.assertIn('由区域教育信息化技术支持单位' if region else '由信息中心', result['technology'])
                model._call_api.return_value = '{"E11":{"actor":"设备组","action":"核查教学终端的配置"}}'
                with override_settings(LLM_ALLOW_NETWORK=True):
                    result, mode, sources = final_advice.generate(data, model, region=region)
                self.assertIn('提出区域层面可采取的改进措施' if region else '提出学校可采取的改进措施',
                              model._call_api.call_args.args[0])
                self.assertEqual((mode, sources['E11'], sources['E12']), ('mixed', 'ai', 'fallback'))
                self.assertIn('由设备组核查教学终端的配置', result['technology'])

    def test_boundary_ties_missing_values_and_lowest_two(self):
        self.data['dimension_scores'].update(asset=1.5, technology=1.5, behavior=1.5)
        self.data['observation_scores'].update(E11=0, E12=None, E21=1.5, E22=1.5)
        result, mode, _ = final_advice.generate(self.data, None)
        self.assertEqual(mode, 'fallback')
        self.assertIn('数据硬件设施表现有待提升', result['technology'])
        self.assertIn('数据系统平台暂无有效得分', result['technology'])
        self.assertIn('核查等保', result['technology'])
        self.assertIn('建立风险事件台账', result['technology'])
        self.assertNotIn('基础设施与安全保障需求', result['overall'])
        self.assertIn('按学期跟踪', result['overall'])

    @override_settings(LLM_ALLOW_NETWORK=True)
    def test_role_specific_prompt_and_invalid_response(self):
        self.data['observation_scores']['E21'] = 1
        llm = Mock()
        llm._call_api.return_value = '{"E21":"由信息中心核验平台等保材料"}'
        school, mode, _ = final_advice.generate(self.data, llm)
        self.assertEqual(mode, 'ai')
        self.assertIn('由信息中心核验', school['technology'])
        self.assertIn('校内实施主体', llm._call_api.call_args.args[0])
        region = {
            'summary': {'avg_score': 4},
            'dimension_statistics': [{'key': 'technology', 'average': 4, 'secondary_indicators': [
                {'key': 'E2', 'average': 3, 'observation_indicators': [
                    {'key': 'E21', 'average': 1}, {'key': 'E22', 'average': 5}]}]}],
        }
        llm._call_api.return_value = '{}'
        regional, mode, _ = final_advice.generate(region, llm, region=True)
        self.assertEqual(mode, 'fallback')
        self.assertIn('该区域数据技术得分为4.00分', regional['technology'])
        self.assertIn('区域教育管理部门', regional['technology'])
        self.assertIn('区域可采取的措施', llm._call_api.call_args.args[0])
        self.assertNotIn('短板', regional['overall'])

    @override_settings(LLM_ALLOW_NETWORK=True)
    def test_preserves_valid_actions_within_and_across_sections(self):
        self.data['observation_scores'].update(E21=1, E22=1, D21=1)
        service = ReportAIService(initialize_llm=False)
        service.llm_service = Mock()
        for response in (
            '{"E21":"由信息中心复核认证资料","D21":"由资源组登记数据资产"}',
            '{"E21":"由信息中心复核认证资料","E22":"得2分","D21":"由资源组登记数据资产"}',
            '{"E21":"由信息中心复核认证资料"}\n{"E22":broken}\n{"D21":"由资源组登记数据资产"}',
        ):
            with self.subTest(response=response):
                service.llm_service._call_api.return_value = response
                result = service.generate_all_suggestions(self.data)
                self.assertEqual(result['_mode'], 'mixed')
                self.assertEqual(result['_action_sources'], {'D21': 'ai', 'E21': 'ai', 'E22': 'fallback'})
                self.assertIn('由资源组登记数据资产', result['asset'])
                self.assertIn('由信息中心复核认证资料', result['technology'])
                self.assertIn('建立风险事件台账', result['technology'])
                self.assertTrue(service.can_reuse(result))

    def test_old_whole_report_fallback_is_rebuilt_once(self):
        self.data['observation_scores']['E21'] = 1
        service = ReportAIService(initialize_llm=False)
        old = service.generate_all_suggestions(self.data)
        del old['_action_sources']
        self.assertFalse(service.can_reuse(old))
        refreshed = service.normalize_cached_suggestions(self.data, old)
        self.assertEqual(refreshed['_action_sources'], {'E21': 'fallback'})
        self.assertTrue(service.can_reuse(refreshed))

    def test_rollback_invalidates_new_cache_and_selects_original_rules(self):
        service = ReportAIService(initialize_llm=False)
        final = service.normalize_cached_suggestions(self.data, {'_schema_version': 4, 'overall': '旧建议'})
        self.assertTrue(service.can_reuse(final))
        with override_settings(REPORT_ADVICE_VERSION='legacy'):
            self.assertFalse(service.can_reuse(final))
            restored = service.generate_all_suggestions(self.data)
            self.assertEqual(restored['_schema_version'], 4)
            self.assertTrue(service.can_reuse(restored))

    @override_settings(REPORT_ADVICE_VERSION='20261124', LLM_ALLOW_NETWORK=True)
    def test_nov24_all_low_dimensions_and_each_scored_observation(self):
        self.data['dimension_scores'].update(literacy=2.9, institution=1, asset=2)
        self.data['observation_scores'].update(E11=0, E12=2.9, E21=3)
        service = ReportAIService(initialize_llm=False)
        service.llm_service = Mock()
        service.llm_service._call_api.return_value = '{"E12":"由信息中心汇总各平台接口需求"}'
        result = service.generate_all_suggestions(self.data)
        self.assertIn('建议优先围绕数据制度、数据资产、数据素养制定专项改进计划', result['overall'])
        self.assertIn('但数据素养、数据资产均表现比较良好，数据制度表现有待提升，仍有改进空间', result['overall'])
        self.assertEqual(result['_action_sources'], {'E11': 'fallback', 'E12': 'ai'})
        self.assertIn('由信息中心汇总各平台接口需求', result['technology'])
        self.assertEqual(result['_schema_version'], '20261124')
        with override_settings(REPORT_ADVICE_VERSION='20261120'):
            self.assertFalse(service.can_reuse(result))
            old = service.generate_all_suggestions(self.data)
        self.assertFalse(service.can_reuse(old))

    @override_settings(REPORT_ADVICE_VERSION='20261124')
    def test_nov24_high_and_missing_are_distinct_in_both_scopes(self):
        school, _, sources = final_advice.generate(self.data, None)
        self.assertEqual(sources, {})
        self.assertIn('建议巩固各维度已有的建设成效', school['overall'])
        region = {'summary': {'avg_score': 3}, 'dimension_statistics': [
            {'key': key, 'average': 3, 'secondary_indicators': []} for key, _, _ in DIMENSIONS]}
        result, _, _ = final_advice.generate(region, None, region=True)
        self.assertIn('形成可供其他地区借鉴的实践模式', result['overall'])
        region['dimension_statistics'][1]['average'] = None
        result, _, _ = final_advice.generate(region, None, region=True)
        self.assertIn('数据制度暂无有效得分', result['overall'])
        self.assertNotIn('形成可供其他地区借鉴', result['overall'])
        region['dimension_statistics'][2]['average'] = 0
        result, _, _ = final_advice.generate(region, None, region=True)
        self.assertIn('当前短板主要集中在数据行为，区域教育管理部门可依托', result['overall'])

    @override_settings(REPORT_ADVICE_VERSION='20261126')
    def test_nov26_overall_priority_order_cap_and_uniform_low_band(self):
        self.data['dimension_scores'].update(literacy=2.9, institution=2.8, behavior=2.7, asset=1.5, technology=1.6)
        region = {'summary': {'avg_score': 2}, 'dimension_statistics': [
            {'key': key, 'average': score, 'secondary_indicators': []}
            for key, score in self.data['dimension_scores'].items()]}
        school, _, _ = final_advice.generate(self.data, None)
        regional, _, _ = final_advice.generate(region, None, region=True)
        self.assertIn('均表现比较良好，仍有改进空间。', school['overall'])
        self.assertIn('优先围绕数据素养、数据制度、数据行为制定', school['overall'])
        self.assertIn('短板主要集中在数据素养、数据制度、数据行为等方面', regional['overall'])
        self.assertNotIn('\n', regional['literacy'])
        self.data['dimension_scores'].update(literacy=3, institution=None, behavior=4, asset=0, technology=5)
        school, _, _ = final_advice.generate(self.data, None)
        self.assertIn('但数据资产表现有待提升，仍有改进空间', school['overall'])
        self.assertIn('数据制度暂无有效得分', school['overall'])
        self.assertIn('优先围绕数据资产制定', school['overall'])

    @override_settings(REPORT_ADVICE_VERSION='20261126', LLM_ALLOW_NETWORK=True)
    def test_nov26_combines_actions_by_actor_and_keeps_individual_fallback(self):
        self.data['observation_scores'].update(E11=2, E12=2, E21=1, E22=3)
        llm = Mock()
        llm._call_api.return_value = (
            '{"E11":{"actor":"信息中心","action":"盘点教学终端"}}\n'
            '{"E12":{"actor":"信息中心","action":"核对各平台接口"}}\n'
            '{"E21":{"action":"缺少实施主体"}}')
        school, mode, sources = final_advice.generate(self.data, llm)
        self.assertEqual((mode, sources), ('mixed', {'E11': 'ai', 'E12': 'ai', 'E21': 'fallback'}))
        self.assertIn('该校的校内部门或岗位', llm._call_api.call_args.args[0])
        self.assertIn('其中，数据基础设施方面', school['technology'])
        self.assertIn('由信息中心盘点教学终端，并核对各平台接口。', school['technology'])
        self.assertIn('由信息中心核查等保', school['technology'])
        self.assertTrue(all('\n' not in paragraph for paragraph in school.values()))

        region = {'summary': {'avg_score': 3}, 'dimension_statistics': [
            {'key': 'technology', 'average': 3, 'secondary_indicators': [
                {'key': 'E2', 'average': 2, 'observation_indicators': [{'key': 'E21', 'average': 1}]}]}]}
        regional, mode, _ = final_advice.generate(region, llm, region=True)
        self.assertIn('区域内的教研、技术支持机构', llm._call_api.call_args.args[0])
        self.assertEqual(mode, 'fallback')
        self.assertIn('由区域教育管理部门指导参评学校核查等保', regional['technology'])

    @override_settings(REPORT_ADVICE_VERSION='20261127', LLM_ALLOW_NETWORK=True)
    def test_nov27_lowest_three_in_both_reports_and_individual_observation_actions(self):
        self.data['dimension_scores'].update(literacy=2.9, institution=1.5, behavior=1.5, asset=0, technology=1.5)
        self.data['observation_scores'].update(E11=2, E12=0, E21=1, E22=3)
        regional = {'summary': {'avg_score': 2}, 'dimension_statistics': [
            {'key': key, 'average': score, 'secondary_indicators': []}
            for key, score in reversed(list(self.data['dimension_scores'].items()))]}
        regional['dimension_statistics'][0]['secondary_indicators'] = [
            {'key': 'E1', 'average': 1, 'observation_indicators': [
                {'key': 'E11', 'average': 2}, {'key': 'E12', 'average': 0}]},
            {'key': 'E2', 'average': 2, 'observation_indicators': [
                {'key': 'E21', 'average': 1}, {'key': 'E22', 'average': 3}]}]
        for region, data in ((False, self.data), (True, regional)):
            with self.subTest(region=region):
                model = Mock()
                actor = '区域教师发展中心' if region else '教务处'
                model._call_api.return_value = '{"E11":{"actor":"' + actor + '","action":"盘点教学终端"}}'
                report, mode, sources = final_advice.generate(data, model, region=region)
                self.assertIn('数据资产、数据制度、数据行为等方面', report['overall'])
                self.assertEqual(sources, {'E11': 'ai', 'E12': 'fallback', 'E21': 'fallback'})
                self.assertEqual(mode, 'mixed')
                self.assertIn('由' + actor + '盘点教学终端', report['technology'])
                prompt = model._call_api.call_args.args[0]
                self.assertIn('按得分由低到高依次选取最多3个一级维度', prompt)
                self.assertIn(actor, prompt)
