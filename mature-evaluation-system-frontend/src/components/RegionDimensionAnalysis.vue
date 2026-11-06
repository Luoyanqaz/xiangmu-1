<template>
  <div class="dimension-analysis-group">
    <h2 class="analysis-heading">各一级指标及其二级指标分析</h2>
    <p class="analysis-note">{{ note }}</p>
    <p v-if="legacyCount" class="analysis-note">{{ secondaryNote }}</p>
    <section v-for="dimension in statistics" :key="dimension.key" class="dimension-analysis" :style="palette(dimension.key)">
      <header class="dimension-banner">
        <div><h3>{{ dimension.label }}维度分析</h3><p>有效得分学校 {{ dimension.count }} 所<span v-if="dimension.missing_count"> · 缺失 {{ dimension.missing_count }} 所</span></p></div>
        <div class="banner-score"><strong>{{ score(dimension.average) }}</strong><span>平均分</span></div>
      </header>
      <div class="dimension-body">
        <p class="dimension-description">{{ dimension.description }}</p>
        <div class="stat-cards">
          <div class="stat-card"><span>最高分</span><strong>{{ score(dimension.maximum) }}</strong><small :title="dimension.highest_schools?.join('、')">{{ schoolNames(dimension.highest_schools) }}</small></div>
          <div class="stat-card"><span>最低分</span><strong>{{ score(dimension.minimum) }}</strong><small :title="dimension.lowest_schools?.join('、')">{{ schoolNames(dimension.lowest_schools) }}</small></div>
          <div class="stat-card"><span>标准差</span><strong>{{ score(dimension.std_dev) }}</strong><small>{{ dimension.count === 1 ? '单校数据，不判断校际差异' : '总体标准差' }}</small></div>
        </div>
        <div v-if="dimension.count" class="dimension-ranks">
          <div v-for="group in [{ key: 'top_schools', title: '前5所学校' }, { key: 'bottom_schools', title: '后5所学校' }]" :key="group.key">
            <h4>{{ dimension.label }}{{ group.title }}</h4>
            <table class="indicator-table rank-table"><thead><tr><th>位次</th><th>学校</th><th>得分</th></tr></thead><tbody>
              <tr v-for="school in dimension[group.key]" :key="school.school_id"><td>{{ school.rank }}</td><td>{{ school.school_name }}</td><td>{{ score(school.score) }}</td></tr>
            </tbody></table>
          </div>
        </div>
        <div class="secondary-block">
          <h4>所属二级指标得分情况</h4>
          <div class="table-scroll"><table class="indicator-table secondary-table">
            <thead><tr><th>所属二级指标</th><th>平均分</th><th>最高分</th><th>最低分</th><th>标准差</th><th>有效学校数</th></tr></thead>
            <tbody><tr v-for="child in dimension.secondary_indicators" :key="child.key">
              <td>{{ child.label }}</td><td><div class="mean-cell"><span class="score-track" aria-hidden="true"><span :style="{ width: `${(child.average ?? 0) * 20}%` }"></span></span><span>{{ score(child.average) }}</span></div></td>
              <td>{{ score(child.maximum) }}</td><td>{{ score(child.minimum) }}</td><td>{{ score(child.std_dev) }}</td><td>{{ child.count }}</td>
            </tr></tbody>
          </table></div>
          <div class="secondary-descriptions"><p v-for="child in dimension.secondary_indicators" :key="child.key">{{ child.description }}</p></div>
        </div>
        <div class="dimension-advice">
          <h4>针对{{ dimension.label }}维度的发展建议 <span class="advice-source">{{ sourceLabel }}</span></h4>
          <p>{{ dimension.count ? (suggestions[dimension.key] || (loading ? '正在生成发展建议…' : '发展建议暂未获取，请刷新重试。')) : '暂无有效评估数据，暂不作发展判断；建议先完成数据采集与核验。' }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ statistics: { type: Array, default: () => [] }, suggestions: { type: Object, default: () => ({}) }, loading: Boolean, mode: String, note: String, secondaryNote: String, legacyCount: Number })
