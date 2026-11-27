<template>
  <div class="home-container">
    <!-- 1. 复用 Home.vue 的顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section" @click="router.push('/home')" style="cursor: pointer">
          <h1 class="system-title">中小学校数据文化成熟度评估监测系统</h1>
        </div>
        <nav class="nav-menu">
          <router-link to="/home" class="nav-item">首页</router-link>
          <router-link to="/about" class="nav-item">关于我们</router-link>
          <router-link to="/culture" class="nav-item">数据文化</router-link>
          <router-link to="/guide" class="nav-item">评估说明</router-link>
          <router-link to="/news" class="nav-item">实践动态</router-link>
          <el-dropdown class="user-dropdown">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ schoolName || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </nav>
      </div>
    </header>

    <!-- 2. 主体内容区：替换为评估概览逻辑 -->
    <main class="main-content">
      <div class="overview-section">
        
        <!-- 评估进度卡片 -->
        <el-card class="custom-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="header-title">评估进度</span>
              <el-button @click="router.push('/home')">返回</el-button>
            </div>
          </template>

          <div v-if="activeAssessment" class="progress-container">
            <div class="progress-top">
              <h3 class="assessment-title">
                {{ activeYear }}年{{ activeAssessment.school_name }}数据文化成熟度评估
              </h3>
              <span class="percentage-label">{{ currentProgress }}% 完成</span>
            </div>
            
            <el-progress 
              :percentage="currentProgress"
              :stroke-width="15" 
              color="#ff9800" 
              :show-text="false"
              class="custom-progress"
            />

            <div class="progress-footer">
              <div class="time-box">
                <span>开始时间：{{ formatDate(activeAssessment.created_at) }}</span>
                <span v-if="!activeAssessment.check_survey_quality" class="deadline">截止时间：{{ getDeadline(activeAssessment.created_at) }}</span>
              </div>
              <el-button type="warning" size="large" class="continue-btn" @click="handleContinue">
                继续评估
              </el-button>
            </div>
          </div>
          <el-empty v-else :image-size="100" description="暂无进行中的评估" />
        </el-card>

        <!-- 历史评估记录卡片 -->
        <el-card class="custom-card history-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="header-title">历史评估记录</span>
            </div>
          </template>

          <el-table :data="paginatedHistory" style="width: 100%" v-loading="loading">
            <el-table-column label="评估报告" min-width="300">
              <template #default="scope">
                <span class="report-link">
                  {{ formatYearMonth(scope.row.completed_at || scope.row.created_at) }}{{ scope.row.school_name }}数据文化成熟度评估报告
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="school_name" label="学校名称" min-width="150" />
            <el-table-column label="问卷回收情况" min-width="240">
              <template #default="{ row }"><SurveyCollection :counts="row.survey_collection" /></template>
            </el-table-column>
            <el-table-column label="评估时间" width="200">
              <template #default="scope">
                <!-- 对应准确的评估时间 -->
                {{ formatDate(scope.row.completed_at || scope.row.updated_at) }}
              </template>
            </el-table-column>
            <el-table-column label="评估状态" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'completed' ? 'success' : 'info'" effect="light">
                  {{ scope.row.status === 'completed' ? '已完成' : '处理中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
              <template #default="scope">
                <el-button link type="primary" @click="viewReport(scope.row.id)" :disabled="scope.row.status !== 'completed'">查看</el-button>
                <el-button link type="primary" @click="downloadReport(scope.row.id)" :disabled="scope.row.status !== 'completed'">下载</el-button>
              </template>
            </el-table-column>
          </el-table>
          <!-- 分页工具条 -->
          <div class="pagination-wrapper">
            <!-- 左侧统计 -->
            <div class="pagination-info">
              显示 {{ (currentPage - 1) * pageSize + 1 }} 至 
              {{ Math.min(currentPage * pageSize, historyAssessments.length) }} 条，
              共 {{ historyAssessments.length }} 条记录
            </div>

            <!-- 右侧自定义分页 -->
            <div class="custom-pager">
              <button 
                class="pager-btn" 
                :disabled="currentPage === 1" 
                @click="currentPage--"
              >
                <span>上</span><span>一</span><span>页</span>
              </button>
    
              <div 
                v-for="page in totalPages" 
                :key="page" 
                class="page-number"
                :class="{ active: currentPage === page }"
                @click="currentPage = page"
              >
                {{ page }}
              </div>

              <button 
                class="pager-btn" 
                :disabled="currentPage === totalPages" 
                @click="currentPage++"
              >
                <span>下</span><span>一</span><span>页</span>
              </button>
            </div>
          </div>
        </el-card>

      </div>
    </main>

    <!-- 3. 复用 Home.vue 的底部页脚 -->
    <footer class="footer">
      <div class="footer-bar">
        <div class="footer-inner">
          <div class="footer-left">
            <div class="footer-logo">
              <img src="@/assets/images/ila_logo.png" class="logo-img" alt="ILA" /> 
            </div>
            <div class="footer-text">
              <div class="line">Copyright © 2026 版权所有：智能学习与评价江苏省产业技术工程化中心</div>
              <div class="line">邮箱：2020250606@jsnu.edu.cn　地址：江苏省徐州市铜山新区上海路101号</div>
            </div>
          </div>
          <div class="footer-right">
            <img src="@/assets/images/Official_Account1.png" alt="官方公众号" class="footer-qrcode" />
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import SurveyCollection from '@/components/SurveyCollection.vue'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { getAssessments } from '@/api/assessment'

const router = useRouter()
const loading = ref(false)
const schoolName = ref('')
const assessments = ref([])

const currentPage = ref(1)
const pageSize = ref(10) // 对应你图片中显示的每页3条

const getDeadline = (startTime) => {
  if (!startTime) return ''
  const date = new Date(startTime)
  date.setHours(date.getHours() + 120) // 增加120小时
  
  // 格式化输出 YYYY-MM-DD HH:mm:ss
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')
  const ss = String(date.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${mm}:${ss}`
}

// 2. 计算总页数
const totalPages = computed(() => {
  return Math.ceil(historyAssessments.value.length / pageSize.value) || 1
})

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return historyAssessments.value.slice(start, end)
})



const activeAssessment = computed(() => {
  // 只有草稿状态才显示在顶部的“进度”卡片里，方便用户点击“继续”
  return assessments.value.find(a => a.status === 'draft')
})

// 2. 修改：历史评估记录（展示所有非草稿的记录：处理中、分析中、已完成）
const historyAssessments = computed(() => {
  // 只要不是草稿，都应该出现在下面的列表里
  return assessments.value.filter(a => a.status !== 'draft')
})

const activeYear = new Date().getFullYear()

onMounted(async () => {
  // 1. 获取用户信息
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    const user = JSON.parse(storedUser)
    schoolName.value = user.school_name || user.username || '用户'
  }

  // 2. 获取评估数据
  loading.value = true
  try {
    const res = await getAssessments()
    assessments.value = res
  } catch (error) {
    ElMessage.error('获取评估记录失败')
  } finally {
    loading.value = false
  }
})

const handleContinue = () => router.push('/school/assessment')
const viewReport = (id) => router.push(`/school/report/${id}`)
const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}

// 格式化时间
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return dateStr.replace('T', ' ').substring(0, 19)
}

const downloadReport = (id) => {
  const target = router.resolve({
    path: `/school/report/${id}`,
    query: {
      download: '1',
      iframe: '1'
    }
  })

  const iframe = document.createElement('iframe')
  iframe.src = target.href
  iframe.style.position = 'fixed'
  iframe.style.left = '-9999px'
  iframe.style.top = '-9999px'
  iframe.style.width = '1200px'
  iframe.style.height = '1600px'
  iframe.style.border = '0'

  document.body.appendChild(iframe)

  setTimeout(() => {
    if (iframe.parentNode) {
      iframe.parentNode.removeChild(iframe)
    }
  }, 60000)
}

// 在 script 里面添加这个函数
const formatYearMonth = (dateStr) => {
  if (!dateStr) return '2026年1月' // 兜底显示
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = date.getMonth() + 1 // getMonth() 返回 0-11，所以要加 1
  return `${year}年${month}月`
}

const currentProgress = computed(() => {
  const a = activeAssessment.value;
  // 如果没有数据，或者后端还没返回状态对象，返回 0
  if (!a || !a.module_status) return 0;

  // 直接提取后端返回的模块状态（这些状态直接决定了评估页是否有绿勾）
  const ms = a.module_status;

  // 1. 数据素养：保留你要求的“每份问卷至少各收集1份”逻辑
  // 注意：如果后端 ms.literacy 已经是按“各收1份”算的，直接用 ms.literacy 即可
  const literacyDone = ms.literacy || false;

  // 2. 其他四个模块：直接读取后端状态，确保与“绿色对号”完全同步
  const institutionDone = ms.institution || false;
  const behaviorDone = ms.behavior || false;
  const assetDone = ms.asset || false;
  const technologyDone = ms.technology || false;

  // 3. 统计完成数
  const modules = [literacyDone, institutionDone, behaviorDone, assetDone, technologyDone];
  const doneCount = modules.filter(Boolean).length;

  // 计算百分比：(完成数 / 5) * 100
  return Math.round((doneCount / 5) * 100);
});
</script>

<style scoped>
/* 继承 Home.vue 的基础样式 */
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.header {
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.system-title { font-size: 20px; font-weight: 600; color: #303133; }
.nav-menu { display: flex; align-items: center; gap: 32px; }
.nav-item { color: #606266; text-decoration: none; font-size: 15px; }
.nav-item:hover { color: #409eff; }
.user-info { display: flex; align-items: center; gap: 6px; cursor: pointer; }

.main-content {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 40px;
}

/* 核心概览内容样式 */
.custom-card {
  margin-bottom: 30px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.progress-container {
  padding: 10px 20px;
}

.progress-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.assessment-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0;
}

.percentage-label {
  color: #ff9800;
  font-weight: bold;
  font-size: 18px;
}

.custom-progress {
  margin-bottom: 30px;
}

.progress-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f2f5;
  padding-top: 25px;
}

.time-box {
  color: #909399;
  font-size: 14px;
}

.deadline {
  margin-left: 40px;
}

.continue-btn {
  padding: 12px 40px;
  border-radius: 8px;
  font-weight: 600;
}

/* 历史表格样式 */
.report-link {
  color: #606266;
  font-size: 14px;
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

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-info p {
  font-size: 13px;
  color: #95a5a6;
  margin: 0;
}

.qrcode img {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background-color: white;
}

/* 分页外层容器 */
.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding: 0 10px;
  color: #606266;
  font-size: 14px;
}

/* 右侧按钮组合 */
.custom-pager {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 纵向文字按钮样式 */
.pager-btn {
  display: flex;
  flex-direction: row; /* 关键：文字纵向排列 */
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 32px; /* 根据文字高度调整 */
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  line-height: 1.2;
  color: #606266;
  transition: all 0.3s;
}

.pager-btn span {
  font-size: 12px;
}

.pager-btn:disabled {
  background-color: #f5f7fa;
  color: #c0c4cc;
  cursor: not-allowed;
}

.pager-btn:hover:not(:disabled) {
  border-color: #409eff;
  color: #409eff;
}

/* 页码数字样式 */
.page-number {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-number.active {
  background-color: #f0f7ff;
  border-color: #409eff;
  color: #409eff;
}

.page-number:hover:not(.active) {
  border-color: #409eff;
}
</style>
