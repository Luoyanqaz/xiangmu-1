<template>
  <div class="page">
    <!-- 顶部：区域信息 + 统计 -->

    <!-- 底部：学校评估列表 -->
    <el-card class="block">
      <template #header>
        <div class="card-header">
          <div class="title">学校评估列表</div>
        </div>
      </template>

      <div class="filter-panel">
        <el-form class="filter-form" :model="query" @submit.prevent>
          <el-form-item label="学校名称">
            <el-input
              v-model="query.school_name"
              placeholder="学校名称"
              clearable
              class="w-name"
              @keyup.enter="handleSearch"
            />
          </el-form-item>

          <el-form-item label="学校类型">
            <el-select v-model="query.school_type" clearable class="w-select" placeholder="全部类型">
              <el-option label="小学" value="primary" />
              <el-option label="初中" value="junior" />
              <el-option label="高中" value="senior" />
              <el-option label="九年一贯制" value="nine_year" />
              <el-option label="十二年一贯制" value="twelve_year" />
            </el-select>
          </el-form-item>

          <el-form-item label="评估状态">
            <el-select v-model="query.status" clearable class="w-select" placeholder="全部状态">
              <el-option label="草稿" value="draft" />
              <el-option label="数据收集中" value="collecting" />
              <el-option label="分析中" value="analyzing" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>

          <el-form-item label="评估时间">
            <el-date-picker
              v-model="query.time_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              class="w-date"
            />
          </el-form-item>

          <el-form-item label="成熟度等级">
            <el-select v-model="query.maturity_level" clearable class="w-select" placeholder="全部等级">
              <el-option label="创新级" value="leading" />
              <el-option label="成熟级" value="mature" />
              <el-option label="成长级" value="growing" />
              <el-option label="初始级" value="initial" />
            </el-select>
          </el-form-item>

          <el-form-item class="actions">
            <el-button type="primary" @click="handleSearch" :loading="loadingList">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table
        class="table"
        :data="list"
        v-loading="loadingList"
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column label="ID" width="80" align="center">
  <template #default="{ $index }">
    {{ (query.page - 1) * query.page_size + $index + 1 }}
  </template>
</el-table-column>

        <el-table-column prop="school_name" label="学校名称" min-width="220" show-overflow-tooltip />

        <el-table-column prop="school_type" label="学校类型" width="140">
          <template #default="{ row }">
            {{ schoolTypeLabel(row.school_type) }}
          </template>
        </el-table-column>

        <el-table-column prop="status" label="评估状态" width="130">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="total_score" label="总分" width="120" sortable="custom">
          <template #default="{ row }">
            <span class="score">{{ formatScore(row.total_score) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="maturity_level" label="成熟度等级" width="140">
          <template #default="{ row }">
            <el-tag v-if="row.maturity_level" type="info" effect="plain">
              {{ maturityLabel(row.maturity_level) }}
            </el-tag>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="190" sortable="custom">
          <template #default="{ row }">
            {{ row.created_at || "-" }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed'"
              type="primary"
              link
              @click="viewReport(row.id)"
            >
              查看报告
            </el-button>
            <span v-else class="muted">暂无报告</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-size="query.page_size"
          :current-page="query.page"
          :page-sizes="[10, 20, 50]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </div>
  <footer class="footer">
  <div class="footer-bar">
    <div class="footer-inner">
      <!-- 左侧：LOGO + 文案 -->
      <div class="footer-left">
        <div class="footer-logo">
          <img src="@/assets/images/ila_logo.png" class="logo-img" alt="ILA" /> 
        </div>

        <div class="footer-text">
          <div class="line">
            Copyright © 2026 版权所有：智能学习与评价江苏省产业技术工程化中心
          </div>
          <div class="line">
            邮箱：2020250606@jsnu.edu.cn　
            地址：江苏省徐州市铜山新区上海路101号
          </div>
        </div>
      </div>

      <!-- 右侧：二维码 -->
      <div class="footer-right">
        <img
          src="@/assets/images/Official_Account1.png"
          alt="官方公众号"
          class="footer-qrcode"
        />
      </div>
    </div>
  </div>
</footer>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { apiGet } from "@/utils/api";
import { useRouter } from "vue-router";
import { useRegionStore } from "@/stores/region";

const router = useRouter();
const regionStore = useRegionStore();

const loadingOverview = ref(false);
const loadingList = ref(false);

const overview = ref({
  region: null,
  school_count: 0,
  has_assessment_count: 0,
  completed_count: 0,
  report_count: 0
});

const list = ref([]);
const total = ref(0);

const query = reactive({
  school_name: "",
  school_type: "",
  status: "",
  time_range: [],
  maturity_level: "",
  page: 1,
  page_size: 20,
  ordering: ""
});

function buildQueryString() {
  const params = new URLSearchParams();

  if (query.school_name) params.set("school_name", query.school_name);
  if (query.school_type) params.set("school_type", query.school_type);
  if (query.status) params.set("status", query.status);
  if (query.maturity_level) params.set("maturity_level", query.maturity_level);

  if (query.time_range && query.time_range.length === 2) {
    params.set("start_at", query.time_range[0]);
    params.set("end_at", query.time_range[1]);
  }

  params.set("page", String(query.page));
  params.set("page_size", String(query.page_size));

  if (query.ordering) params.set("ordering", query.ordering);

  return params.toString();
}

async function loadOverview() {
  loadingOverview.value = true;
  try {
    const { data: resp } = await apiGet("/api/region-admin/overview/");
    if (!resp?.success) throw new Error(resp?.message || "加载失败");

    overview.value = resp.data || {};

    if (overview.value.region) {
      regionStore.setRegion(overview.value.region);
    }
  } catch (e) {
    ElMessage.error(e?.message || "加载失败");
  } finally {
    loadingOverview.value = false;
  }
}

async function loadList() {
  loadingList.value = true;
  try {
    const qs = buildQueryString();
    const { data: resp } = await apiGet(`/api/region-admin/assessments/?${qs}`);
    if (!resp?.success) throw new Error(resp?.message || "加载失败");

    const raw = resp.data?.assessments || [];

    list.value = raw.map((it) => ({
      id: it.id,
      status: it.status,
      maturity_level: it.maturity_level,

      school_id: it.school?.id,
      school_name: it.school?.name || it.school_name || "-",
      school_type: it.school?.school_type || it.school_type || "",

      total_score: it.scores?.total_score ?? it.total_score,
      created_at: it.times?.created_at || it.created_at,

      report_available: !!it.report?.has_report,
      report_url: it.report?.report_url || null
    }));

    total.value = resp.data?.pagination?.total || 0;
  } catch (e) {
    console.error(e);
    ElMessage.error(e?.message || "加载失败");
  } finally {
    loadingList.value = false;
  }
}

async function reloadAll() {
  await Promise.all([loadOverview(), loadList()]);
}

async function handleSearch() {
  query.page = 1;
  await loadList();
}

async function handleReset() {
  query.school_name = "";
  query.school_type = "";
  query.status = "";
  query.time_range = [];
  query.maturity_level = "";
  query.page = 1;
  query.page_size = 20;
  query.ordering = "";
  await loadList();
}

async function handlePageChange(p) {
  query.page = p;
  await loadList();
}

async function handleSizeChange(s) {
  query.page_size = s;
  query.page = 1;
  await loadList();
}

async function handleSortChange({ prop, order }) {
  if (!order) {
    query.ordering = "";
  } else {
    query.ordering = order === "ascending" ? prop : `-${prop}`;
  }
  await loadList();
}

function viewReport(id) {
  if (!id) {
    ElMessage.warning("报告 ID 不存在");
    return;
  }
  router.push(`/school/report/${id}`);
}

function statusLabel(s) {
  const map = {
    draft: "草稿",
    collecting: "数据收集中",
    analyzing: "分析中",
    completed: "已完成"
  };
  return map[s] || "-";
}

function statusTagType(s) {
  if (s === "completed") return "success";
  if (s === "draft") return "info";
  if (s === "collecting") return "warning";
  if (s === "analyzing") return "primary";
  return "info";
}

function maturityLabel(v) {
  const map = {
    leading: "创新级",
    mature: "成熟级",
    growing: "成长级",
    initial: "初始级"
  };
  return map[v] || v || "-";
}

function schoolTypeLabel(v) {
  const map = {
    primary: "小学",
    junior: "初中",
    senior: "高中",
    nine_year: "九年一贯制",
    twelve_year: "十二年一贯制"
  };
  return map[v] || v || "-";
}

function formatScore(v) {
  if (v === null || v === undefined || v === "") return "-";
  const n = Number(v);
  if (Number.isNaN(n)) return "-";
  return n.toFixed(1);
}

onMounted(async () => {
  await reloadAll();
});
</script>

<style scoped>
.page {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}

.block {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  margin-bottom: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 600;
  color: #303133;
}

.stat-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(4, minmax(180px, 1fr));
  gap: 14px;
}

.stat-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 14px 10px;
  text-align: center;
}

.stat-num {
  font-size: 32px;
  font-weight: 700;
  color: #1f5fbf;
  line-height: 1.1;
}

.stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: #606266;
}

