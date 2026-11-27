<template>
  <div class="dimension-analysis-group">
    <h2 class="analysis-heading">各维度表现分析</h2>
    <p class="analysis-note">{{ displayNote }}</p>
    <p v-if="legacyCount" class="analysis-note">{{ secondaryNote }}</p>
    <div v-if="developmentSummary" class="development-summary-box">{{ developmentSummary }}</div>
    <section v-for="dimension in statistics" :key="dimension.key" class="dimension-analysis" :style="palette(dimension.key)">
      <header class="dimension-banner">
        <h3>{{ dimension.label }}维度分析</h3>
        <div class="banner-score"><strong>{{ score(dimension.average) }}</strong><span>平均分</span></div>
      </header>
      <div class="dimension-body">
        <div class="stat-cards">
          <div class="stat-card"><span>最高分</span><strong>{{ score(dimension.maximum) }}</strong><small :title="dimension.highest_schools?.join('、')">{{ schoolNames(dimension.highest_schools) }}</small></div>
          <div class="stat-card"><span>最低分</span><strong>{{ score(dimension.minimum) }}</strong><small :title="dimension.lowest_schools?.join('、')">{{ schoolNames(dimension.lowest_schools) }}</small></div>
          <div class="stat-card"><span>标准差</span><strong>{{ score(dimension.std_dev) }}</strong><small>{{ dimension.count === 1 ? '单校数据，不判断校际差异' : '总体标准差' }}</small></div>
        </div>
        <div v-if="dimension.count" class="dimension-ranks">
          <div v-for="group in [{ key: 'top_schools', title: '前5所学校' }, { key: 'bottom_schools', title: '后5所学校' }]" :key="group.key">
            <h4>{{ dimension.label }}{{ group.title }}</h4>
            <table class="indicator-table rank-table"><thead><tr><th>排名</th><th>学校</th><th>得分</th></tr></thead><tbody>
              <tr v-for="school in dimension[group.key]" :key="school.school_id"><td :class="{ 'rank-red': group.key === 'top_schools' }">{{ school.rank }}</td><td>{{ school.school_name }}</td><td>{{ score(school.score) }}</td></tr>
            </tbody></table>
          </div>
        </div>
        <div class="secondary-block">
          <h4>所属二级指标得分情况</h4>
          <div class="table-scroll"><table class="indicator-table secondary-table">
            <thead><tr><th>所属二级指标</th><th>平均分</th><th>最高分</th><th>最低分</th><th>标准差</th></tr></thead>
            <tbody><tr v-for="child in dimension.secondary_indicators" :key="child.key">
              <td>{{ child.label }}</td><td><div class="mean-cell"><span class="score-track" aria-hidden="true"><span :style="{ width: `${(child.average ?? 0) * 20}%` }"></span></span><span>{{ score(child.average) }}</span></div></td>
              <td>{{ score(child.maximum) }}</td><td>{{ score(child.minimum) }}</td><td>{{ score(child.std_dev) }}</td>
            </tr></tbody>
          </table></div>
        </div>
        <div v-if="dimension.key === 'literacy'" class="literacy-radar-section">
          <h4>教师与学生数据素养雷达图</h4>
          <div class="literacy-radar-row">
            <div v-for="group in literacyRadarGroups" :key="group.key" class="literacy-radar-card">
              <h5>{{ group.label }}</h5>
              <div :ref="el => setRadarElement(group.key, el)" class="literacy-radar-chart" role="img" :aria-label="radarDescription(group)"></div>
              <div v-if="!group.complete" class="radar-missing">
                <p>暂无完整五维数据</p>
                <span v-for="point in group.points" :key="point.key">{{ point.label }}：{{ score(point.average) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="dimension.key === 'institution' || dimension.key === 'technology'" class="observation-charts">
          <figure v-for="group in dimension.secondary_indicators" :key="group.key" class="observation-chart">
            <figcaption>{{ group.label }}</figcaption>
            <div class="bar-unit">区域均分（分）</div>
            <div class="bar-plot">
              <div v-for="tick in [0, 1, 2, 3, 4, 5]" :key="tick" class="bar-gridline"
                   :style="{ bottom: tick * 20 + '%' }" aria-hidden="true"><span>{{ tick }}</span></div>
              <div v-for="point in group.observation_indicators" :key="point.key" class="bar-column">
                <div v-if="point.average != null" class="observation-bar" :style="{ height: point.average * 20 + '%' }">
                  <span class="bar-value">{{ score(point.average) }}</span>
                </div>
                <span v-else class="bar-pending">待补分</span>
                <span class="bar-category">{{ wrapObservationLabel(point.label) }}</span>
              </div>
            </div>
          </figure>
        </div>
        <div v-if="dimension.key === 'behavior'" class="behavior-charts">
          <div class="behavior-monitor">
            <h4>{{ behaviorMonitor.label }}</h4>
            <div :ref="el => setRadarElement('C1', el)" class="behavior-chart" role="img" :aria-label="radarDescription(behaviorMonitor)"></div>
          </div>
          <div class="behavior-effect">
            <h4>{{ behaviorRadar.label }}</h4>
            <div :ref="el => setRadarElement('C2', el)" class="behavior-chart" role="img" :aria-label="radarDescription(behaviorRadar)"></div>
            <div v-if="!behaviorRadar.complete" class="radar-missing">
              <p>暂无完整三维数据</p>
              <span v-for="point in behaviorRadar.points" :key="point.key">{{ point.label }}：{{ score(point.average) }}</span>
            </div>
          </div>
        </div>
        <div v-if="dimension.key === 'asset'" class="asset-visuals">
          <div class="asset-charts">
            <div class="asset-chart-panel">
              <h4>数据资产意识</h4>
              <div :ref="el => setRadarElement('D1', el)" class="behavior-chart" role="img" :aria-label="radarDescription(assetRadar)"></div>
              <div v-if="!assetRadar.complete" class="radar-missing">
                <p>暂无完整三维数据</p>
                <span v-for="point in assetRadar.points" :key="point.key">{{ point.label }}：{{ score(point.average) }}</span>
              </div>
            </div>
            <div class="asset-chart-panel">
              <h4>数据资产积累</h4>
              <div :ref="el => setRadarElement('D2', el)" class="behavior-chart" role="img" :aria-label="radarDescription(assetAccumulation)"></div>
            </div>
          </div>
          <div class="asset-volume-cards">
            <div class="asset-volume-card">
              <h5>数据资产总量</h5>
              <strong class="volume-total">{{ score(dimension.volume_summary?.total_gb) }} GB</strong>
              <p>区域内 {{ dimension.volume_summary?.school_count ?? 0 }} 所可统计学校的已统计数据合计</p>
              <div class="volume-track"><span class="volume-total-fill" :style="{ width: volumePercentage(dimension.volume_summary?.total_gb, 9000) + '%' }"></span></div>
              <div class="volume-scale"><span>0 GB</span><span>9000 GB</span></div>
            </div>
            <div class="asset-volume-card">
              <h5>人均数据资产量</h5>
              <strong class="volume-per-capita">{{ score(dimension.volume_summary?.per_capita_gb) }} GB</strong>
              <p>{{ dimension.volume_summary?.missing_population_count ? '纳入学校的师生人数不完整，暂无法计算人均量' : '按上述学校数据总量除以其教师和学生总人数计算' }}</p>
              <div class="volume-track"><span class="volume-per-capita-fill" :style="{ width: volumePercentage(dimension.volume_summary?.per_capita_gb, 40) + '%' }"></span></div>
              <div class="volume-scale"><span>0 GB</span><span>40 GB</span></div>
            </div>
          </div>
        </div>
        <div class="dimension-advice">
          <h4><span class="advice-icon" aria-hidden="true">!</span>针对{{ dimension.label }}维度的发展建议</h4>
          <p>{{ dimension.count ? (suggestions[dimension.key] || (loading ? '正在生成发展建议…' : '发展建议暂未获取，请刷新重试。')) : '暂无有效评估数据，暂不作发展判断；建议先完成数据采集与核验。' }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
const props = defineProps({ statistics: { type: Array, default: () => [] }, suggestions: { type: Object, default: () => ({}) }, loading: Boolean, note: String, secondaryNote: String, legacyCount: Number, developmentSummary: String })
const displayNote = computed(() => (props.note || '').replace('；同分并列位次（1、1、3）', ''))
const colors = {
  literacy: ['#709ce0', '#f0f5fd'], institution: ['#6eb7b2', '#eff9f8'],
  behavior: ['#c8a15d', '#fcf8ef'], asset: ['#a18fc7', '#f7f4fc'], technology: ['#88c391', '#f3fcf6']
}
const palette = key => ({ '--dimension-color': colors[key]?.[0] || '#88c391', '--dimension-light': colors[key]?.[1] || '#f3fcf6' })
function score(value) { return value != null && Number.isFinite(Number(value)) ? Number(value).toFixed(2) : '—' }
function volumePercentage(value, maximum) {
  return value == null ? 0 : Math.min(100, Math.max(0, value / maximum * 100))
}
function wrapObservationLabel(label) {
  return label.replace(/(工作小组|运行情况|管理人员|与培训情况|制度类文件|指导类文件|合规与认证|事件记录)$/, '\n$1')
}
function schoolNames(names = []) { return names.length ? `${names.slice(0, 2).join('、')}${names.length > 2 ? ` 等${names.length}所` : ''}` : '暂无有效数据' }

const radarAxes = ['数据意识与思维', '数据知识与技能', '数据评价与交流', '数据应用与创新', '数据伦理与隐私']
const literacyRadarGroups = computed(() => {
  const children = props.statistics.find(item => item.key === 'literacy')?.secondary_indicators || []
  return [
    { key: 'A1', prefix: 'A1', label: '教师数据素养', color: '#639efa' },
    { key: 'A2', prefix: 'A3', label: '学生数据素养', color: '#909399' }
  ].map(group => {
    const observations = children.find(child => child.key === group.key)?.observation_indicators || []
    const points = radarAxes.map((label, index) => {
      const key = `${group.prefix}${index + 1}`
      const value = observations.find(point => point.key === key)?.average
      const average = typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 5 ? value : null
      return { key, label, average }
    })
    return { ...group, points, complete: points.every(point => point.average !== null) }
  })
})
const radarDescription = group => `${group.label}，区域学校均分（满分5分）：${group.points.map(point => `${point.label}${score(point.average)}`).join('，')}`
function observationGroup(dimension, key, label, axes) {
  const children = props.statistics.find(item => item.key === dimension)?.secondary_indicators || []
  const observations = children.find(child => child.key === key)?.observation_indicators || []
  const points = axes.map(([code, name]) => {
    const value = observations.find(point => point.key === code)?.average
    const average = typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 5 ? value : null
    return { key: code, label: name, average }
  })
  return { key, label, color: '#4096ef', points, complete: points.every(point => point.average !== null) }
}
const behaviorMonitor = computed(() => observationGroup('behavior', 'C1', '数据行为监测', [
  ['C11', '教师数据行为'], ['C12', '学生数据行为']
]))
const behaviorRadar = computed(() => observationGroup('behavior', 'C2', '数据应用成效', [
  ['C21', '数据应用特色成果'], ['C23', '教师主观评价'], ['C22', '数据应用社会影响']
]))
const assetRadar = computed(() => observationGroup('asset', 'D1', '数据资产意识', [
  ['D11', '数据资产价值意识'], ['D12', '数据资产应用意识'], ['D13', '数据资产治理意识']
]))
const assetAccumulation = computed(() => observationGroup('asset', 'D2', '数据资产积累', [
  ['D21', '数据资产总量'], ['D22', '人均数据资产量']
]))
const radarGroups = computed(() => [...literacyRadarGroups.value, behaviorRadar.value, assetRadar.value])
const barGroups = computed(() => [behaviorMonitor.value, assetAccumulation.value])
const radarElements = new Map()
let radarCharts = []
let resizeObserver
let mounted = false
function setRadarElement(key, element) {
  if (element) radarElements.set(key, element)
  else radarElements.delete(key)
}
function clearRadarCharts() {
  resizeObserver?.disconnect()
  radarCharts.forEach(({ chart }) => chart.dispose())
  radarCharts = []
}
function renderRadarCharts() {
  if (!mounted) return
  clearRadarCharts()
  radarGroups.value.forEach(group => {
    const element = radarElements.get(group.key)
    if (!element) return
    const chart = echarts.init(element, null, { renderer: 'canvas' })
    const radius = () => Math.max(20, Math.min(95, (element.clientWidth - 180) / 2))
    chart.setOption({
      animation: false,
      radar: {
        indicator: group.points.map(point => ({ name: point.label, min: 0, max: 5 })),
        center: ['50%', '50%'], radius: radius(), splitNumber: 5,
        axisName: { color: '#777', fontSize: 10 },
        splitArea: { show: false }, splitLine: { lineStyle: { color: '#dfe5ef' } },
        axisLine: { lineStyle: { color: '#bfc4cc' } }
      },
      series: group.complete ? [{
        type: 'radar', symbol: 'circle', symbolSize: 8,
        itemStyle: { color: group.color }, lineStyle: { color: group.color, width: 2 },
        areaStyle: { color: group.color, opacity: 0.3 },
        label: { show: true, color: '#222', fontSize: 12, formatter: params => score(params.value) },
        data: [{ name: group.label, value: group.points.map(point => point.average) }]
      }] : []
    })
    // Recompute the radius as well as the canvas when the report width changes.
    radarCharts.push({ chart, resize: () => { chart.resize(); chart.setOption({ radar: { radius: radius() } }) } })
    resizeObserver?.observe(element)
  })
  barGroups.value.forEach(group => {
    const element = radarElements.get(group.key)
    if (!element) return
    const chart = echarts.init(element, null, { renderer: 'canvas' })
    chart.setOption({
      animation: false,
      grid: { left: group.key === 'D2' ? 108 : 96, right: 58, top: 20, bottom: 40 },
      xAxis: {
        type: 'value', min: 0, max: 5, interval: 1, name: '得分',
        axisLabel: { color: '#555' }, splitLine: { lineStyle: { color: '#dfe5ef' } }
      },
      yAxis: {
        type: 'category', inverse: true, data: group.points.map(point => point.label),
        axisLabel: { color: '#444', fontSize: 12 }, axisTick: { show: false },
        axisLine: { show: true, lineStyle: { color: '#909399' } }
      },
      series: [{
        type: 'bar', barMaxWidth: 55,
        data: group.points.map((point, index) => ({
          value: point.average,
          itemStyle: { color: ['#679bf2', '#86bb4c'][index] }
        })),
        label: { show: true, position: 'right', color: '#444', formatter: params => score(params.value) + '分' },
        markPoint: {
          symbolSize: 0,
          data: group.points.flatMap((point, index) => point.average === null ? [{ coord: [2.5, index] }] : []),
          label: { show: true, formatter: '待补分', position: 'inside', color: '#64748b' }
        }
      }]
    })
    radarCharts.push({ chart, resize: () => chart.resize() })
    resizeObserver?.observe(element)
  })
}
onMounted(() => {
  mounted = true
  resizeObserver = new ResizeObserver(() => radarCharts.forEach(({ resize }) => resize()))
  renderRadarCharts()
})
watch([radarGroups, barGroups], renderRadarCharts, { flush: 'post' })
onBeforeUnmount(() => { mounted = false; clearRadarCharts() })
</script>

<style scoped>
.dimension-analysis-group { margin: 38px 0; color: #334155; }
.analysis-heading { text-align: center; color: #284867; font-size: 22px; font-weight: 900; margin: 0 0 16px; }
.analysis-note { font-size: 12px; line-height: 1.8; color: #64748b; margin: 6px 0 12px; }
.development-summary-box {
  background: #f8fbff;
  border: 1px solid #e3ebf5;
  border-radius: 10px;
  padding: 18px 22px;
  color: #475569;
  font-size: 15px;
  line-height: 1.9;
  text-indent: 2em;
  text-align: justify;
  overflow-wrap: break-word;
}
.dimension-analysis { border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; margin-top: 26px; background: white; }
.dimension-banner { display: flex; align-items: center; justify-content: space-between; gap: 16px; background: var(--dimension-color); color: white; padding: 18px 24px; }
.dimension-banner h3 { font-size: 25px; font-weight: 900; line-height: 1.2; margin: 0; }
.banner-score { text-align: right; display: flex; flex-direction: column; gap: 6px; }
.banner-score strong { font-size: 34px; font-weight: 900; line-height: 1; }
.banner-score span { font-size: 14px; font-weight: 700; }
.dimension-body { padding: 20px 24px 24px; }
.stat-cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-bottom: 23px; }
.stat-card { display: flex; flex-direction: column; gap: 4px; align-items: center; justify-content: flex-start; padding: 14px 10px; border-radius: 8px; background: var(--dimension-light); text-align: center; }
.stat-card>span { font-size: 13px; font-weight: 700; color: var(--dimension-color); }
.stat-card strong { font-size: 25px; font-weight: 900; line-height: 1; color: var(--dimension-color); }
.stat-card small { color: #64748b; font-size: 12px; font-weight: 600; line-height: 1.6; overflow-wrap: anywhere; }
.dimension-ranks { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin: 22px 0; }
h4 { margin: 0 0 10px; font-size: 15px; font-weight: 900; }
.indicator-table { border-collapse: collapse; width: 100%; font-size: 14px; font-variant-numeric: tabular-nums; }
.indicator-table th { background: #edf2f8; font-weight: 800; color: #3e5673; }
.indicator-table td { font-weight: 600; }
.indicator-table th,.indicator-table td { text-align: right; padding: 12px 14px; border-bottom: 1px solid #edf1f5; line-height: 1.6; }
.rank-table td:last-child { font-weight: 900; color: var(--dimension-color); }
.rank-table td.rank-red { color: #ef4444; font-weight: 900; }
.indicator-table th:first-child,.indicator-table td:first-child { text-align: left; }
.rank-table th:nth-child(2),.rank-table td:nth-child(2) { text-align: left; }
.rank-table th:first-child,.rank-table td:first-child { width: 64px; min-width: 64px; white-space: nowrap; }
.secondary-block { margin: 25px 0; }.mean-cell { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }.score-track { width: 65px; height: 5px; background: #e7eef9; border-radius: 5px; overflow: hidden; }.score-track>span { display: block; background: #4d7fca; height: 100%; }
.dimension-advice { padding: 16px; background: #eef7fe; border-left: 3px solid #6aa5df; border-radius: 5px; }.dimension-advice h4 { color: #294f76; }.dimension-advice p { margin: 0; padding: 14px; background: white; line-height: 1.9; font-size: 14px; white-space: pre-line; border-radius: 4px; }
.table-scroll { overflow-x: auto; }
.advice-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 15px;
  height: 15px;
  box-sizing: border-box;
  margin-right: 8px;
  border: 1.5px solid currentColor;
  border-radius: 50%;
  color: #2563eb;
  font-size: 11px;
  font-weight: 900;
  line-height: 1;
  vertical-align: middle;
}
.literacy-radar-section { margin: 28px 0; break-inside: avoid; }
.literacy-radar-section > h4 { text-align: center; font-size: 20px; color: #222; margin-bottom: 18px; }
.literacy-radar-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 30px; }
.literacy-radar-card { min-width: 0; background: #f7f7fa; border-radius: 10px; padding: 20px 8px 6px; }
.literacy-radar-card h5 { text-align: center; margin: 0; font-size: 14px; font-weight: 700; color: #444; }
.literacy-radar-chart { width: 100%; height: 270px; }
.radar-missing { padding: 0 12px 14px; color: #64748b; font-size: 12px; line-height: 1.8; text-align: center; }
.radar-missing p { margin: 0 0 4px; }
.radar-missing span { display: block; }
.asset-visuals { background: #eff5fe; padding: 18px 14px; margin: 28px 0; border-radius: 8px; }
.asset-charts, .asset-volume-cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; }
.asset-chart-panel { min-width: 0; break-inside: avoid; }
.asset-chart-panel h4 { text-align: center; color: #222; font-size: 18px; margin: 4px 0 12px; }
.asset-volume-cards { margin-top: 20px; }
.asset-volume-card { background: white; border-radius: 10px; padding: 22px 18px; text-align: center; break-inside: avoid; }
.asset-volume-card h5 { color: #909399; font-size: 15px; font-weight: 500; margin: 0 0 18px; }
.asset-volume-card strong { display: block; font-size: 30px; font-weight: 800; overflow-wrap: anywhere; }
.volume-total { color: #86bb4c; }.volume-per-capita { color: #e47470; }
.asset-volume-card p { font-size: 12px; line-height: 1.6; color: #909399; min-height: 38px; margin: 14px 0; }
.volume-track { height: 12px; background: #ebeef5; border-radius: 8px; overflow: hidden; }
.volume-track span { display: block; height: 100%; border-radius: inherit; }
.volume-total-fill { background: #86bb4c; }.volume-per-capita-fill { background: #e47470; }
.volume-scale { display: flex; justify-content: space-between; color: #909399; font-size: 12px; margin-top: 8px; }
@media (max-width: 760px) { .asset-charts, .asset-volume-cards { grid-template-columns: 1fr; } }
.behavior-charts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; margin: 28px 0; break-inside: avoid; }
.behavior-monitor, .behavior-effect { min-width: 0; padding: 18px 8px 8px; border-radius: 8px; }
.behavior-monitor { background: #eff5fe; }
.behavior-effect { background: #f7f7fa; }
.behavior-charts h4 { text-align: center; color: #444; font-size: 17px; margin-bottom: 10px; }
.behavior-chart { height: 280px; width: 100%; }
@media (max-width: 760px) { .behavior-charts { grid-template-columns: 1fr; } }
.observation-charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 22px; margin: 28px 0; }
.observation-chart { min-width: 0; margin: 0; padding: 0 8px 58px; break-inside: avoid; }
.observation-chart figcaption { text-align: center; font-size: 17px; font-weight: 800; color: #30343d; }
.bar-unit { margin: 14px 0 18px; font-size: 12px; color: #64748b; }
.bar-plot { position: relative; display: flex; height: 210px; margin-left: 22px; }
.bar-gridline { position: absolute; left: 0; right: 0; height: 1px; background: #dfe5ef; }
.bar-gridline:first-child { background: #909399; }
.bar-gridline span { position: absolute; right: calc(100% + 6px); top: -8px; line-height: 16px; color: #64748b; font-size: 12px; }
.bar-column { position: relative; flex: 1; display: flex; align-items: flex-end; justify-content: center; min-width: 0; }
.observation-bar { position: relative; width: 60%; max-width: 68px; background: #679bf2; }
.bar-column:last-child .observation-bar { background: #909399; }
.bar-value { position: absolute; bottom: 100%; left: 0; right: 0; text-align: center; padding-bottom: 3px; font-size: 14px; color: #30343d; }
.bar-pending { position: absolute; top: 50%; transform: translateY(-50%); }
.bar-category { position: absolute; top: 100%; padding-top: 6px; width: 100%; text-align: center; line-height: 1.4; white-space: pre-line; overflow-wrap: anywhere; }
.bar-pending, .bar-category { color: #64748b; font-size: 13px; }
@media print { .bar-gridline, .observation-bar { print-color-adjust: exact; } }
@media (max-width: 760px) { .literacy-radar-row { grid-template-columns: 1fr; gap: 16px; } }
@media (max-width: 650px) { .dimension-body { padding: 14px; }.dimension-ranks { grid-template-columns: 1fr; }.stat-cards { gap: 8px; }.secondary-table { min-width: 560px; }.dimension-banner { padding: 16px; } }
@media print { .dimension-banner,.stat-card { print-color-adjust: exact; }.dimension-banner,.stat-cards,.secondary-block,.dimension-advice { break-inside: avoid; } }
</style>
