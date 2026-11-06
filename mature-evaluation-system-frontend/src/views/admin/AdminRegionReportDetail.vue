<template>
  <div class="region-report-page">
    <!-- 顶部操作区（不参与打印） -->
    <div class="toolbar no-print">
      <el-button @click="reloadAll" :loading="loading">刷新</el-button>
      <el-button type="primary" @click="exportPDF" :loading="exporting" :disabled="loading || aiLoading">
        导出 PDF
      </el-button>
    </div>

    <div ref="reportRef" class="report-shell">
      <!-- 标题区 -->
      <section class="report-header">
        <h1 class="report-title">
          {{ regionFullName || "区域" }}数据文化成熟度评估报告
        </h1>
          <div class="report-info-line">
            <div class="info-item">
              <span class="info-icon pin">📍</span>
              <span class="info-label">区域名称：</span>
              <span class="info-value">{{ regionFullName || "江南智慧教育示范区" }}</span>
            </div>

            <div class="info-item">
              <span class="info-icon calendar">🗓️</span>
              <span class="info-label">评估时间：</span>
              <span class="info-value">{{ evaluationTime }}</span>
            </div>

            <div class="info-item">
              <span class="info-icon school">🏫</span>
              <span class="info-label">区域参评学校：</span>
              <span class="info-value">
                {{ summary.school_count || latestSchools.length || 0 }} 所（小学/初中/一贯制）
              </span>
            </div>
          </div>
        </section>
        <div class="overview-card">
          <div class="overview-text">
            <p>
              本报告旨在帮助您全面了解区域各学校数据文化建设情况。
              <strong>数据文化</strong>是指学校在数据使用和管理方面的制度、规范、实践和价值观的集合；
              而数据文化成熟度则是学校在数据使用、管理和价值实现方面的成熟程度。
            </p>
            <p>
              平台基于学校填报的多维度数据，通过科学的评估规则，并辅助于
              <strong>DeepSeek</strong> 大模型进行智能评估，
              准确识别学校数据文化的建设水平与现实问题，以促进学校数据使用、管理和价值实现，
              推动学校数据治理能力的提升。本报告包括以下五个核心分析维度：
            </p>
          </div>

          <div class="overview-divider"></div>

          <div class="core-title">