.filter-panel {
  padding: 6px 2px 10px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 10px;
}

.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-form .el-form-item {
  margin-bottom: 0;
}

.w-name {
  width: 220px;
}

.w-select {
  width: 140px;
}

.w-date {
  width: 260px !important;
}

.actions {
  margin-left: auto;
  flex-shrink: 0;
}

.actions :deep(.el-form-item__content) {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  align-items: center;
}

.table {
  width: 100%;
}

.score {
  font-weight: 600;
  color: #303133;
}

.muted {
  color: #909399;
  font-size: 12px;
}

.pager {
  padding: 12px 4px 0;
  display: flex;
  justify-content: flex-end;
}

/* 底部页脚 */
/* ===== Footer（深色条，按截图）===== */
.footer {
  margin-top: auto;
  width: 100%;
}

.footer-bar {
  background: #2f3d4a; /* 深蓝灰色背景 */
  padding: 8px 0;    /* 增加上下内边距，让比例更协调 */
}

.footer-inner {
  /* 核心：必须与 header-content 的宽度和对齐逻辑完全一致 */
  max-width: 99%;
  margin: 0 auto;
  padding: 0 20px;    /* 与 header 保持一致的左右内边距 */
  
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
  /* 彻底删除之前的 margin-left: -200px */
}

.footer-logo .logo-img {
  height: 80px;
  width: auto;
  display: block;
}

.footer-text {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;      /* 标准页脚字号 */
  line-height: 1.8;
  text-align: left;
}

.footer-text .line {
  white-space: nowrap; /* 强制不换行，保持整齐 */
}

.footer-right {
  /* 彻底删除之前的 margin-right: -200px */
  display: flex;
  align-items: center;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.footer-qrcode {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  background: #ffffff;
  padding: 3px;
}

.qr-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.contact-note {
  margin-top: 18px;          /* 与邮箱拉开距离 */
  font-size: 13px;           /* 比正文小 */
  color: #9ca3af;            /* 浅灰色 */
  font-style: italic;        /* 微斜体，学术/说明感 */
  line-height: 1.6;
}

@media (max-width: 1200px) {
  .stat-grid {
    grid-template-columns: 1fr 1fr;
  }

  .actions {
    margin-left: 0;
  }
}

@media (max-width: 720px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>