<template>
  <article class="type-report">
    <header class="report-header">
      <h1>{{ report.region.name }}{{ report.school_type_label }}数据文化成熟度评估报告</h1>
      <div class="report-meta">
        <span>所属区域：{{ regionName }}</span>
        <span>学校类型：{{ report.school_type_label }}</span>
        <span>生成时间：{{ generatedTime }}</span>
      </div>
      <p class="scope-note">{{ scopeNote }}</p>
      <p v-if="report.summary.missing_count" class="missing-note">{{ report.summary.missing_count }} 所已完成评估的学校缺少有效总分，未纳入总分排序及等级分布；各指标按自身有效学校数统计。</p>
      <p v-if="!report.summary.completed_school_count" class="empty-notice">该区域该类型学校暂无已完成评估。</p>
    </header>

    <section class="report-section overview-section">
      <div class="section-heading"><h2>{{ report.school_type_label }}学校总体成熟度</h2><span>统计单位：学校 · 分值范围：0—5分</span></div>
      <div class="summary-grid">
        <div><span>纳入学校</span><strong>{{ report.summary.count }}<small> 所</small></strong><small>已完成评估 {{ report.summary.completed_school_count }} / {{ report.summary.school_count }} 所</small></div>
        <div><span>学校总分均值</span><strong>{{ score(report.summary.average) }}</strong><small>最高 {{ score(report.summary.maximum) }} · 最低 {{ score(report.summary.minimum) }}</small></div>
        <div><span>总分标准差</span><strong>{{ score(report.summary.std_dev) }}</strong><small>学校之间的离散程度</small></div>
        <div><span>成熟级及以上</span><strong>{{ matureRatio }}</strong><small>{{ matureCount }} 所学校</small></div>
      </div>
    </section>

    <section class="report-section distribution-section">
      <div class="section-heading"><h2>成熟度等级分布</h2><span>按学校总分划分等级</span></div>
      <div v-if="report.summary.count" class="maturity-chart-row">
        <div class="maturity-chart-card">
          <h3>成熟度等级占比</h3>
          <div ref="pieRef" class="maturity-chart-box" role="img" aria-label="成熟度等级占比环形图，具体数值见下方分布表"></div>
        </div>
        <div class="maturity-chart-card">
          <h3>成熟度等级学校数量</h3>
          <div ref="barRef" class="maturity-chart-box" role="img" aria-label="成熟度等级学校数量柱状图，具体数值见下方分布表"></div>
        </div>
      </div>
      <p v-else class="empty-notice">暂无有效总分数据，暂无法展示成熟度等级分布。</p>
      <div class="table-scroll">
        <table class="maturity-table">
          <thead><tr><th scope="col">成熟度等级</th><th scope="col">分数区间</th><th scope="col">学校数量</th><th scope="col">占比</th></tr></thead>
          <tbody><tr v-for="level in report.levels" :key="level.key">
            <td><span class="maturity-pill" :style="{ background: levelColors[level.key].light, color: levelColors[level.key].color }">{{ level.label }}</span></td>
            <td>{{ level.score_range }}</td><td class="maturity-count">{{ level.count }} 所</td><td>{{ report.summary.count ? `${level.ratio.toFixed(1)}%` : '—' }}</td>
          </tr></tbody>
        </table>
      </div>
    </section>

    <section class="report-section total-section">
      <div class="section-heading"><h2>学校总分排序</h2><span>所选区域同类型内排序 · 分数相同时按名称排序</span></div>
      <div class="ranking-grid" :class="{ 'single-list': report.total_ranking.display_mode === 'full' }">
        <div v-for="group in groups(report.total_ranking)" :key="group.title" class="ranking-list">
          <h3>{{ group.title }}</h3>
          <ol v-if="group.schools.length">
            <li v-for="(school, index) in group.schools" :key="school.school_id" class="school-row">
              <span class="row-number">{{ index + 1 }}</span><span class="school-name">{{ school.school_name }}</span>
              <strong>{{ score(school.score) }}</strong><span class="level-badge" :class="school.maturity_level">{{ school.maturity_label }}</span>
            </li>
          </ol>
          <p v-else class="empty-row">暂无有效总分数据</p>
        </div>
      </div>
    </section>

    <section class="report-section levels-section">
      <div class="section-heading"><h2>各成熟度等级学校表现</h2></div>
      <section v-for="level in populatedLevels" :key="level.key" class="level-section" :class="level.key">
        <div class="level-heading"><h3>{{ level.label }}</h3><span>{{ level.score_range }} 分</span></div>
        <div class="level-stats">
          <span>学校 <strong>{{ level.count }} 所</strong></span><span>占比 <strong>{{ level.ratio.toFixed(1) }}%</strong></span>
          <span>均分 <strong>{{ score(level.average) }}</strong></span><span>标准差 <strong>{{ score(level.std_dev) }}</strong></span>
        </div>
        <div class="ranking-grid" :class="{ 'single-list': level.display_mode === 'full' }">
          <div v-for="group in groups(level)" :key="group.title" class="ranking-list">
            <h4>{{ group.title }}</h4>
            <ol v-if="group.schools.length">
              <li v-for="(school, index) in group.schools" :key="school.school_id" class="school-row">
                <span class="row-number">{{ index + 1 }}</span><span class="school-name">{{ school.school_name }}</span>
                <strong>{{ score(school.score) }}</strong><span class="level-badge" :class="school.maturity_level">{{ school.maturity_label }}</span>
              </li>
            </ol>
            <p v-else class="empty-row">本等级暂无学校</p>
          </div>
        </div>
      </section>
    </section>

    <section class="report-section dimensions-section">
      <div class="section-heading"><h2>各维度表现</h2></div>
      <div class="table-scroll">
        <table class="indicator-table primary-table">
          <thead><tr><th scope="col">一级维度</th><th scope="col">均分</th><th scope="col">最高分</th><th scope="col">最低分</th><th scope="col">标准差</th></tr></thead>
          <tbody><tr v-for="dimension in report.dimensions" :key="dimension.key">
            <th scope="row">{{ dimension.label }}</th><td>{{ score(dimension.average) }}</td><td>{{ score(dimension.maximum) }}</td>
            <td>{{ score(dimension.minimum) }}</td><td>{{ score(dimension.std_dev) }}</td>
          </tr></tbody>
        </table>
      </div>
      <section v-for="(dimension, index) in report.dimensions" :key="dimension.key" class="secondary-section">
        <div class="secondary-heading"><h3><span class="dimension-number">{{ String(index + 1).padStart(2, '0') }}</span>{{ dimension.label }}</h3><span>一级维度均分 {{ score(dimension.average) }}</span></div>
        <div class="table-scroll">
          <table class="indicator-table secondary-table">
            <thead><tr><th scope="col">所属二级指标</th><th scope="col">均分</th><th scope="col">最高分</th><th scope="col">最低分</th><th scope="col">标准差</th></tr></thead>
            <tbody><tr v-for="child in dimension.secondary_indicators.filter(indicator => indicator.key !== 'manager_literacy')" :key="child.key">
              <td>{{ child.label }}<small v-if="child.unavailable_reason" class="indicator-note">{{ child.unavailable_reason }}</small></td>
              <td><div class="mean-cell"><span class="score-track" aria-hidden="true"><span :style="{ width: `${(child.average ?? 0) * 20}%` }"></span></span><span>{{ score(child.average) }}</span></div></td>
              <td>{{ score(child.maximum) }}</td><td>{{ score(child.minimum) }}</td><td>{{ score(child.std_dev) }}</td>
            </tr></tbody>
          </table>
        </div>
      </section>
    </section>
    <footer class="report-footer">-本报告由中小学校数据文化成熟度评估监测系统自动生成-</footer>
  </article>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts'