五大核心分析维度
          </div>

          <div class="core-grid">
            <div
              v-for="item in dimensionCards"
              :key="item.key"
              class="core-card"
            >
              
              <div class="core-name">
                {{ item.index }}. {{ item.name }}
              </div>

              <div class="core-desc">
                {{ item.text }}
              </div>
            </div>
          </div>
        </div>

      <!-- 一、区域成熟度等级分布 -->
      <!-- 一、区域成熟度等级分布 -->
      <section class="maturity-section">
        <div class="maturity-title-wrap">
          <div class="maturity-title">区域成熟度等级分布</div>
          <div class="maturity-line"></div>
        </div>

        <div class="maturity-chart-row">
          <div class="maturity-chart-card">
            <div class="maturity-chart-title">成熟度等级占比</div>
            <div ref="pieRef" class="maturity-chart-box"></div>
          </div>

          <div class="maturity-chart-card">
            <div class="maturity-chart-title">成熟度等级学校数量</div>
            <div ref="barRef" class="maturity-chart-box"></div>
          </div>
        </div>

        <div class="maturity-table-wrap">
          <table class="maturity-table">
            <thead>
              <tr>
                <th>成熟度等级</th>
                <th>分数区间</th>
                <th>学校数量</th>
                <th>占比</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in levelDistribution" :key="row.key">
                <td class="maturity-level-cell">
                  <span
                    class="maturity-pill"
                    :style="{ background: row.light, color: row.color }"
                  >
                    {{ row.label }}
                  </span>
                </td>
                <td>{{ row.range }}</td>
                <td class="maturity-count">{{ row.count }} 所</td>
                <td>{{ row.ratio }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 二、区域整体数据表现 -->
      <!-- 二、区域整体数据表现 -->
      <section class="overall-section">
        <div class="overall-title-wrap">
          <div class="overall-title">区域整体数据表现</div>
          <div class="overall-line"></div>
        </div>

        <!-- 上半部分：雷达图 + 右侧分数卡 -->
        <div class="overall-top">
          <div class="overall-radar-area">
            <div class="overall-radar-title">区域整体五维度得分</div>

            <div class="radar-wrapper">
              <div ref="radarRef" class="overall-radar-chart"></div>

              <!-- 只显示分值，不再重复显示维度名称，避免和雷达图文字重叠 -->
              <div class="radar-score-tag tag-literacy">
                {{ formatScore(dimensionAverage.literacy) }}
              </div>
              <div class="radar-score-tag tag-institution">
                {{ formatScore(dimensionAverage.institution) }}
              </div>
              <div class="radar-score-tag tag-behavior">
                {{ formatScore(dimensionAverage.behavior) }}
              </div>
              <div class="radar-score-tag tag-asset">
                {{ formatScore(dimensionAverage.asset) }}
              </div>
              <div class="radar-score-tag tag-technology">
                {{ formatScore(dimensionAverage.technology) }}
              </div>
            </div>

            <div class="overall-radar-legend">
              <span class="legend-box"></span>
              <span>区域平均分</span>
            </div>
          </div>

          <div class="overall-score-list">
            <div class="overall-score-card highest">
              <div class="score-label">最高分</div>
              <div class="score-value">{{ formatScore(highestScore) }}</div>
              <div class="score-school">{{ highestSchoolName }}</div>
            </div>

            <div class="overall-score-card average">
              <div class="score-label">平均分</div>
              <div class="score-value">{{ formatScore(regionAverageScore) }}</div>
              <div class="score-school">区域整体水平</div>
            </div>

            <div class="overall-score-card lowest">
              <div class="score-label">最低分</div>
              <div class="score-value">{{ formatScore(lowestScore) }}</div>
              <div class="score-school">{{ lowestSchoolName }}</div>
            </div>
          </div>
        </div>

        <!-- 下半部分：前5名 + 后5名 -->
        <div class="overall-rank-area">
          <div class="overall-rank-card top">
            <div class="overall-rank-title">
              <span class="rank-icon up">↑</span>
              <span>总分前5名</span>
            </div>

            <table class="overall-rank-table top-table">
              <thead>
                <tr>
                  <th>排名</th>
                  <th>学校名称</th>
                  <th>等级</th>
                  <th>总分</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in topSchools"
                  :key="`top-${row.assessment_id}`"
                  :class="`top-rank-${row.rank}`"
                >
                  <td>{{ row.rank }}</td>
                  <td>{{ row.school_name }}</td>
                  <td>
                    <span class="level-mini-tag purple">
                      {{ maturityLabel(row.maturity_level) }}
                    </span>
                  </td>
                  <td class="top-score">{{ formatScore(row.total_score) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="overall-rank-card bottom">
            <div class="overall-rank-title">
              <span class="rank-icon down">↓</span>
              <span>总分后5名</span>
            </div>

            <table class="overall-rank-table bottom-table">
              <thead>
                <tr>
                  <th>排名</th>
                  <th>学校名称</th>
                  <th>等级</th>
                  <th>总分</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in bottomSchools"
                  :key="`bottom-${row.assessment_id}`"
                >
                  <td>{{ row.rank }}</td>
                  <td>{{ row.school_name }}</td>
                  <td>
                    <span class="level-mini-tag red">
                      {{ maturityLabel(row.maturity_level) }}
                    </span>
                  </td>
                  <td class="bottom-score">{{ formatScore(row.total_score) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 三、分层学校分析 -->
      <!-- 三、各成熟度等级学校分析 -->
        <section
          v-for="section in orderedLevelAnalysis"
          :key="section.key"
          class="level-analysis-section"
          :class="section.key"
        >
          <!-- 顶部彩色标题栏 -->
          <div class="level-analysis-header">
            <div class="level-header-left">
              <div class="level-title">{{ section.label }}学校分析</div>
              <div class="level-subtitle">
                得分区间 {{ section.range }} · 共 {{ section.count }} 所学校
              </div>
            </div>

            <div class="level-header-right">
              <div class="level-avg-score">{{ formatScore(section.avg_score) }}</div>
              <div class="level-avg-label">平均分</div>
            </div>
          </div>

          <!-- 三个统计卡片 -->
          <div class="level-stat-row">
            <div class="level-stat-card">
              <div class="level-stat-label">最高分</div>
              <div class="level-stat-value">{{ formatScore(section.highest_score) }}</div>
              <div class="level-stat-school">{{ section.highest_school || "-" }}</div>
            </div>

            <div class="level-stat-card">
              <div class="level-stat-label">最低分</div>
              <div class="level-stat-value">{{ formatScore(section.lowest_score) }}</div>
              <div class="level-stat-school">{{ section.lowest_school || "-" }}</div>
            </div>

            <div class="level-stat-card">
              <div class="level-stat-label">标准差</div>
              <div class="level-stat-value">{{ formatScore(section.std_score) }}</div>
              <div class="level-stat-school">离散程度较{{ section.std_score >= 1 ? "大" : "小" }}</div>
            </div>
          </div>

          <!-- 前5名 / 后5名 -->
          <div class="level-rank-layout">
            <div class="level-rank-block">
              <div class="level-rank-title">{{ section.label }}前5名</div>

              <table class="level-rank-table">
                <thead>
                  <tr>
                    <th>排名</th>
                    <th>学校</th>
                    <th>得分</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in section.top_schools"
                    :key="`${section.key}-top-${row.assessment_id}`"
                  >
                    <td :class="{ 'rank-red': row.rank <= 3 }">{{ row.rank }}</td>
                    <td>{{ row.school_name }}</td>
                    <td class="level-table-score">{{ formatScore(row.total_score) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="level-rank-block">
              <div class="level-rank-title">{{ section.label }}后5名</div>

              <table class="level-rank-table">
                <thead>
                  <tr>
                    <th>排名</th>
                    <th>学校</th>
                    <th>得分</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in section.bottom_schools"
                    :key="`${section.key}-bottom-${row.assessment_id}`"
                  >
                    <td>{{ row.rank }}</td>
                    <td>{{ row.school_name }}</td>
                    <td class="level-table-score weak">{{ formatScore(row.total_score) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- AI 建议 -->
          <div class="level-ai-box">
            <div class="level-ai-title">
              <span class="ai-info-icon">ⓘ</span>
              针对{{ section.label }}学校的发展建议
            </div>

            <div class="level-ai-content">
              {{ getLevelSuggestion(section.key) }}
            </div>
          </div>
        </section>
      
      <!-- 四、区域发展建议 -->
      <!-- 四、区域发展建议 -->
<RegionDimensionAnalysis
  :statistics="reportStatistics.dimension_statistics || []"
  :suggestions="aiSuggestions.dimension_suggestions || {}"
  :loading="aiLoading"
  :mode="aiSuggestions.suggestion_mode"
  :note="reportStatistics.statistics_note"
  :secondary-note="reportStatistics.secondary_note"
  :legacy-count="reportStatistics.legacy_assessment_count || 0"
/>
<section class="development-section">
  <div class="development-title-wrap">
    <div class="development-title">
      区域发展建议
    </div>
  </div>

  <div class="development-card">
    <!-- 顶部总结 -->
    <div class="development-summary-box">
      {{ defaultDevelopmentSummary }}
    </div>

    <!-- 五条建议 -->
<div class="development-list">
  <div
    v-for="item in developmentItems"
    :key="item.index"
    class="development-item"
    :class="`development-item-${item.index}`"
  >
    <div class="development-content">
      <div class="development-item-title">
        <span class="development-title-index">
          {{ item.index }}.
        </span>
        <span>{{ item.dimension }} —— {{ item.title }}</span>
      </div>

      <div class="development-item-text">
        {{ item.content }}
      </div>
    </div>
  </div>
</div>

    <!-- 总体结论 -->
<div class="development-final-box">
  <div class="development-final-title">
    总体战略目标
  </div>

  <div class="development-final-text">
    {{ defaultConclusion }}
  </div>
</div>
  </div>
        <div class="report-footer">
        <p class="footer-note">-本报告由中小学校数据文化成熟度评估监测系统自动生成-</p>
      </div>
</section>
    </div>

  </div>
</template>

<script setup>
import RegionDimensionAnalysis from "@/components/RegionDimensionAnalysis.vue";
import { computed, nextTick, onMounted, onUnmounted, ref } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import * as echarts from "echarts";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import { apiGet, apiPost } from "@/utils/api";
import { useRegionStore } from "@/stores/region";

const regionStore = useRegionStore();
const route = useRoute();

const isAdminViewMode = computed(() => true)

const loading = ref(false);
const aiLoading = ref(false);
const exporting = ref(false);
const reportRef = ref(null);

const region = ref(null);
const queryRegion = computed(() => {
  return {
    region_id: route.query.region_id || "",
    province: route.query.province || "",
    city: route.query.city || "",
    district: route.query.district || ""
  };
});
const summary = ref({});
const assessments = ref([]);
const reportStatistics = ref({});
const aiSuggestions = ref({
  level_suggestions: {
    initial: "",
    growing: "",
    mature: "",
    leading: ""
  },
  development: {
    summary: "",
    items: [],
    conclusion: ""
  }
});

const pieRef = ref(null);
const barRef = ref(null);
const radarRef = ref(null);

let chartInstances = [];

const levelMeta = [
  {
    key: "initial",
    label: "初始级",
    range: "[0.0, 1.5]",
    color: "#f27b7b",
    light: "#f9dede"
  },
  {
    key: "growing",
    label: "成长级",
    range: "[1.5, 3.0]",
    color: "#f0ab4d",
    light: "#fae7c9"
  },
  {
    key: "mature",
    label: "成熟级",
    range: "[3.0, 4.0]",
    color: "#67c98a",
    light: "#dff4e7"
  },
  {
    key: "leading",
    label: "创新级",
    range: "[4.0, 5.0]",
    color: "#5ca4d9",
    light: "#dbeefa"
  }
];

const dimensionCards = [
  {
    index: "1",
    key: "literacy",
    icon: "📘",
    name: "数据素养",
    color: "#2f6fd6",
    bg: "#eaf2ff",
    text: "评估学校教师和学生在数据应用方面的综合能力，包括数据意识与思维、数据知识与技能、数据伦理与隐私等。"
  },
  {
    index: "2",
    key: "institution",
    icon: "📄",
    name: "数据制度",
    color: "#20b26b",
    bg: "#e9f8f0",
    text: "评估学校在组织架构、人员配备与管理规范方面的制度化水平，包括数据组织机构、数据人员配备、数据管理文件等。"
  },
  {
    index: "3",
    key: "behavior",
    icon: "⚡",
    name: "数据行为",
    color: "#e9a11a",
    bg: "#fff5dc",
    text: "评估数据在工作、学习与决策中的实际应用情况，包括学生数据行为、教师数据行为、数据应用成效等。"
  },
  {
    index: "4",
    key: "asset",
    icon: "◫",
    name: "数据资产",
    color: "#e5486b",
    bg: "#ffecef",
    text: "评估学校对数据资源的认知水平、积累规模等内容，包括数据资产意识、数据资产总量等。"
  },
  {
    index: "5",
    key: "technology",
    icon: "⚙",
    name: "数据技术",
    color: "#8b5cf6",
    bg: "#f2ebff",
    text: "评估学校在数据采集、存储、处理与安全保障方面的技术支撑能力，包括数据硬件设施、数据系统平台、数据安全合规与认证等。"
  }
];

const dimensionLabels = {
  literacy: "数据素养",
  institution: "数据制度",
  behavior: "数据行为",
  asset: "数据资产",
  technology: "数据技术"
};

const regionFullName = computed(() => {
  const q = queryRegion.value;

  if (q.province || q.city || q.district) {
    return `${q.province || ""}${q.city || ""}${q.district || ""}`;
  }

  const r = region.value || {};
  return `${r.province || ""}${r.city || ""}${r.name || ""}`;
});

const regionText = computed(() => {
  const q = queryRegion.value;

  if (q.province || q.city || q.district) {
    return [q.province, q.city, q.district].filter(Boolean).join(" / ") || "-";
  }

  const r = region.value || {};
  return [r.province, r.city, r.name].filter(Boolean).join(" / ") || "-";
});

const latestSchools = computed(() => keepLatestBySchool(assessments.value));

const regionAverageScore = computed(() => summary.value.avg_score ?? null);

const highestScore = computed(() => summary.value.highest_score ?? null);
const lowestScore = computed(() => summary.value.lowest_score ?? null);

const highestSchoolName = computed(() => {
  if (!topSchools.value.length) return "-";
  return topSchools.value[0]?.school_name || "-";
});

const lowestSchoolName = computed(() => {
  if (!bottomSchools.value.length) return "-";
  return bottomSchools.value[bottomSchools.value.length - 1]?.school_name || "-";
});

const dimensionAverage = computed(() => reportStatistics.value.dimension_average || {});

const levelDistribution = computed(() => {
  const total = latestSchools.value.length || 0;
  return levelMeta.map(level => {
    const rows = latestSchools.value.filter(x => x.maturity_level === level.key);
    const count = rows.length;
    return {
      ...level,
      count,
      ratio: total ? ((count / total) * 100).toFixed(1) : "0.0",
      avg_score: average(rows.map(x => x.total_score))
    };
  });
});

const totalRanking = computed(() => {
  const rows = latestSchools.value.filter(item => item.total_score != null)
    .sort((a, b) => b.total_score - a.total_score || a.school_id - b.school_id);
  let rank = 0;
  return rows.map((item, i) => {
    if (i === 0 || item.total_score !== rows[i - 1].total_score) rank = i + 1;
    return { ...item, rank };
  });
});
const topSchools = computed(() => totalRanking.value.slice(0, 5));
const bottomSchools = computed(() => totalRanking.value.slice(-5));

const levelAnalysis = computed(() => {
  return levelMeta.map((level) => {
    const rows = latestSchools.value
      .filter((x) => x.maturity_level === level.key)
      .sort((a, b) => num(b.total_score) - num(a.total_score));

    const count = rows.length;
    const scores = rows.map((x) => num(x.total_score));

    const top = rows.slice(0, 5).map((x, i) => ({
      ...x,
      rank: i + 1
    }));

    const bottomStartRank = Math.max(1, count - 4);
    const bottom = rows.slice(-5).map((x, i) => ({
      ...x,
      rank: bottomStartRank + i
    }));

    const highest = rows[0] || null;
    const lowest = rows[count - 1] || null;

    return {
      ...level,
      count,
      avg_score: average(scores),
      highest_score: highest ? num(highest.total_score) : 0,
      highest_school: highest?.school_name || "",
      lowest_score: lowest ? num(lowest.total_score) : 0,
      lowest_school: lowest?.school_name || "",
      std_score: standardDeviation(scores),
      dimension_average: getDimensionAverage(rows),
      top_schools: top,
      bottom_schools: bottom
    };
  });
});

function standardDeviation(values) {
  const arr = values.filter(v => v != null && Number.isFinite(Number(v))).map(Number);

  if (!arr.length) return 0;

  const avg = average(arr);
  const variance =
    arr.reduce((sum, value) => sum + Math.pow(value - avg, 2), 0) / arr.length;

  return Math.sqrt(variance);
}

const orderedLevelAnalysis = computed(() => {
  return levelAnalysis.value.filter(x => x.count > 0);
});

const developmentItems = computed(() => {
  const items = aiSuggestions.value.development?.items

  if (Array.isArray(items) && items.length > 0) {
    return items.map((item, index) => ({
      index: item.index || index + 1,
      title: item.title || "发展建议",
      dimension: item.dimension || "综合维度",
      content: item.content || ""
    }))
  }

  return [
    {
      index: 1,
      title: "加强数据素养培养",
      dimension: "数据素养",
      content: "当前区域发展建议正在生成或暂未获取成功，请稍后刷新页面。"
    },
    {
      index: 2,
      title: "完善数据治理制度",
      dimension: "数据制度",
      content: "当前区域发展建议正在生成或暂未获取成功，请稍后刷新页面。"
    },
    {
      index: 3,
      title: "推动数据应用落地",
      dimension: "数据行为",
      content: "当前区域发展建议正在生成或暂未获取成功，请稍后刷新页面。"
    },
    {
      index: 4,
      title: "提升数据资产意识",
      dimension: "数据资产",
      content: "当前区域发展建议正在生成或暂未获取成功，请稍后刷新页面。"
    },
    {
      index: 5,
      title: "夯实数据技术支撑",
      dimension: "数据技术",
      content: "当前区域发展建议正在生成或暂未获取成功，请稍后刷新页面。"
    }
  ]
})

const defaultDevelopmentSummary = computed(() => {
  return aiSuggestions.value.development?.summary || ""
})

const defaultConclusion = computed(() => {
  return aiSuggestions.value.development?.conclusion || ""
})

async function reloadAll() {
  loading.value = true

  try {
    await loadAssessments()
    await nextTick()
    initCharts()
    await loadAISuggestions()
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.message || "区域报告加载失败")
  } finally {
    loading.value = false
  }
}

async function loadAssessments() {
  const params = new URLSearchParams()
  params.set("page", "1")
  params.set("page_size", "1000")
  params.set("status", "completed")

  if (queryRegion.value.region_id) {
    params.set("region_id", queryRegion.value.region_id)
  }

  if (queryRegion.value.province) {
    params.set("province", queryRegion.value.province)
  }

  if (queryRegion.value.city) {
    params.set("city", queryRegion.value.city)
  }

  if (queryRegion.value.district) {
    params.set("district", queryRegion.value.district)
  }

  const url = `/api/admin/region-report/statistics/?${params.toString()}`

  console.log("超级管理员区域报告请求URL:", url)

  const { data: resp } = await apiGet(url)

  console.log("超级管理员区域报告响应:", resp)

  if (!resp?.success) {
    throw new Error(resp?.message || "区域评估数据加载失败")
  }

  const data = resp.data || {}
  region.value = data.region || null
  summary.value = data.summary || {}
  reportStatistics.value = data
  aiSuggestions.value = { level_suggestions: {}, development: { items: [] }, dimension_suggestions: {}, suggestion_mode: "" }
  assessments.value = (data.assessments || []).map(normalizeAssessment)
}

async function loadAISuggestions() {
  aiLoading.value = true

  try {
    const payload = buildAIPayload()

    const { data: resp } = await apiPost(
      "/api/admin/region-report/ai-suggestions/",
      payload
    )

    if (!resp?.success) {
      throw new Error(resp?.message || "AI 建议生成失败")
    }

    const data = resp.data || {}

    aiSuggestions.value = {
      dimension_suggestions: data.dimension_suggestions || {},
      suggestion_mode: data.suggestion_mode || "",
      level_suggestions: {
        initial: data.level_suggestions?.initial || "",
        growing: data.level_suggestions?.growing || "",
        mature: data.level_suggestions?.mature || "",
        leading: data.level_suggestions?.leading || ""
      },
      development: {
        summary: data.development?.summary || "",
        items: Array.isArray(data.development?.items)
          ? data.development.items
          : [],
        conclusion: data.development?.conclusion || ""
      }
    }
  } catch (e) {
    console.warn("AI 区域建议生成失败，使用默认建议：", e)
  } finally {
    aiLoading.value = false
  }
}

const evaluationTime = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1

  const semester = month >= 2 && month <= 7 ? "春季学期" : "秋季学期"

  return `${year}年${month}月 · ${semester}`
})

function buildAIPayload() {
  return { region: region.value || {} };
}

function normalizeAssessment(item) {
  const school = item.school || {};
  const scores = item.scores || {};
  const totalScore = scores.total_score == null ? null : num(scores.total_score);
  const maturity = item.maturity_level || scoreToLevel(totalScore);

  return {
    id: item.id,
    assessment_id: item.id,
    school_id: school.id || item.school_id,
    school_name: school.name || item.school_name || "-",
    school_type: school.school_type || item.school_type || "",
    status: item.status || "",
    maturity_level: maturity,
    total_score: totalScore,
    created_at: item.times?.created_at || item.created_at || "",
    completed_at: item.times?.completed_at || item.completed_at || "",
    dimension_scores: {
      literacy: scores.literacy_score == null ? null : num(scores.literacy_score),
      institution: scores.institution_score == null ? null : num(scores.institution_score),
      behavior: scores.behavior_score == null ? null : num(scores.behavior_score),
      asset: scores.asset_score == null ? null : num(scores.asset_score),
      technology: scores.technology_score == null ? null : num(scores.technology_score)
    }
  };
}

function keepLatestBySchool(list) {
  const map = new Map();
  list.forEach(item => {
    if (!item.school_id) return;
    const old = map.get(item.school_id);
    if (!old) {
      map.set(item.school_id, item);
      return;
    }
    const oldTime = new Date(old.completed_at || old.created_at || 0).getTime();
    const newTime = new Date(item.completed_at || item.created_at || 0).getTime();
    if (newTime > oldTime) {
      map.set(item.school_id, item);
    }
  });
  return Array.from(map.values());
}

function initCharts() {
  destroyCharts();
  initPie();
  initBar();
  initRadar();
}

function initPie() {
  if (!pieRef.value) return;

  const chart = echarts.init(pieRef.value, null, { renderer: "svg" });
  chartInstances.push(chart);

  chart.setOption({
    tooltip: {
      trigger: "item",
      formatter: (params) => {
        return `${params.name}<br/>学校数：${params.value} 所<br/>占比：${params.percent}%`;
      }
    },
    legend: {
      bottom: 8,
      left: "center",
      itemWidth: 18,
      itemHeight: 12,
      icon: "roundRect",
      textStyle: {
        color: "#475569",
        fontSize: 13
      }
    },
    series: [
      {
        name: "成熟度等级占比",
        type: "pie",
        radius: ["42%", "68%"],
        center: ["50%", "44%"],
        avoidLabelOverlap: true,
        minAngle: 5,
        itemStyle: {
          borderColor: "#ffffff",
          borderWidth: 6,
          borderRadius: 10
        },
        label: {
          show: true,
          formatter: (params) => {
            return `${params.name}\n${params.percent}%`;
          },
          fontSize: 14,
          fontWeight: 700,
          color: "#3f3f46",
          lineHeight: 24
        },
        labelLine: {
          show: true,
          length: 18,
          length2: 16,
          lineStyle: {
            width: 1.5
          }
        },
        data: levelDistribution.value.map((x) => ({
          name: x.label,
          value: x.count,
          itemStyle: { color: x.color }
        }))
      }
    ]
  });
}

function initBar() {
  if (!barRef.value) return;

  const chart = echarts.init(barRef.value, null, { renderer: "svg" });
  chartInstances.push(chart);

  chart.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (params) => {
        const p = params[0];
        return `${p.name}<br/>学校数量：${p.value} 所`;
      }
    },
    grid: {
      left: 48,
      right: 20,
      top: 40,
      bottom: 70
    },
    xAxis: {
      type: "category",
      data: levelDistribution.value.map((x) => `${x.label}\n${x.range}`),
      axisTick: { show: false },
      axisLine: {
        lineStyle: { color: "#9ca3af" }
      },
      axisLabel: {
        color: "#6b7280",
        fontSize: 12,
        lineHeight: 18
      }
    },
    yAxis: {
      type: "value",
      name: "学校数量（所）",
      nameTextStyle: {
        color: "#6b7280",
        fontSize: 12,
        padding: [0, 0, 8, -10]
      },
      min: 0,
      max: function (value) {
        return Math.max(10, Math.ceil(value.max + 1));
      },
      interval: 2,
      splitLine: {
        lineStyle: {
          color: "#d9e3ef"
        }
      },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: "#6b7280",
        fontSize: 12
      }
    },
    series: [
      {
        type: "bar",
        barWidth: 56,
        data: levelDistribution.value.map((x) => ({
          value: x.count,
          itemStyle: {
            color: x.color,
            borderRadius: [10, 10, 0, 0]
          }
        })),
        label: {
          show: true,
          position: "top",
          formatter: "{c}所",
          color: "#3f3f46",
          fontSize: 16,
          fontWeight: 700
        }
      }
    ]
  });
}

function initRadar() {
  if (!radarRef.value) return;

  const chart = echarts.init(radarRef.value, null, { renderer: "svg" });
  chartInstances.push(chart);

  const d = dimensionAverage.value;

  chart.setOption({
    tooltip: {
      trigger: "item",
      formatter: () => {
        return `
          <div style="line-height: 1.8;">
            <div><strong>区域平均分</strong></div>
            <div>数据素养：${formatScore(d.literacy)}</div>
            <div>数据制度：${formatScore(d.institution)}</div>
            <div>数据行为：${formatScore(d.behavior)}</div>
            <div>数据资产：${formatScore(d.asset)}</div>
            <div>数据技术：${formatScore(d.technology)}</div>
          </div>
        `;
      }
    },
    radar: {
      center: ["50%", "55%"],
      radius: "58%",   // 比之前小一点，给外围分值标签留空间
      splitNumber: 5,
      startAngle: 90,
      indicator: [
          { name: "数据素养", max: 5 },
          { name: "数据制度", max: 5 },
          { name: "数据行为", max: 5 },
          { name: "数据资产", max: 5 },
          { name: "数据技术", max: 5 }
      ],
      axisName: {
        color: "#2f5f97",
        fontSize: 15,
        fontWeight: 800,
        padding: [6, 0, 6, 0]
      },
      splitArea: {
        areaStyle: {
          color: [
            "#edf6ff",
            "#e5f1fd",
            "#dcebf9",
            "#d4e6f7",
            "#cce1f4"
          ]
        }
      },
      splitLine: {
        lineStyle: {
          color: "#bcd3eb",
          width: 1
        }
      },
      axisLine: {
        lineStyle: {
          color: "#bcd3eb",
          width: 1
        }
      }
    },
    series: [
      {
        name: "区域平均分",
        type: "radar",
        symbol: "circle",
        symbolSize: 7,
        lineStyle: {
          width: 4,
          color: "#3b82d6"
        },
        itemStyle: {
          color: "#3b82d6"
        },
        areaStyle: {
          color: "rgba(59, 130, 214, 0.18)"
        },
        data: [
          {
            value: [
              num(d.literacy),
              num(d.institution),
              num(d.behavior),
              num(d.asset),
              num(d.technology)
            ],
            name: "区域平均分"
          }
        ]
      }
    ]
  });
}

function destroyCharts() {
  chartInstances.forEach(c => c?.dispose());
  chartInstances = [];
}

function resizeCharts() {
  chartInstances.forEach(c => c?.resize());
}

function getDimensionAverage(list) {
  return {
    literacy: average(list.map(x => x.dimension_scores.literacy)),
    institution: average(list.map(x => x.dimension_scores.institution)),
    behavior: average(list.map(x => x.dimension_scores.behavior)),
    asset: average(list.map(x => x.dimension_scores.asset)),
    technology: average(list.map(x => x.dimension_scores.technology))
  };
}

function topThreeDimensions(dimAvg) {
  return Object.keys(dimensionLabels).map(key => ({
    key,
    label: dimensionLabels[key],
    score: num(dimAvg[key])
  })).sort((a, b) => b.score - a.score).slice(0, 3);
}

function getLevelSuggestion(key) {
  if (aiLoading.value) return "AI 建议生成中...";
  const text = aiSuggestions.value.level_suggestions?.[key];
  if (text) return text;

  const defaults = {
    initial:
      "初始默认",
    growing:
      "成长默认",
    mature:
      "成熟默认",
    leading:
      "领先默认"
  };
  return defaults[key] || "暂无建议。";
}

function scoreToLevel(score) {
  const s = num(score)

  if (s <= 1.5) return "initial"
  if (s <= 3.0) return "growing"
  if (s <= 4.0) return "mature"
  return "leading"
}

function maturityLabel(v) {
  const map = {
    initial: "初始级",
    growing: "成长级",
    mature: "成熟级",
    leading: "创新级"
  };
  return map[v] || v || "-";
}

function num(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function average(arr) {
  const nums = arr.filter(v => v != null && Number.isFinite(Number(v))).map(Number);
  if (!nums.length) return 0;
  return nums.reduce((a, b) => a + b, 0) / nums.length;
}

function formatScore(v) {
  return v != null && Number.isFinite(Number(v)) ? Number(v).toFixed(2) : "—";
}


async function exportPDF() {
  if (!reportRef.value) {
    ElMessage.warning("报告内容尚未加载完成")
    return
  }

  exporting.value = true

  try {
    await nextTick()

    // 避免图表导出时尺寸异常
    resizeCharts()
    await nextTick()

    const reportEl = reportRef.value

    const canvas = await html2canvas(reportEl, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      backgroundColor: "#ffffff",
      logging: false
    })

    const imgData = canvas.toDataURL("image/png")

    // A4 宽度，页面高度按内容自适应，不分页
    const pdfWidth = 210
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width

    const pdf = new jsPDF({
      orientation: "p",
      unit: "mm",
      format: [pdfWidth, pdfHeight]
    })

    pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight)

    const fileName = `${regionFullName.value || "区域"}数据文化成熟度评估报告.pdf`
    pdf.save(fileName)
  } catch (error) {
    console.error("导出 PDF 失败：", error)
    ElMessage.error("导出 PDF 失败，请稍后重试")
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  window.addEventListener("resize", resizeCharts);
  await reloadAll();
});

onUnmounted(() => {
  window.removeEventListener("resize", resizeCharts);
  destroyCharts();
});
</script>

<style scoped>
.region-report-page {
  min-height: 100vh;
  background: #f3f5f8;
  padding: 20px 0 36px;
}

.toolbar {
  width: 1080px;
  margin: 0 auto 14px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.report-shell {
  width: 1080px;
  margin: 0 auto;
  background: #fff;
  border-radius: 10px;
  padding: 26px 26px 32px;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.06);
  box-sizing: border-box;
}

.report-header {
  margin-bottom: 24px;
}

.report-title {
  margin: 0;
  text-align: center;
  font-size: 28px;
  line-height: 1.25;
  font-weight: 800;
  color: #1f2937;
  letter-spacing: 0.5px;
}

.meta-row {
  margin-top: 14px;
  display: flex;
  justify-content: center;
  gap: 22px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #334155;
}

.meta-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #2f7ecb;
  display: inline-block;
  margin-right: 6px;
}

