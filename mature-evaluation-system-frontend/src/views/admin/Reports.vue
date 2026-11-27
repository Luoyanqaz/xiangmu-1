<template>
  <div class="admin-reports-page">
    <!-- 1. 顶部省份区域分组视图 -->
    <div class="province-group-section">
      <el-card 
        v-for="province in provinceData" 
        :key="province?.name || Math.random()" 
        class="province-card" 
        shadow="never"
      >
        <template #header>
          <div class="province-header" v-if="province">
            <span class="province-name">{{ province.name }}</span>
            <span class="province-summary">

              共 <strong>{{ (province.cities || []).length }}</strong> 个市区 · 
              <strong>{{ province.total_schools || 0 }}</strong> 所学校
            </span>
          </div>
        </template>
        
        <div class="region-grid">
        <div
          v-for="region in getDistrictRegions(province)"
          :key="region.key"
          class="region-item"
        >
          <span class="region-name">{{ region.displayName }}</span>

          <div class="region-actions">
            <el-button link type="primary" @click="viewRegionReport(region)">查看区域报告</el-button>
            <el-button link type="primary" @click="showCollection(region)">问卷回收情况</el-button>
          </div>
        </div>
      </div>
      </el-card>
    </div>

    <el-drawer v-model="collectionOpen" :title="(collectionRegion?.district || '') + ' · 问卷回收情况'"
               size="min(520px, 100%)">
      <p v-if="collectionLoading" role="status">正在加载问卷回收情况…</p>
      <div v-else-if="collectionError" role="alert">
        问卷回收情况加载失败。
        <el-button link type="primary" @click="showCollection(collectionRegion)">重试</el-button>
      </div>
      <template v-else-if="collection">
        <div class="collection-table-wrap">
          <table class="collection-table">
            <thead><tr><th>问卷类型</th><th>回收总数</th><th>有效</th><th>无效</th><th>历史未判定</th></tr></thead>
            <tbody>
              <tr v-for="(label, role) in { teacher: '教师问卷', student: '学生问卷' }" :key="role">
                <th scope="row">{{ label }}</th>
                <td>{{ collection[role].received }}</td><td>{{ collection[role].valid }}</td>
                <td>{{ collection[role].invalid }}</td><td>{{ collection[role].unjudged }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="collection-note">每所学校取最近一次已完成评估。历史未判定指启用有效性校验前回收的问卷。</p>
        <p v-if="collection.shortages.teacher || collection.shortages.student || collection.shortages.both">
          有效样本不足学校：仅教师 {{ collection.shortages.teacher }} 所，仅学生 {{ collection.shortages.student }} 所，两类均不足 {{ collection.shortages.both }} 所。
        </p>
      </template>
    </el-drawer>

    <!-- 2. 学校评估列表及筛选 -->
    <el-card shadow="never" class="list-section">
      <!-- 搜索筛选条 -->
      <div class="filter-container">
  <el-form :inline="true" :model="filters" size="default">
    
    <!-- 1. 所属区域 -->
    <el-form-item label="所属区域">
        <el-cascader
          v-model="filters.regionCodes"
          :options="chinaArea"
          clearable
          :props="{ checkStrictly: true }"
        />
      </el-form-item>

    <!-- 2. 学校名称 -->
    <el-form-item label="学校名称">
      <el-input v-model="filters.school_name" placeholder="请输入学校名称" clearable style="width: 200px" />
    </el-form-item>

    <!-- 3. 状态 -->
    <el-form-item label="状态">
      <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 130px">
        <el-option label="草稿" value="draft" />
        <el-option label="采集中" value="collecting" />
        <el-option label="已完成" value="completed" />
      </el-select>
    </el-form-item>

    <!-- 4. 成熟度等级 -->
    <el-form-item label="成熟度等级">
      <el-select v-model="filters.level" placeholder="全部等级" clearable style="width: 130px">
        <el-option label="初始级" value="初始级" />
        <el-option label="成长级" value="成长级" />
        <el-option label="成熟级" value="成熟级" />
        <el-option label="创新级" value="创新级" />
      </el-select>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSearch">查询</el-button>
      <el-button @click="handleReset">重置</el-button>
    </el-form-item>

  </el-form> <!-- 第 80 行左右：确保这里只有一个闭合 -->
</div>

      <!-- 数据表格 -->
      <el-table :data="listData" v-loading="loadingList" stripe style="width: 100%">
        <el-table-column label="序号" width="80" align="center">
  <template #default="{ $index }">
    {{ (page - 1) * pageSize + $index + 1 }}
  </template>
</el-table-column>
        <el-table-column prop="district" label="所属区域" width="120" />
        <el-table-column prop="school_name" label="学校名称" min-width="220" />
        <el-table-column prop="status" label="评估状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'" effect="light">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="总分" width="100" align="center">
          <template #default="{ row }">
             {{ row.status === 'completed' ? row.total_score : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="maturity_level_display" label="成熟度等级" width="120" align="center">
          <template #default="{ row }">
             <span :class="['level-text', row.maturity_level]">{{ row.maturity_level_display || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" sortable />
        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <el-button v-if="row.status === 'completed'" link type="primary" @click="viewReport(row.id)">查看报告</el-button>
            <span v-else style="color: #909399; font-size: 13px">暂无报告</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-footer">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          v-model:current-page="page"
          v-model:page-size="pageSize"
          @current-change="applyFilters"
          @size-change="applyFilters"
        />
      </div>
    </el-card>
  </div>
  <!-- 底部页脚 -->
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/api/request'
import { regionData, codeToText } from 'element-china-area-data'

const chinaArea = regionData

const filters = reactive({
  school_name: '',
  regionCodes: [],
  status: '',
  level: ''
})

const router = useRouter()
const loading = ref(false)

// --- 顶部省份区域数据 ---
const provinceData = ref([])

// --- 表格数据 ---
const listData = ref([])
const totalCount = ref(0)
const page = ref(1)
const pageSize = ref(20)

// --- 原始数据（核心）---
const allRawData = ref([])

// --- 下拉区域 ---
const allDistricts = ref([])

/* ======================
   工具函数（统一字段）
====================== */
const getArea = (item) => {
  return item.district || item.city || item.school?.city || ''
}

/* ======================
   顶部数据
====================== */
const fetchSummaryData = async () => {
  try {
    const res = await request.get('/province-summary/')
    const root = res.data || res
    const actualData = root.data || root

    provinceData.value = Array.isArray(actualData) ? actualData : []
  } catch (e) {
    console.error('加载汇总数据失败:', e)
    provinceData.value = []
  }
}

const buildProvinceDistrictSummary = (rows) => {
  const provinceMap = new Map()

  ;(rows || []).forEach((item) => {
    const school = item.school || {}

    const province = item.province || school.province || item.school_province || ''
    const city = item.city || school.city || item.school_city || ''
    const district = item.district || school.district || item.school_district || ''

    const schoolId =
      item.school_id ||
      school.id ||
      item.school?.id ||
      item.school_name ||
      school.name ||
      item.id

    if (!province || !city || !district) {
      return
    }

    if (!provinceMap.has(province)) {
      provinceMap.set(province, {
        name: province,
        total_schools: 0,
        schoolSet: new Set(),
        cityMap: new Map()
      })
    }

    const provinceItem = provinceMap.get(province)
    provinceItem.schoolSet.add(schoolId)

    if (!provinceItem.cityMap.has(city)) {
      provinceItem.cityMap.set(city, {
        name: city,
        total_schools: 0,
        schoolSet: new Set(),
        districtMap: new Map()
      })
    }

    const cityItem = provinceItem.cityMap.get(city)
    cityItem.schoolSet.add(schoolId)

    if (!cityItem.districtMap.has(district)) {
      cityItem.districtMap.set(district, {
        name: district,
        total_schools: 0,
        schoolSet: new Set()
      })
    }

    const districtItem = cityItem.districtMap.get(district)
    districtItem.schoolSet.add(schoolId)
  })

  return Array.from(provinceMap.values()).map((province) => {
    const cities = Array.from(province.cityMap.values()).map((city) => {
      const districts = Array.from(city.districtMap.values()).map((district) => ({
        name: district.name,
        total_schools: district.schoolSet.size
      }))

      return {
        name: city.name,
        total_schools: city.schoolSet.size,
        districts
      }
    })

    return {
      name: province.name,
      total_schools: province.schoolSet.size,
      cities
    }
  })
}

const getDistrictRegions = (province) => {
  const result = []
  const provinceName = province?.name || ''

  ;(province?.cities || []).forEach((city) => {
    const cityName = city?.name || ''
    const districts = city?.districts || []

    districts.forEach((district) => {
      const districtName = district?.name || district?.district || ''

      result.push({
        key: `${provinceName}-${cityName}-${districtName}`,
        province: district?.province || provinceName,
        city: district?.city || cityName,
        district: district?.district || districtName,
        region_id: district?.region_id || '',
        total_schools: district?.total_schools || district?.school_count || 0,
        displayName: `${cityName}${districtName}`
      })
    })
  })

  return result
}

const regionParams = ({ region_id, province, city, district }) => ({ region_id, province, city, district })

const viewRegionReport = (region) => {
  router.push({
    path: '/admin/region-report-detail',
    query: regionParams(region)
  })
}

const collectionOpen = ref(false)
const collectionRegion = ref(null)
const collection = ref(null)
const collectionLoading = ref(false)
const collectionError = ref(false)
let collectionRequest = 0

const showCollection = async (region) => {
  const requestId = ++collectionRequest
  collectionRegion.value = region
  collectionOpen.value = true
  collectionLoading.value = true
  collectionError.value = false
  collection.value = null
  try {
    const response = await request.get('/admin/region-report/survey-collection/', { params: regionParams(region) })
    if (requestId === collectionRequest) collection.value = response.data
  } catch {
    if (requestId === collectionRequest) collectionError.value = true
  } finally {
    if (requestId === collectionRequest) collectionLoading.value = false
  }
}

/* ======================
   表格数据（只负责拿数据）
====================== */
const fetchTableData = async () => {
  loading.value = true

  let prov = '', city = '', dist = ''
  if (filters.regionCodes?.length > 0) {
    prov = codeToText[filters.regionCodes[0]]
    city = codeToText[filters.regionCodes[1]] || ''
    dist = codeToText[filters.regionCodes[2]] || ''
  }

  try {
    const res = await request.get('/assessment-list/', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        school_name: filters.school_name,
        status: filters.status,
        level: filters.level,
        province: prov,
        city: city,
        district: dist
      }
    })

    const root = res.data || res
    listData.value = root.results || []
    totalCount.value = root.count || 0

  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

/* ======================
   核心过滤逻辑（唯一入口）
====================== */
const applyFilters = () => {
  let filtered = allRawData.value

  // 学校名
  if (filters.school_name) {
    filtered = filtered.filter(item =>
      item.school_name?.includes(filters.school_name)
    )
  }

  // 区域
  if (filters.district) {
    filtered = filtered.filter(item =>
      getArea(item) === filters.district
    )
  }

  // 状态
  if (filters.status) {
    filtered = filtered.filter(item =>
      item.status === filters.status
    )
  }

  // 等级
  if (filters.level) {
    filtered = filtered.filter(item => {
      const level = item.maturity_level_display || item.maturity_level
      return level === filters.level
    })
  }

  // 分页
  totalCount.value = filtered.length
  const start = (page.value - 1) * pageSize.value
  listData.value = filtered.slice(start, start + pageSize.value)
}

/* ======================
   交互
====================== */
const handleSearch = () => {
  page.value = 1
  fetchTableData()
}

const handleReset = () => {
  Object.keys(filters).forEach(k => filters[k] = '')
  handleSearch()
}

const getStatusLabel = (s) => ({
  draft: '草稿',
  collecting: '采集中',
  completed: '已完成'
}[s] || s)

const viewReport = (id) => {
  router.push(`/school/report/${id}`)
}


/* ======================
   生命周期
====================== */
onMounted(() => {
  fetchSummaryData()
  fetchTableData()
})
</script>

<style scoped>
.admin-reports-page {
  padding: 20px;
  background-color: #f4f6f9;
  min-height: 100vh;
}

/* 省份卡片样式 */
.province-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.province-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.province-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.province-summary {
  font-size: 14px;
  color: #606266;
}

.province-summary strong {
  color: #409eff;
  margin: 0 4px;
}

/* 区域网格 */
.region-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.region-item {
  box-sizing: border-box;
  flex-wrap: wrap;
  gap: 8px;
  width: calc(33.33% - 10px);
  background-color: #f8fbff;
  border: 1px solid #e1f0ff;
  padding: 12px 20px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.region-name {
  font-size: 15px;
  color: #303133;
  font-weight: 500;
}

.region-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
.region-actions .el-button { margin: 0; }
.collection-table-wrap { overflow-x: auto; }
.collection-table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.collection-table th, .collection-table td {
  padding: 12px 8px; text-align: right; white-space: nowrap; border-bottom: 1px solid #e4e9f0;
}
.collection-table th:first-child { text-align: left; }
.collection-table thead { background: #f4f7fb; }
.collection-note { color: #606266; font-size: 14px; line-height: 1.6; }

/* 列表筛选区 */
.list-section {
  border-radius: 8px;
}

.filter-container {
  background-color: #fafafa;
  padding: 18px 20px 0;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #eee;
}

/* 等级文字颜色 */
.level-text.initial { color: #909399; }
.level-text.growing { color: #409eff; }
.level-text.mature { color: #67c23a; }
.level-text.leading { color: #f56c6c; }

.pagination-footer {
  margin-top: 25px;
  display: flex;
  justify-content: flex-end;
}

.copyright {
  text-align: center;
  padding: 30px 0;
  color: #9ca3af;
  font-size: 13px;
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

/* 响应式适配 */
@media (max-width: 1200px) {
  .region-item { width: calc(50% - 10px); }
}
@media (max-width: 700px) {
  .region-item { width: 100%; }
}
</style>