const props = defineProps({ report: { type: Object, required: true } })
const pieRef = ref(null)
const barRef = ref(null)
let charts = []
let resizeObserver
const levelColors = {
  initial: { color: '#f27b7b', light: '#f9dede' },
  growing: { color: '#f0ab4d', light: '#fae7c9' },
  mature: { color: '#67c98a', light: '#dff4e7' },
  leading: { color: '#5ca4d9', light: '#dbeefa' },
}
const populatedLevels = computed(() => props.report.levels.filter(level => level.count > 0))
const matureCount = computed(() => props.report.levels
  .filter(level => level.key === 'mature' || level.key === 'leading')
  .reduce((total, level) => total + level.count, 0))
const matureRatio = computed(() => props.report.summary.count
  ? `${(matureCount.value / props.report.summary.count * 100).toFixed(1)}%` : '—')
const regionName = computed(() => [props.report.region.province, props.report.region.city, props.report.region.name].filter(Boolean).join(' / '))
const scopeNote = computed(() => (props.report.scope_note || '').replace(
  '均值与总体标准差按学校得分计算，0分正常计入，缺失及超出0—5范围的值不计入；单校标准差为0，无有效数据时显示“—”。',
  '',
))
const generatedTime = computed(() => new Date(props.report.generated_at).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }))
const score = value => value != null && Number.isFinite(Number(value)) ? Number(value).toFixed(2) : '—'
const groups = ranking => ranking.display_mode === 'full'
  ? [{ title: '完整排序', schools: ranking.schools }]
  : [{ title: '前5名', schools: ranking.top_schools }, { title: '后5名', schools: ranking.bottom_schools }]