.meta-label {
  color: #64748b;
}

.meta-value {
  color: #1e293b;
  font-weight: 600;
}

.intro-card {
  margin-top: 18px;
  background: #fbfcfe;
  border: 1px solid #e6edf5;
  border-radius: 8px;
  padding: 16px 20px;
  color: #475569;
  font-size: 14px;
  line-height: 1.9;
}

.intro-card p {
  margin: 0;
  text-indent: 2em;
}

.intro-card p + p {
  margin-top: 6px;
}

.mini-block-title {
  margin-top: 18px;
  font-size: 15px;
  font-weight: 700;
  color: #1f3f66;
}

.mini-icon {
  color: #2f7ecb;
  margin-right: 6px;
}

.dimension-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}

.dimension-card {
  min-height: 160px;
  border: 1px solid #e6edf5;
  border-radius: 8px;
  padding: 14px 14px 12px;
  background: #fff;
  box-sizing: border-box;
}

.dimension-top {
  display: flex;
  justify-content: flex-start;
}

.dimension-badge {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  text-align: center;
  line-height: 30px;
}

.dimension-name {
  margin-top: 10px;
  font-size: 15px;
  font-weight: 700;
  color: #1f2937;
}

.dimension-desc {
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
  line-height: 1.65;
}

.report-section {
  margin-top: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  border-bottom: 3px solid #2f7ecb;
  padding-bottom: 8px;
  margin-bottom: 14px;
}

