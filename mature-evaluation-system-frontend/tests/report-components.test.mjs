import assert from 'node:assert/strict'
import { test, after } from 'node:test'
import { readFile, writeFile, mkdir, mkdtemp, rm } from 'node:fs/promises'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createSSRApp } from 'vue'
import { renderToString } from '@vue/server-renderer'

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
  assert.match(html, /基于统计数据的规则建议/)
})

test('empty indicator uses dashes and withholds development judgments', async () => {
  const html = await renderToString(createSSRApp(RegionAnalysis, {
    statistics: [{ key: 'technology', label: '数据技术', count: 0, average: null, maximum: null, minimum: null, std_dev: null,
      secondary_indicators: [{ key: 'E1', label: '数据基础设施', count: 0, average: null }] }],
  }))
  assert.doesNotMatch(html, />0\.00</)
  assert.match(html, /暂无有效评估数据/)
})