function disposeCharts() {
  resizeObserver?.disconnect()
  charts.forEach(chart => chart.dispose())
  charts = []
}

function renderCharts() {
  disposeCharts()
  if (!pieRef.value || !barRef.value) return
  const levels = props.report.levels
  const pie = echarts.init(pieRef.value)
  charts.push(pie)
  pie.setOption({
    animation: false,
    tooltip: { trigger: 'item', formatter: '{b}<br/>学校数：{c} 所<br/>占比：{d}%' },
    legend: { bottom: 8, left: 'center', itemWidth: 18, itemHeight: 12, icon: 'roundRect', textStyle: { color: '#475569', fontSize: 13 } },
    series: [{
      name: '成熟度等级占比', type: 'pie', radius: ['42%', '68%'], center: ['50%', '44%'],
      avoidLabelOverlap: true, minAngle: 5,
      itemStyle: { borderColor: '#ffffff', borderWidth: 6, borderRadius: 10 },
      label: { show: true, formatter: '{b}\n{d}%', fontSize: 14, fontWeight: 700, color: '#3f3f46', lineHeight: 24 },
      labelLine: { show: true, length: 18, length2: 16, lineStyle: { width: 1.5 } },
      data: levels.map(level => ({ name: level.label, value: level.count, itemStyle: { color: levelColors[level.key].color } })),
    }],
  })
  const bar = echarts.init(barRef.value)
  charts.push(bar)
  bar.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>学校数量：{c} 所' },
    grid: { left: 48, right: 20, top: 40, bottom: 70 },
    xAxis: {
      type: 'category', data: levels.map(level => `${level.label}\n${level.score_range}`), axisTick: { show: false },
      axisLine: { lineStyle: { color: '#9ca3af' } }, axisLabel: { color: '#6b7280', fontSize: 12, lineHeight: 18, interval: 0 },
    },
    yAxis: {
      type: 'value', name: '学校数量（所）', min: 0, minInterval: 1,
      nameTextStyle: { color: '#6b7280', fontSize: 12, padding: [0, 0, 8, -10] },
      splitLine: { lineStyle: { color: '#d9e3ef' } }, axisLabel: { color: '#6b7280', fontSize: 12 },
    },
    series: [{
      type: 'bar', barMaxWidth: 56,
      data: levels.map(level => ({ value: level.count, itemStyle: { color: levelColors[level.key].color, borderRadius: [10, 10, 0, 0] } })),
      label: { show: true, position: 'top', formatter: '{c}所', color: '#3f3f46', fontSize: 16, fontWeight: 700 },
    }],
  })
  resizeObserver = new ResizeObserver(() => charts.forEach(chart => chart.resize()))
  resizeObserver.observe(pieRef.value)
  resizeObserver.observe(barRef.value)
}