.section-index {
  width: 18px;
  height: 18px;
  border-radius: 3px;
  background: #2f7ecb;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  text-align: center;
  line-height: 18px;
  margin-right: 8px;
}

.section-title {
  font-size: 18px;
  font-weight: 800;
  color: #1f3f66;
}

.section-box {
  background: #fff;
}

.chart-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
  align-items: center;
}

.chart-panel {
  padding: 4px 0 0;
}

.panel-title {
  text-align: center;
  font-size: 14px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 4px;
}

.chart-box {
  height: 300px;
}

.dist-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
  font-size: 13px;
}

.dist-table thead th {
  background: #2f7ecb;
  color: #fff;
  font-weight: 700;
  padding: 11px 8px;
  text-align: center;
}

.dist-table tbody td {
  border-bottom: 1px solid #e8eef6;
  padding: 10px 8px;
  text-align: center;
  color: #334155;
}

.dist-table tbody tr:nth-child(even) {
  background: #f8fbff;
}

.level-chip {
  display: inline-block;
  min-width: 68px;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
  font-weight: 700;
}

.overall-layout {
  display: grid;
  grid-template-columns: 1fr 240px;
  gap: 24px;
  align-items: center;
}

.radar-panel {
  position: relative;
}

.radar-box {
  height: 330px;
}

