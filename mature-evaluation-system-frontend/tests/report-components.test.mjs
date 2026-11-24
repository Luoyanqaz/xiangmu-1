import assert from 'node:assert/strict'
import { test, after } from 'node:test'
import { readFile, writeFile, mkdir, mkdtemp, rm } from 'node:fs/promises'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createSSRApp } from 'vue'
import { renderToString } from '@vue/server-renderer'
import { MATURITY_LEVEL_RANGES, scoreToMaturityLevel } from '../src/utils/constants.js'

const cacheRoot = resolve('node_modules/.cache')
await mkdir(cacheRoot, { recursive: true })
const temp = await mkdtemp(resolve(cacheRoot, 'report-components-'))
after(() => rm(temp, { recursive: true, force: true }))
async function component(name) {
  const file = resolve('src/components', `${name}.vue`)
  const { descriptor, errors } = parse(await readFile(file, 'utf8'), { filename: file })
  assert.deepEqual(errors, [])
  const compiled = compileScript(descriptor, { id: name, inlineTemplate: true })
  const output = resolve(temp, `${name}.mjs`)
  await writeFile(output, compiled.content)
  return (await import(pathToFileURL(output).href)).default
}
const SchoolRank = await component('SchoolReportRank')
const RegionAnalysis = await component('RegionDimensionAnalysis')
const SchoolTypeReport = await component('SchoolTypeReportContent')

test('maturity classification includes lower boundaries and the maximum score', () => {
  for (const [score, expected] of [[0, 'initial'], [1.4999, 'initial'], [1.5, 'growing'], [2.9999, 'growing'], [3, 'mature'], [3.9999, 'mature'], [4, 'leading'], [5, 'leading']]) {
    assert.equal(scoreToMaturityLevel(score), expected)
    assert.equal(scoreToMaturityLevel(String(score)), expected)
  }
  for (const value of [null, undefined, '', ' ', true, -1, 5.001, NaN, Infinity]) {
    assert.equal(scoreToMaturityLevel(value), '')
  }
  assert.deepEqual(Object.values(MATURITY_LEVEL_RANGES), ['[0.0, 1.5)', '[1.5, 3.0)', '[3.0, 4.0)', '[4.0, 5.0]'])
})

test('school rank renders both cohorts and never fabricates a zero rank', async () => {
  const html = await renderToString(createSSRApp(SchoolRank, {
    ranking: { same_type: { rank: 3, total: 16 }, region: { rank: 6, total: 35 } }, inline: true,
  }))
  assert.match(html, /同类型学校位次/)
  assert.match(html, /3\/16/)
  assert.match(html, /6\/35/)
  const empty = await renderToString(createSSRApp(SchoolRank, {
    ranking: { same_type: { rank: null, total: 0 }, region: { rank: null, total: 0 } },
  }))
  assert.doesNotMatch(empty, /0\/0/)
  assert.equal((empty.match(/<strong>—<\/strong>/g) || []).length, 2)
})