onMounted(renderCharts)
watch(() => props.report, renderCharts, { flush: 'post' })
onBeforeUnmount(disposeCharts)
</script>

<style scoped>
.type-report { --ink: #23456d; --muted: #77899d; --rule: #e0e9f3; color: #263c55; background: #fff; font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; padding: 40px 44px 28px; line-height: 1.6; }
.report-header { padding-bottom: 26px; border-bottom: 1px solid var(--rule); }
h1 { text-align: center; font-size: 27px; color: var(--ink); margin: 0 0 20px; }
.report-meta { display: flex; justify-content: center; gap: 12px 24px; flex-wrap: wrap; color: #000; font-size: 15px; }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); background: #f6f9fd; border: 1px solid var(--rule); border-radius: 6px; }
.summary-grid > div { padding: 16px 10px; text-align: center; }
.summary-grid > div + div { border-left: 1px solid var(--rule); }
.summary-grid span { display: block; font-size: 13px; color: var(--muted); }
.summary-grid strong { display: block; font-size: 23px; margin-top: 4px; color: var(--ink); }
.summary-grid small { font-size: 12px; font-weight: 400; }
.maturity-chart-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 34px; margin-bottom: 28px; }
.maturity-chart-card { min-width: 0; }
.maturity-chart-card h3 { text-align: center; font-size: 18px; font-weight: 800; color: #2f5f97; margin: 0 0 10px; }
.maturity-chart-box { height: 420px; }
.maturity-table { width: 100%; min-width: 560px; border-collapse: separate; border-spacing: 0; font-size: 15px; }
.maturity-table th { background: linear-gradient(90deg, #2d66a3, #357cc1); color: white; font-weight: 800; padding: 16px 18px; text-align: left; }
.maturity-table th:first-child { border-top-left-radius: 10px; }
.maturity-table th:last-child { border-top-right-radius: 10px; }
.maturity-table td { padding: 18px; border-bottom: 1px solid #edf2f7; }
.maturity-table tbody tr:nth-child(even) { background: #f7fafc; }
.maturity-pill { display: inline-flex; justify-content: center; min-width: 68px; padding: 6px 14px; border-radius: 999px; font-size: 14px; font-weight: 800; white-space: nowrap; }
.maturity-count { font-weight: 800; }
.scope-note { font-size: 12px; color: var(--muted); line-height: 1.8; }
.scope-note { margin: 12px 0 0; }
.missing-note { font-size: 13px; color: #936a31; }
.empty-notice { padding: 16px; text-align: center; background: #f6f9fd; color: var(--muted); }
.report-section { padding: 32px 0; border-bottom: 1px solid var(--rule); }
.section-heading { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 8px 20px; padding-bottom: 12px; border-bottom: 3px solid #588ac7; margin-bottom: 24px; }
.section-heading h2 { margin: 0; font-size: 23px; color: var(--ink); }
.section-heading > span, .secondary-heading > span { font-size: 13px; color: var(--muted); }
.ranking-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 36px; }
.ranking-grid.single-list { grid-template-columns: 1fr; }
.ranking-list h3, .ranking-list h4 { margin: 0 0 12px; font-size: 18px; color: var(--ink); }
.ranking-list ol { list-style: none; padding: 0; margin: 0; border-top: 1px solid var(--rule); }
.school-row { display: flex; align-items: center; gap: 10px; min-height: 52px; padding: 10px 5px; border-bottom: 1px solid var(--rule); box-sizing: border-box; break-inside: avoid; }
.row-number { flex: 0 0 26px; color: var(--muted); font-variant-numeric: tabular-nums; }
.school-name { flex: 1; overflow-wrap: anywhere; font-size: 14px; }
.school-row > strong { color: var(--ink); font-variant-numeric: tabular-nums; }
.level-badge { white-space: nowrap; font-size: 13px; font-weight: 600; border-radius: 4px; padding: 4px 7px; }
.initial { --level-color: #d8757c; --level-light: #fcf2f3; }
.growing { --level-color: #d3a24c; --level-light: #fcf7eb; }
.mature { --level-color: #6db38c; --level-light: #eff8f3; }
.leading { --level-color: #608fd0; --level-light: #eff5fe; }
.level-badge { color: var(--level-color); background: var(--level-light); }
.level-section { padding: 26px 0 30px; border-bottom: 1px solid var(--rule); }
.level-section:last-child { border-bottom: none; padding-bottom: 0; }
.level-heading { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; border-left: 5px solid var(--level-color); padding-left: 14px; }
.level-heading h3 { margin: 0; font-size: 19px; color: var(--ink); }
.level-heading > span { font-size: 13px; color: var(--muted); }
.level-stats { display: flex; flex-wrap: wrap; gap: 12px 24px; padding: 14px 0 24px 19px; font-size: 13px; color: var(--muted); }
.level-stats strong { color: #314b69; }
.empty-row { margin: 0; border-top: 1px solid var(--rule); padding: 20px; color: var(--muted); text-align: center; font-size: 14px; }
.table-scroll { overflow-x: auto; }
.indicator-table { width: 100%; min-width: 640px; border-collapse: collapse; font-size: 14px; table-layout: fixed; }
.indicator-table th, .indicator-table td { padding: 13px 12px; border-bottom: 1px solid var(--rule); text-align: right; vertical-align: middle; }
.indicator-table th:first-child, .indicator-table td:first-child { text-align: left; width: 30%; }
.indicator-table thead { background: #ebf2fb; color: #365b87; }
.indicator-table tbody tr:nth-child(even) { background: #f7faff; }
.indicator-table tbody th { color: #334c68; }
.secondary-table th:first-child, .secondary-table td:first-child { width: 35%; }
.secondary-table th:nth-child(2) { width: 22%; }
.secondary-section { margin-top: 28px; }
.secondary-heading { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; }
.secondary-heading h3 { display: flex; align-items: center; gap: 12px; margin: 0; color: var(--ink); font-size: 18px; }
.dimension-number { background: #507fb6; color: #fff; border-radius: 4px; padding: 2px 7px; font-size: 14px; font-weight: 400; }
.mean-cell { display: flex; align-items: center; justify-content: flex-end; gap: 10px; }
.score-track { display: inline-block; width: 75px; height: 7px; background: #e6eef9; border-radius: 5px; overflow: hidden; flex-shrink: 0; }
.score-track > span { display: block; height: 100%; background: #507fb6; border-radius: 5px; }
.indicator-note { display: block; color: var(--muted); font-size: 11px; margin-top: 4px; }
.report-footer { text-align: center; padding-top: 26px; color: #999fa7; font-size: 13px; }
@media (max-width: 900px) {
  .type-report { padding: 24px 20px; }
  .ranking-grid { grid-template-columns: 1fr; gap: 24px; }
  .maturity-chart-row { grid-template-columns: 1fr; }
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
  .summary-grid > div + div { border-left: none; }
  h1 { font-size: 22px; }
}
@media print {
  .type-report { padding: 0; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  .table-scroll { overflow: visible; }
  .section-heading, .secondary-heading, .level-heading { break-after: avoid; }
  tr, .school-row { break-inside: avoid; }
}
</style>