.radar-legend {
  margin-top: -4px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #4f8ef7;
  font-size: 12px;
  font-weight: 600;
}

.legend-line {
  width: 20px;
  height: 3px;
  border-radius: 2px;
  background: #4f8ef7;
  margin-right: 6px;
}

.score-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.score-card {
  height: 98px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.score-number {
  font-size: 28px;
  font-weight: 800;
}

.score-label {
  margin-top: 4px;
  font-size: 12px;
  color: #64748b;
}

.score-card.avg .score-number {
  color: #22c55e;
}
.score-card.high .score-number {
  color: #3b82f6;
}
.score-card.low .score-number {
  color: #ef4444;
}

.rank-layout {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.rank-card {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e7edf6;
}

.rank-card.green {
  background: #f3fcf6;
}

.rank-card.red {
  background: #fff4f4;
}

.rank-card-title {
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 700;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 4px;
}

.rank-arrow {
  font-size: 14px;
  font-weight: 800;
}

.rank-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  font-size: 12px;
}

.rank-table thead th {
  background: #eef3f8;
  color: #334155;
  font-weight: 700;
  padding: 9px 6px;
  text-align: center;
}

.rank-table tbody td {
  border-bottom: 1px solid #edf2f7;
  padding: 8px 6px;
  text-align: center;
  color: #334155;
}

.rank-table tbody td:nth-child(2) {
  text-align: left;
  padding-left: 10px;
}

.mini-tag {
  display: inline-block;
  padding: 2px 7px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.mini-tag.purple {
  background: #efe9ff;
  color: #8b5cf6;
}

.mini-tag.rose {
  background: #ffe6e7;
  color: #ef4444;
}

.text-green {
  color: #16a34a !important;
  font-weight: 700;
}

.text-red {
  color: #ef4444 !important;
  font-weight: 700;
}

.level-report-section {
  margin-top: 24px;
  border: 1px solid #e8eef6;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}

.level-banner {
  min-height: 86px;
  padding: 16px 22px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.level-report-section.initial .level-banner {
  background: linear-gradient(90deg, #ef4444, #f43f5e);
}
.level-report-section.growing .level-banner {
  background: linear-gradient(90deg, #f59e0b, #fb923c);
}
.level-report-section.mature .level-banner {
  background: linear-gradient(90deg, #2563eb, #4f46e5);
}
.level-report-section.leading .level-banner {
  background: linear-gradient(90deg, #16a34a, #22c55e);
}

.level-banner-title {
  font-size: 24px;
  font-weight: 800;
}

.level-banner-sub {
  margin-top: 4px;
  font-size: 12px;
  opacity: 0.95;
}

.level-banner-score {
  text-align: right;
}

.level-banner-number {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
}

.level-banner-text {
  margin-top: 5px;
  font-size: 12px;
}

.dim-score-row {
  padding: 16px 20px 10px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.dim-score-card {
  min-height: 82px;
  border-radius: 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.level-report-section.initial .dim-score-card {
  background: #fff0f0;
}
.level-report-section.growing .dim-score-card {
  background: #fff7e9;
}
.level-report-section.mature .dim-score-card {
  background: #edf3ff;
}
.level-report-section.leading .dim-score-card {
  background: #ecfbf0;
}

.dim-score-value {
  font-size: 22px;
  font-weight: 800;
}

.level-report-section.initial .dim-score-value {
  color: #ef4444;
}
.level-report-section.growing .dim-score-value {
  color: #f59e0b;
}
.level-report-section.mature .dim-score-value {
  color: #2563eb;
}
.level-report-section.leading .dim-score-value {
  color: #16a34a;
}

.dim-score-name {
  margin-top: 4px;
  font-size: 13px;
  color: #334155;
  font-weight: 700;
}

.dim-score-sub {
  margin-top: 3px;
  font-size: 11px;
  color: #94a3b8;
}

.level-table-layout {
  padding: 6px 20px 14px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.level-table-card {
  background: #fff;
}

.small-table-title {
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.small-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.small-table thead th {
  background: #eef3f8;
  color: #334155;
  font-weight: 700;
  padding: 8px 6px;
  text-align: center;
}

.small-table tbody td {
  border-bottom: 1px solid #edf2f7;
  padding: 8px 6px;
  text-align: center;
  color: #334155;
}

.small-table tbody td:nth-child(2) {
  text-align: left;
  padding-left: 10px;
}

.suggest-box {
  margin: 0 20px 18px;
  background: #f3fbff;
  border: 1px solid #d7eef8;
  border-left: 4px solid #46a8df;
  border-radius: 8px;
  padding: 14px 16px;
}

.suggest-title {
  display: flex;
  align-items: center;
  font-size: 13px;
  font-weight: 700;
  color: #2b77a9;
  margin-bottom: 8px;
}

.suggest-icon {
  margin-right: 6px;
  font-size: 14px;
}

.suggest-content {
  font-size: 13px;
  line-height: 1.9;
  color: #475569;
  text-indent: 2em;
}

.dev-summary {
  background: #fafcff;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  padding: 14px 16px;
  font-size: 13px;
  line-height: 1.9;
  color: #475569;
  text-indent: 2em;
}

.dev-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dev-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #fff;
  border: 1px solid #edf2f7;
  border-radius: 10px;
  padding: 16px;
}

.dev-num {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  text-align: center;
  line-height: 38px;
  flex-shrink: 0;
}

.num-1 { background: #3b82f6; }
.num-2 { background: #22c55e; }
.num-3 { background: #f59e0b; }
.num-4 { background: #f43f5e; }
.num-5 { background: #8b5cf6; }

.dev-main {
  flex: 1;
}

.dev-title {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
}

.dev-dim {
  margin-top: 3px;
  font-size: 12px;
  color: #64748b;
}

.dev-text {
  margin-top: 7px;
  font-size: 13px;
  line-height: 1.85;
  color: #475569;
}

.final-box {
  margin-top: 16px;
  background: #0f172a;
  border-radius: 10px;
  padding: 16px 18px;
}

.final-box-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.final-box-text {
  font-size: 13px;
  line-height: 1.9;
  color: #d9e1ea;
}

.report-info-line {
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 22px;
  flex-wrap: wrap;
  font-size: 17px;
  color: #1e3a5f;
  font-weight: 700;
}

.info-item {
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}

.info-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 6px;
  font-size: 18px;
  line-height: 1;
}

.info-label {
  color: #1e3a5f;
  font-weight: 800;
}

.info-value {
  color: #111827;
  font-weight: 700;
}



.benchmark-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 26px;
  padding: 0 13px;
  border-radius: 14px;
  background: #e7f0ff;
  color: #2f6fd6;
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
}

.overview-card {
  margin-top: 18px;
  background: #ffffff;
  border: 1px solid #dfe7f1;
  border-radius: 18px;
  padding: 26px 30px 30px;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

.overview-text {
  color: #1f2937;
  font-size: 19px;
  line-height: 2;
}

.overview-text p {
  margin: 0;
  text-indent: 2em;
}

.overview-text p + p {
  margin-top: 10px;
}

.overview-text strong {
  font-weight: 800;
  color: #111827;
}

.overview-divider {
  height: 5px;
  background: #2f97da;
  border-radius: 999px;
  margin: 18px 0 28px;
}

.core-title {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 21px;
  font-weight: 800;
  color: #1f365c;
  margin-bottom: 22px;
}

.core-card {
  min-height: 210px;
  border: 1px solid #d9e3ef;
  border-radius: 16px;
  background: #fbfcfe;
  padding: 20px 20px 18px;
  box-sizing: border-box;
}

.core-name {
  margin-top: 0;
  text-align: center;
  font-size: 17px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1.4;
}

.core-title-icon {
  color: #2f6fd6;
  font-size: 20px;
  line-height: 1;
}

.core-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 18px;
}


.core-icon-box {
  width: 58px;
  height: 58px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  line-height: 1;
}


.core-desc {
  margin-top: 12px;
  font-size: 15px;
  line-height: 1.85;
  color: #64748b;
}

/* ===== 成熟度等级分布 ===== */
.maturity-section {
  margin-top: 28px;
}

.maturity-title-wrap {
  margin-bottom: 24px;
}

.maturity-title {
  text-align: center;
  font-size: 22px;
  font-weight: 800;
  color: #1f3f66;
  letter-spacing: 0.5px;
}

.maturity-line {
  margin-top: 14px;
  height: 4px;
  width: 100%;
  background: #2f97da;
  border-radius: 999px;
}

.maturity-chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 34px;
  align-items: start;
  margin-top: 6px;
}

.maturity-chart-card {
  background: #fff;
}

.maturity-chart-title {
  text-align: center;
  font-size: 18px;
  font-weight: 800;
  color: #2f5f97;
  margin-bottom: 10px;
}

.maturity-chart-box {
  height: 420px;
}

.maturity-table-wrap {
  margin-top: 28px;
}

.maturity-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 15px;
}

.maturity-table thead th {
  background: linear-gradient(90deg, #2d66a3, #357cc1);
  color: #ffffff;
  font-weight: 800;
  font-size: 15px;
  padding: 16px 18px;
  text-align: left;
}

.maturity-table thead th:first-child {
  border-top-left-radius: 10px;
}

.maturity-table thead th:last-child {
  border-top-right-radius: 10px;
}

.maturity-table tbody td {
  padding: 18px 18px;
  color: #3f3f46;
  border-bottom: 1px solid #edf2f7;
  background: #ffffff;
}

.maturity-table tbody tr:nth-child(even) td {
  background: #f7fafc;
}

.maturity-level-cell {
  width: 180px;
}

.maturity-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 68px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 800;
}

.maturity-count {
  font-weight: 800;
  color: #1f2937;
}

/* ===== 区域整体数据表现 ===== */
.overall-section {
  margin-top: 34px;
}

.overall-title-wrap {
  margin-bottom: 24px;
}

.overall-title {
  text-align: center;
  font-size: 22px;
  font-weight: 800;
  color: #1f3f66;
  letter-spacing: 0.5px;
}

.overall-line {
  margin-top: 14px;
  height: 4px;
  width: 100%;
  background: #2f97da;
  border-radius: 999px;
}

.overall-top {
  display: grid;
  grid-template-columns: 1fr 310px;
  gap: 42px;
  align-items: center;
}

.overall-radar-area {
  position: relative;
  min-height: 440px;
}

.overall-radar-title {
  text-align: center;
  font-size: 22px;
  font-weight: 800;
  color: #3f3f46;
  margin-bottom: 4px;
}

.radar-wrapper {
  position: relative;
  height: 410px;
}

.overall-radar-chart {
  width: 100%;
  height: 410px;
}

.radar-score-tag {
  position: absolute;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  height: 24px;
  padding: 0 8px;
  background: rgba(59, 130, 214, 0.10);   /* 改成很浅的蓝色 */
  border: 1px solid rgba(59, 130, 214, 0.20);
  color: #2563eb;
  font-size: 13px;
  font-weight: 800;
  border-radius: 999px;
  box-shadow: 0 1px 4px rgba(59, 130, 214, 0.08);
  white-space: nowrap;
  pointer-events: none;
}

/* 位置全部往外挪一点，避免和维度名称重叠 */
.tag-literacy {
  top: 34px;
  left: 50%;
  transform: translateX(-50%);
}

.tag-technology {
  top: 170px;
  right: 90px;
}

.tag-asset {
  bottom: 60px;
  right: 130px;
}

.tag-behavior {
  bottom: 65px;
  left: 130px;
}

.tag-institution {
  top: 170px;
  left: 90px;
}

.overall-radar-legend {
  margin-top: -6px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 14px;
}

.legend-box {
  display: inline-block;
  width: 28px;
  height: 13px;
  background: #3b82d6;
  border-radius: 4px;
}

.overall-score-list {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.overall-score-card {
  width: 100%;
  height: 106px;
  border: 1px solid #dfe7f1;
  border-radius: 10px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-label {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 700;
}

.score-value {
  margin-top: 4px;
  font-size: 29px;
  line-height: 1;
  font-weight: 900;
}

.score-school {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.overall-score-card.highest .score-value {
  color: #10b981;
}

.overall-score-card.average .score-value {
  color: #2563eb;
}

.overall-score-card.lowest .score-value {
  color: #ef4444;
}

/* 排名区域 */
.overall-rank-area {
  margin-top: 28px;
  background: #f6f9fc;
  padding: 16px 18px 22px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
}

.overall-rank-card {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #dfe7f1;
  background: #ffffff;
}

.overall-rank-card.top {
  background: #f0fff8;
  border-color: #d5f4e4;
}

.overall-rank-card.bottom {
  background: #fff5f5;
  border-color: #f4d7d7;
}

.overall-rank-title {
  height: 58px;
  padding: 0 22px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 900;
}

.overall-rank-card.top .overall-rank-title {
  color: #047857;
}

.overall-rank-card.bottom .overall-rank-title {
  color: #b91c1c;
}

.rank-icon {
  font-size: 28px;
  line-height: 1;
}

.rank-icon.up {
  color: #059669;
}

.rank-icon.down {
  color: #dc2626;
}

.overall-rank-table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
  font-size: 15px;
}

.overall-rank-table thead th {
  background: #e7edf5;
  color: #475569;
  padding: 15px 14px;
  text-align: left;
  font-weight: 800;
}

.overall-rank-table tbody td {
  padding: 15px 14px;
  border-bottom: 1px solid #edf2f7;
  color: #334155;
  font-weight: 600;
}

.overall-rank-table tbody tr:last-child td {
  border-bottom: none;
}

.top-table tbody tr.top-rank-1 td {
  background: #fff3a4;
}

.top-table tbody tr.top-rank-2 td {
  background: #e5e7eb;
}

.top-table tbody tr.top-rank-3 td {
  background: #ffe0b7;
}

.level-mini-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 58px;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 13px;
  font-weight: 700;
}

.level-mini-tag.purple {
  background: #ede9fe;
  color: #7c3aed;
}

.level-mini-tag.red {
  background: #ffe4e6;
  color: #ef4444;
}

.top-score {
  color: #92400e !important;
  font-weight: 900 !important;
}

.bottom-score {
  color: #ef4444 !important;
  font-weight: 900 !important;
}

/* ===== 各成熟度等级学校分析 ===== */
.level-analysis-section {
  margin-top: 30px;
  background: #ffffff;
  border: 1px solid #e5eaf2;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

/* 顶部标题栏 */
.level-analysis-header {
  min-height: 92px;
  padding: 18px 28px;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.level-analysis-section.initial .level-analysis-header {
  background: linear-gradient(90deg, #ff3b3f, #e91e4d);
}

.level-analysis-section.growing .level-analysis-header {
  background: linear-gradient(90deg, #ff9800, #fb6d00);
}

.level-analysis-section.mature .level-analysis-header {
  background: linear-gradient(90deg, #2f7df6, #4f46e5);
}

.level-analysis-section.leading .level-analysis-header {
  background: linear-gradient(90deg, #16a34a, #22c55e);
}

.level-title {
  font-size: 25px;
  font-weight: 900;
  line-height: 1.2;
}

.level-subtitle {
  margin-top: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.level-header-right {
  text-align: right;
}

.level-avg-score {
  font-size: 34px;
  line-height: 1;
  font-weight: 900;
}

.level-avg-label {
  margin-top: 6px;
  font-size: 14px;
  font-weight: 700;
}

/* 三个统计卡片 */
.level-stat-row {
  padding: 24px 28px 18px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.level-stat-card {
  min-height: 94px;
  border-radius: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border: 1px solid transparent;
}

.level-analysis-section.initial .level-stat-card {
  background: #fff1f1;
  border-color: #ffe0e0;
}

.level-analysis-section.growing .level-stat-card {
  background: #fff7e6;
  border-color: #ffedc6;
}

.level-analysis-section.mature .level-stat-card {
  background: #eef5ff;
  border-color: #d9e8ff;
}

.level-analysis-section.leading .level-stat-card {
  background: #ecfdf3;
  border-color: #d7f7e4;
}

.level-stat-label {
  font-size: 13px;
  color: #ef4444;
  font-weight: 700;
}

.level-analysis-section.growing .level-stat-label {
  color: #f59e0b;
}

.level-analysis-section.mature .level-stat-label {
  color: #2563eb;
}

.level-analysis-section.leading .level-stat-label {
  color: #16a34a;
}

.level-stat-value {
  margin-top: 4px;
  font-size: 25px;
  line-height: 1;
  font-weight: 900;
  color: #ef4444;
}

.level-analysis-section.growing .level-stat-value {
  color: #f59e0b;
}

.level-analysis-section.mature .level-stat-value {
  color: #2563eb;
}

.level-analysis-section.leading .level-stat-value {
  color: #16a34a;
}

.level-stat-school {
  margin-top: 6px;
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
}

/* 排名表格 */
.level-rank-layout {
  padding: 8px 28px 22px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
}

.level-rank-block {
  background: #ffffff;
}

.level-rank-title {
  margin-bottom: 10px;
  font-size: 15px;
  font-weight: 900;
  color: #1f2937;
}

.level-rank-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.level-rank-table thead th {
  background: #e8eef6;
  color: #334155;
  padding: 12px 14px;
  text-align: left;
  font-weight: 800;
}

.level-rank-table tbody td {
  padding: 12px 14px;
  border-bottom: 1px solid #edf2f7;
  color: #1f2937;
  font-weight: 600;
}

.level-rank-table tbody tr:last-child td {
  border-bottom: none;
}

.level-rank-table th:first-child,
.level-rank-table td:first-child {
  width: 90px;
}

.level-rank-table td:nth-child(2) {
  text-align: left;
}

.rank-red {
  color: #ef4444 !important;
  font-weight: 900 !important;
}

.level-table-score {
  text-align: right;
  font-weight: 900 !important;
}

.level-analysis-section.initial .level-table-score {
  color: #ef4444 !important;
}

.level-analysis-section.growing .level-table-score {
  color: #f59e0b !important;
}

.level-analysis-section.mature .level-table-score {
  color: #2563eb !important;
}

.level-analysis-section.leading .level-table-score {
  color: #16a34a !important;
}

.level-table-score.weak {
  color: #ef4444 !important;
}

/* AI 建议框 */
.level-ai-box {
  margin: 0 28px 28px;
  min-height: 210px;
  background: #eaf7ff;
  border-radius: 10px;
  border-left: 5px solid #27a8e8;
  padding: 18px 20px;
  box-sizing: border-box;
}

.level-ai-title {
  display: flex;
  align-items: center;
  font-size: 15px;
  font-weight: 900;
  color: #1f3f66;
  margin-bottom: 16px;
}

.ai-info-icon {
  margin-right: 8px;
  color: #2563eb;
  font-weight: 900;
}

.level-ai-content {
  min-height: 145px;
  background: #ffffff;
  border-radius: 8px;
  padding: 26px 30px;
  color: #334155;
  font-size: 14px;
  line-height: 1.9;
  text-indent: 2em;
  box-sizing: border-box;
}

/* ===== 区域发展建议 ===== */
.development-section {
  margin-top: 34px;
}

.development-title-wrap {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
  border-left: 5px solid #28a7e8;
  padding-left: 14px;
}

.development-title {
  font-size: 22px;
  font-weight: 900;
  color: #1f3f66;
  line-height: 1.2;
}

.development-card {
  background: #ffffff;
  border: 1px solid #dfe7f1;
  border-radius: 14px;
  padding: 26px 28px 30px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
}

.development-summary-box {
  background: #f8fbff;
  border: 1px solid #e3ebf5;
  border-radius: 10px;
  padding: 18px 22px;
  color: #475569;
  font-size: 15px;
  line-height: 1.9;
  text-indent: 2em;
}

/* 建议列表 */
.development-list {
  margin-top: 22px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.development-item {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  min-height: 112px;
  padding: 20px 22px;
  border-radius: 12px;
  border: 1px solid transparent;
  box-sizing: border-box;
}

.development-item-1 {
  background: linear-gradient(90deg, #f3f8ff, #ffffff);
  border-color: #d9e9ff;
}

.development-item-2 {
  background: linear-gradient(90deg, #f0fff8, #ffffff);
  border-color: #d8f5e7;
}

.development-item-3 {
  background: linear-gradient(90deg, #fffaf0, #ffffff);
  border-color: #ffedc7;
}

.development-item-4 {
  background: linear-gradient(90deg, #fff4f6, #ffffff);
  border-color: #ffe0e7;
}

.development-item-5 {
  background: linear-gradient(90deg, #f7f3ff, #ffffff);
  border-color: #e7dcff;
}

.development-number {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  color: #ffffff;
  font-size: 22px;
  font-weight: 900;
  text-align: center;
  line-height: 48px;
  flex-shrink: 0;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.12);
}

.development-item-1 .development-number {
  background: #3b82f6;
}

.development-item-2 .development-number {
  background: #10b981;
}

.development-item-3 .development-number {
  background: #f59e0b;
}

.development-item-4 .development-number {
  background: #f43f5e;
}

.development-item-5 .development-number {
  background: #8b5cf6;
}

.development-content {
  flex: 1;
}

.development-item-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2937;
  font-size: 17px;
  font-weight: 900;
  line-height: 1.4;
}

.development-icon {
  font-size: 17px;
  line-height: 1;
}

.development-item-text {
  margin-top: 10px;
  color: #475569;
  font-size: 15px;
  line-height: 1.85;
}

/* 底部总体目标 */
.development-final-box {
  margin-top: 24px;
  background: #0f172a;
  border-radius: 12px;
  padding: 22px 24px;
  color: #ffffff;
}

.development-final-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 900;
  margin-bottom: 12px;
}

.final-lightning {
  color: #facc15;
  font-size: 20px;
}

.development-final-text {
  color: #dbe4ef;
  font-size: 15px;
  line-height: 1.9;
}

.development-title-wrap {
  margin-bottom: 24px;
  text-align: center;
}

.development-title {
  text-align: center;
  font-size: 22px;
  font-weight: 800;
  color: #1f3f66;
  letter-spacing: 0.5px;
}

.development-item {
  display: block;
  background: #ffffff;
  border: 1px solid #edf2f7;
  border-radius: 10px;
  padding: 16px 18px;
}

.development-content {
  width: 100%;
}

.development-item-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 800;
  color: #1f2937;
  margin-bottom: 8px;
}

.development-title-index {
  font-size: 15px;
  font-weight: 900;
  color: #2563eb;
  flex-shrink: 0;
}

.development-item-text {
  font-size: 14px;
  line-height: 1.9;
  color: #475569;
  text-indent: 2em;
}

.level-analysis-section.initial .level-analysis-header {
  background: #ff7b82;
}

.level-analysis-section.growing .level-analysis-header {
  background: #ffb34d;
}

.level-analysis-section.mature .level-analysis-header {
  background: #5dade2;
}

.level-analysis-section.leading .level-analysis-header {
  background: #65d18d;
}

.report-footer {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  border-top: 1px solid #e4e7ed;
  margin-top: 40px;
}

/* ===== 报告正文类文字统一两端对齐 ===== */
.report-shell .overview-text p,
.report-shell .core-desc,
.report-shell .level-ai-content,
.report-shell .development-summary-box,
.report-shell .development-item-text,
.report-shell .development-final-text {
  text-align: justify;
  text-align-last: left;
  line-height: 1.9;
  word-break: break-word;
  overflow-wrap: break-word;
}

/* 去掉总分前5名表格前三名的底色 */
.top-table tbody tr.top-rank-1 td,
.top-table tbody tr.top-rank-2 td,
.top-table tbody tr.top-rank-3 td {
  background: #ffffff !important;
}

/* 响应式 */
@media (max-width: 1200px) {
  .level-rank-layout {
    grid-template-columns: 1fr;
  }

  .level-stat-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .overall-top {
    grid-template-columns: 1fr;
  }

  .overall-score-list {
    flex-direction: row;
  }

  .overall-rank-area {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .maturity-chart-row {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .maturity-chart-box {
    height: 360px;
  }
}

/* 响应式，防止小屏挤压 */
@media (max-width: 1200px) {
  .core-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .overview-card {
    padding: 18px;
  }

  .overview-text {
    font-size: 15px;
  }

  .core-grid {
    grid-template-columns: 1fr;
  }
}

@media print {
  .no-print {
    display: none !important;
  }

  .region-report-page {
    padding: 0;
    background: #fff;
  }

  .report-shell {
    width: 100%;
    margin: 0;
    box-shadow: none;
    border-radius: 0;
  }

  .report-section,
  .level-report-section {
    break-inside: avoid;
    page-break-inside: avoid;
  }
}
</style>