test('regional sections render first/second level statistics, green technology and advice', async () => {
  const stats = { count: 2, average: 2, maximum: 4, minimum: 0, std_dev: 2, description: '最高4分，最低0分，平均2分，标准差2分。' }
  const dimensions = ['literacy', 'institution', 'behavior', 'asset', 'technology'].map(key => ({
    key, label: key === 'technology' ? '数据技术' : key, ...stats,
    highest_schools: ['甲校'], lowest_schools: ['乙校'], top_schools: [], bottom_schools: [],
    secondary_indicators: [{ key: 'E1', label: '数据基础设施', ...stats }],
  }))
  const html = await renderToString(createSSRApp(RegionAnalysis, {
    statistics: dimensions, suggestions: { technology: '依据数据基础设施得分，完善平台互联。' }, mode: 'fallback',
  }))
  assert.equal((html.match(/class="dimension-analysis"/g) || []).length, 5)
  assert.match(html, /--dimension-color:#88c391/)
  assert.match(html, /数据基础设施/)
  assert.match(html, /标准差/)
  assert.match(html, />0\.00</)
  assert.match(html, /依据数据基础设施得分，完善平台互联/)
  assert.doesNotMatch(html, /基于统计数据的规则建议/)
})

test('empty indicator uses dashes and withholds development judgments', async () => {
  const html = await renderToString(createSSRApp(RegionAnalysis, {
    statistics: [{ key: 'technology', label: '数据技术', count: 0, average: null, maximum: null, minimum: null, std_dev: null,
      secondary_indicators: [{ key: 'E1', label: '数据基础设施', count: 0, average: null }] }],
  }))
  assert.doesNotMatch(html, />0\.00</)
  assert.match(html, /暂无有效评估数据/)
})

test('regional literacy radar renders only in literacy, before advice, with distinct teacher/student scores', async () => {
  const children = ['A1', 'A2'].map((key, role) => ({
    key, label: role ? '学生数据素养' : '教师数据素养', average: 2,
    observation_indicators: Array.from({ length: 5 }, (_, index) => ({
      key: `${role ? 'A3' : 'A1'}${index + 1}`, average: role ? 4 : index,
    })),
  }))
  const dimension = { key: 'literacy', label: '数据素养', count: 2, secondary_indicators: children }
  const html = await renderToString(createSSRApp(RegionAnalysis, {
    statistics: [dimension, { key: 'behavior', label: '数据行为', count: 0, secondary_indicators: [] }],
  }))
  assert.equal((html.match(/class="literacy-radar-section"/g) || []).length, 1)
  assert.equal((html.match(/class="literacy-radar-chart"/g) || []).length, 2)
  assert.ok(html.indexOf('所属二级指标得分情况') < html.indexOf('教师与学生数据素养雷达图'))
  assert.ok(html.indexOf('教师与学生数据素养雷达图') < html.indexOf('针对数据素养维度的发展建议'))
  assert.match(html, /教师数据素养，区域学校均分（满分5分）：数据意识与思维0\.00/)
  assert.match(html, /学生数据素养，区域学校均分（满分5分）：数据意识与思维4\.00/)
  assert.doesNotMatch(html, /暂无完整五维数据/)
  children[0].observation_indicators[0].average = null
  const missing = await renderToString(createSSRApp(RegionAnalysis, { statistics: [dimension] }))
  assert.match(missing, /暂无完整五维数据/)
  assert.match(missing, /数据意识与思维：—/)
})

function typeReportFixture(empty = false) {
  const stats = { count: empty ? 0 : 1, average: empty ? null : 0, maximum: empty ? null : 0, minimum: empty ? null : 0, std_dev: empty ? null : 0 }
  const school = { school_id: 1, school_name: '测试学校甲', score: 0, maturity_level: 'initial', maturity_label: '初始级' }
  const ranking = { display_mode: 'full', schools: empty ? [] : [school], top_schools: [], bottom_schools: [] }
  return {
    region: { province: '测试省', city: '测试市', name: '一区' }, school_type_label: '小学', generated_at: '2026-11-10T08:00:00+08:00',
    scope_note: '同区域同类型，最近一次已完成评估。', secondary_note: '管理者数据素养暂无得分。',
    summary: { ...stats, completed_school_count: stats.count, school_count: stats.count }, total_ranking: ranking,
    levels: ['initial', 'growing', 'mature', 'leading'].map((key, index) => ({
      key, label: ['初始级', '成长级', '成熟级', '创新级'][index], score_range: MATURITY_LEVEL_RANGES[key],
      ...stats, count: index === 0 ? stats.count : 0, ratio: index === 0 && !empty ? 100 : 0,
      ...ranking, schools: index === 0 ? ranking.schools : [],
    })),
    dimensions: ['数据素养', '数据制度', '数据行为', '数据资产', '数据技术'].map((label, index) => ({
      key: String(index), label, ...stats,
      secondary_indicators: index === 0 ? [
        { key: 'A1', label: '教师数据素养', ...stats },
        { key: 'manager_literacy', label: '管理者数据素养', count: 0, average: null, unavailable_reason: '现行评分体系未设置该项得分，暂不统计。' },
        { key: 'A2', label: '学生数据素养', ...stats },
      ] : [{ key: 'E1', label: '二级指标', ...stats }],
    })),
  }
}

test('school type report follows reference order and renders populated levels and indicator statistics', async () => {
  const html = await renderToString(createSSRApp(SchoolTypeReport, { report: typeReportFixture() }))
  assert.ok(html.indexOf('学校总体成熟度') < html.indexOf('成熟度等级分布'))
  assert.ok(html.indexOf('成熟度等级分布') < html.indexOf('学校总分排序'))
  assert.ok(html.indexOf('学校总分排序') < html.indexOf('各成熟度等级学校表现'))
  assert.ok(html.indexOf('各成熟度等级学校表现') < html.indexOf('各维度表现'))
  assert.equal((html.match(/level-section /g) || []).length, 1)
  assert.equal((html.match(/class="secondary-section"/g) || []).length, 5)
  assert.match(html, /测试学校甲/)
  assert.match(html, /100\.0%/)
  assert.match(html, />0\.00</)
  assert.doesNotMatch(html, /<td>管理者数据素养/)
  assert.doesNotMatch(html, /现行评分体系未设置该项得分/)
  assert.match(html, /完整排序/)
  assert.doesNotMatch(html, />后5名</)
})

test('school type empty report preserves sections and displays missing scores as dashes', async () => {
  const html = await renderToString(createSSRApp(SchoolTypeReport, { report: typeReportFixture(true) }))
  assert.match(html, /该区域该类型学校暂无已完成评估/)
  assert.match(html, /暂无有效总分数据/)
  assert.match(html, />—</)
  assert.doesNotMatch(html, />0\.00</)
  assert.doesNotMatch(html, /测试学校甲/)
  assert.equal((html.match(/level-section /g) || []).length, 0)
  assert.match(html, /暂无法展示成熟度等级分布/)
  assert.doesNotMatch(html, /成熟度等级占比环形图/)
  assert.match(html, /成熟级及以上<\/span><strong>—<\/strong>/)
})

test('mature and leading percentage uses valid total scores rather than all completed schools', async () => {
  const report = typeReportFixture()
  report.summary = { ...report.summary, count: 6, completed_school_count: 8, school_count: 10 }
  report.levels.forEach((level, index) => {
    level.count = [2, 2, 1, 1][index]
    level.ratio = Math.round(level.count / 6 * 1000) / 10
  })
  const html = await renderToString(createSSRApp(SchoolTypeReport, { report }))
  assert.match(html, /纳入学校<\/span><strong>6/)
  assert.match(html, /已完成评估 8 \/ 10 所/)
  assert.match(html, /成熟级及以上<\/span><strong>33\.3%<\/strong><small>2 所学校/)
})