const sourceLabel = computed(() => props.loading ? '生成中' : props.mode === 'ai' ? 'AI建议' : props.mode === 'fallback' ? '基于统计数据的规则建议' : '')
const colors = {
  literacy: ['#709ce0', '#f0f5fd'], institution: ['#6eb7b2', '#eff9f8'],
  behavior: ['#c8a15d', '#fcf8ef'], asset: ['#a18fc7', '#f7f4fc'], technology: ['#88c391', '#f3fcf6']
}
const palette = key => ({ '--dimension-color': colors[key]?.[0] || '#88c391', '--dimension-light': colors[key]?.[1] || '#f3fcf6' })
function score(value) { return value != null && Number.isFinite(Number(value)) ? Number(value).toFixed(2) : '—' }
function schoolNames(names = []) { return names.length ? `${names.slice(0, 2).join('、')}${names.length > 2 ? ` 等${names.length}所` : ''}` : '暂无有效数据' }
</script>

<style scoped>
.dimension-analysis-group { margin: 38px 0; color: #334155; }
.analysis-heading { text-align: center; color: #284867; font-size: 23px; margin: 0 0 16px; }
.analysis-note { font-size: 12px; line-height: 1.8; color: #64748b; margin: 6px 0 12px; }
.dimension-analysis { border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; margin-top: 26px; background: white; }
.dimension-banner { display: flex; align-items: center; justify-content: space-between; gap: 16px; background: var(--dimension-color); color: white; padding: 18px 24px; }
.dimension-banner h3 { font-size: 20px; margin: 0 0 6px; }.dimension-banner p { margin: 0; font-size: 12px; }
.banner-score { text-align: right; display: flex; flex-direction: column; gap: 2px; }.banner-score strong { font-size: 30px; }.banner-score span { font-size: 12px; }
.dimension-body { padding: 20px 24px 24px; }.dimension-description { margin: 0 0 18px; font-size: 14px; line-height: 1.9; }
.stat-cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-bottom: 23px; }
.stat-card { display: flex; flex-direction: column; gap: 4px; align-items: center; justify-content: flex-start; padding: 14px 10px; border-radius: 8px; background: var(--dimension-light); text-align: center; }
.stat-card>span { font-size: 12px; color: #475569; }.stat-card strong { font-size: 25px; color: #34576d; }.stat-card small { color: #64748b; font-size: 11px; line-height: 1.6; overflow-wrap: anywhere; }
.dimension-ranks { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin: 22px 0; }
h4 { margin: 0 0 10px; font-size: 14px; font-weight: 600; }.indicator-table { border-collapse: collapse; width: 100%; font-size: 12px; font-variant-numeric: tabular-nums; }
.indicator-table th { background: #edf2f8; font-size: 11px; color: #3e5673; }.indicator-table th,.indicator-table td { text-align: right; padding: 10px 8px; border-bottom: 1px solid #edf1f5; line-height: 1.6; }
.indicator-table th:first-child,.indicator-table td:first-child { text-align: left; }.rank-table th:nth-child(2),.rank-table td:nth-child(2) { text-align: left; }.rank-table th:first-child { width: 40px; }
.secondary-block { margin: 25px 0; }.mean-cell { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }.score-track { width: 65px; height: 5px; background: #e7eef9; border-radius: 5px; overflow: hidden; }.score-track>span { display: block; background: #4d7fca; height: 100%; }
.secondary-descriptions { color: #64748b; font-size: 12px; line-height: 1.8; margin-top: 12px; }.secondary-descriptions p { margin: 4px 0; }
.dimension-advice { padding: 16px; background: #eef7fe; border-left: 3px solid #6aa5df; border-radius: 5px; }.dimension-advice h4 { color: #294f76; }.dimension-advice p { margin: 0; padding: 14px; background: white; line-height: 1.9; font-size: 13px; white-space: pre-line; border-radius: 4px; }
.advice-source { font-size: 11px; color: #64748b; font-weight: normal; margin-left: 8px; }.table-scroll { overflow-x: auto; }
@media (max-width: 650px) { .dimension-body { padding: 14px; }.dimension-ranks { grid-template-columns: 1fr; }.stat-cards { gap: 8px; }.secondary-table { min-width: 560px; }.dimension-banner { padding: 16px; } }
@media print { .dimension-banner,.stat-card { print-color-adjust: exact; }.dimension-banner,.stat-cards,.secondary-block,.dimension-advice { break-inside: avoid; } }
</style>
