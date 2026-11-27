<template>
  <div class="data-asset-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
            <span class="title">数据资产评价</span>
            <el-tag v-if="isReadonly" type="info" style="margin-left: 10px">只读模式</el-tag>
          </div>
          <el-button type="primary" @click="handleSave" :loading="saving" v-if="!isReadonly">
            保存
          </el-button>
        </div>
      </template>

      <el-alert
        v-if="isReadonly"
        :title="readonlyTip"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-alert
        v-else
        title="评价说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        为全面评价您所在学校"数据资产"建设情况，请您按要求完成以下内容的填写。
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        label-position="top"
        class="asset-form"
        :hide-required-asterisk="true"
        :disabled="isReadonly"
      >
        <!-- 1. 数据资产意识 -->
        <div class="section-title">1. 数据资产意识</div>
        
        <div class="section-subtitle">教师的数据资产意识</div>
        
        <el-alert
          type="success"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <p>该维度将通过问卷调查的方式，了解教师的数据资产意识。为便于数据采集，同卷（<strong>中小学校教师数据资产意识调查问卷</strong>）已全部整合到"数据素养评价"板块。</p>
        </el-alert>

        <!-- 2. 数据资产积累 -->
      <!-- 2. 数据资产积累 -->
      <div class="section-title">2. 数据资产积累</div>

      <div class="form-section">
        <el-form-item>
          <template #label>
            <div class="label-with-hint">
              <span>学校是否对校内数据资产进行统一管理或统筹管理（包括区域平台统一管理、学校自主管理）？</span>
            </div>
          </template>

          <el-radio-group v-model="formData.has_unified_data_management" class="inline-radio-group">
            <el-radio :label="true">是</el-radio>
            <el-radio :label="false">否</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="formData.has_unified_data_management === true">
          <template #label>
            <div class="label-with-hint">
              <span>学校是否能够通过相关平台、系统等，对校内主要数据资源进行统计查询？</span>
            </div>
          </template>

          <el-radio-group v-model="formData.can_query_data_assets" class="inline-radio-group">
            <el-radio :label="true">是</el-radio>
            <el-radio :label="false">否</el-radio>
          </el-radio-group>
        </el-form-item>

        <div
          v-if="formData.has_unified_data_management === false || formData.can_query_data_assets === false"
          class="form-tip"
        >
          当前选择下，系统将根据计分规则直接赋予数据资产总量对应分值，无需继续填写各类数据总量。
        </div>

        <template v-if="formData.has_unified_data_management === true && formData.can_query_data_assets === true">
          <div class="form-section-label data-volume-label-row">
          <span>数据资产统计：教育教学、师生管理、数字资源、校园管理与行政以及其他类型数据总量：</span>

          <el-popover
            placement="top-start"
            :width="300"
            trigger="hover"
            popper-class="custom-hint-popper"
          >
            <template #reference>
              <span class="hint-tag">填写说明</span>
            </template>

            <div class="hint-body">
              <p class="hint-text">
                说明：数据资产包括教育教学数据（学生学习数据、教师教学数据）、师生管理数据（基本信息数据、心理生理健康数据等）、数字资源数据（电子教材与教案、学科资料库等）、校园管理与行政数据（财务数据、安全管理数据等）等。
              </p>
            </div>
          </el-popover>
        </div>
          <div class="data-volume-section">
            <!-- 教育教学数据 -->
            <div class="data-volume-block">
              <div class="volume-title">教育教学数据总量</div>

              <el-radio-group v-model="formData.teaching_data_stat_method" class="stat-method-group">
                <el-radio label="unable">无法统计</el-radio>
                <el-radio label="estimated">可部分估算</el-radio>
                <el-radio label="system_query">可系统查询</el-radio>
              </el-radio-group>

              <div
                v-if="formData.teaching_data_stat_method === 'estimated' || formData.teaching_data_stat_method === 'system_query'"
                class="data-volume-item"
              >
                <span class="volume-label">数据总量</span>
                <el-input-number v-model="formData.teaching_data_volume" :min="0" :controls="false" />
                <span style="font-size: 14px;">GB</span>
              </div>

              <div class="volume-hint">
                数据来源示例：中小学日常教学相关数据，如课程安排、授课计划、考试成绩、作业信息、课堂考勤、教研活动记录等。<br>
                统计方式示例：可通过学校教学管理系统、学习平台或成绩管理系统的数据库，统计教育教学数据的总量；具体统计方式可根据学校实际情况进行调整。
              </div>
            </div>

            <!-- 师生管理数据 -->
            <div class="data-volume-block">
              <div class="volume-title">师生管理数据总量</div>

              <el-radio-group v-model="formData.teacher_student_data_stat_method" class="stat-method-group">
                <el-radio label="unable">无法统计</el-radio>
                <el-radio label="estimated">可部分估算</el-radio>
                <el-radio label="system_query">可系统查询</el-radio>
              </el-radio-group>

              <div
                v-if="formData.teacher_student_data_stat_method === 'estimated' || formData.teacher_student_data_stat_method === 'system_query'"
                class="data-volume-item"
              >
                <span class="volume-label">数据总量</span>
                <el-input-number v-model="formData.teacher_student_data_volume" :min="0" :controls="false" />
                <span style="font-size: 14px;">GB</span>
              </div>

              <div class="volume-hint">
                数据来源示例：师生个人信息、班级花名册、出勤记录、奖惩记录、健康与安全信息等。<br>
                统计方式示例：可通过人事管理系统、学生管理系统或电子班牌等，汇总所有师生管理相关数据总量；具体统计方式可根据学校实际情况进行调整。
              </div>
            </div>

            <!-- 数字资源数据 -->
            <div class="data-volume-block">
              <div class="volume-title">数字资源数据总量</div>

              <el-radio-group v-model="formData.digital_resource_data_stat_method" class="stat-method-group">
                <el-radio label="unable">无法统计</el-radio>
                <el-radio label="estimated">可部分估算</el-radio>
                <el-radio label="system_query">可系统查询</el-radio>
              </el-radio-group>

              <div
                v-if="formData.digital_resource_data_stat_method === 'estimated' || formData.digital_resource_data_stat_method === 'system_query'"
                class="data-volume-item"
              >
                <span class="volume-label">数据总量</span>
                <el-input-number v-model="formData.digital_resource_data_volume" :min="0" :controls="false" />
                <span style="font-size: 14px;">GB</span>
              </div>

              <div class="volume-hint">
                数据来源示例：学校存储的各类数字教学资源，如课件教案、微课视频、习题题库、电子图书、校本教材、研学资料等。<br>
                统计方式示例：可查看学校资源库平台、校园云盘、校本资源服务器存储后台，统计资源存储总量；具体统计方式可根据学校实际情况进行调整。
              </div>
            </div>

            <!-- 校园管理与行政数据 -->
            <div class="data-volume-block">
              <div class="volume-title">校园管理与行政数据总量</div>

              <el-radio-group v-model="formData.campus_admin_data_stat_method" class="stat-method-group">
                <el-radio label="unable">无法统计</el-radio>
                <el-radio label="estimated">可部分估算</el-radio>
                <el-radio label="system_query">可系统查询</el-radio>
              </el-radio-group>

              <div
                v-if="formData.campus_admin_data_stat_method === 'estimated' || formData.campus_admin_data_stat_method === 'system_query'"
                class="data-volume-item"
              >
                <span class="volume-label">数据总量</span>
                <el-input-number v-model="formData.campus_admin_data_volume" :min="0" :controls="false" />
                <span style="font-size: 14px;">GB</span>
              </div>

              <div class="volume-hint">
                数据来源示例：校园后勤安保、校舍资产、设备耗材、食堂管理、门禁出入、会议通知、公文流转、财务报销、安全台账等校园行政后勤数据。<br>
                统计方式示例：可通过校园后勤管理系统、行政办公系统、资产台账系统等，统计校园管理与行政数据总量；具体统计方式可根据学校实际情况进行调整。
              </div>
            </div>

            <!-- 其他类型数据 -->
            <div class="data-volume-block">
              <div class="volume-title">其他类型数据（选填）</div>

              <div class="data-volume-item">
                <span class="volume-label">数据总量</span>
                <el-input-number v-model="formData.other_type_data_volume" :min="0" :controls="false" />
                <span style="font-size: 14px;">GB</span>
              </div>

              <div class="volume-hint">
                数据来源示例：如校园安防数据、图书馆借阅数据、食堂消费数据、校车使用记录等。<br>
                统计方式示例：可将学校未分类数据量进行汇总，得到其他类型数据总量；具体统计方式可根据学校实际情况进行调整。
              </div>
            </div>
          </div>
        </template>
      </div>
      </el-form>
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const assessmentId = computed(() => route.params.id)

const loading = ref(true)
const saving = ref(false)
const formRef = ref(null)
const isReadonly = ref(false)  // 只读模式
const assessmentInfo = ref(null)

// 表单数据
const formData = ref({
  // D21 前置判断
  has_unified_data_management: null,
  can_query_data_assets: null,

  // 教育教学数据
  teaching_data_stat_method: '',
  teaching_data_volume: null,

  // 师生管理数据
  teacher_student_data_stat_method: '',
  teacher_student_data_volume: null,

  // 数字资源数据
  digital_resource_data_stat_method: '',
  digital_resource_data_volume: null,

  // 校园管理与行政数据
  campus_admin_data_stat_method: '',
  campus_admin_data_volume: null,

  // 其他类型数据
  other_type_data_volume: null,

  // 旧字段先保留，避免旧数据或后端兼容问题
  management_data_volume: null,
  resource_data_volume: null,
  service_data_volume: null,
  other_data_volume: null
})

const isAssessmentExpired = (assessmentData) => {
  if (assessmentData?.check_survey_quality) return false
  const startTime = assessmentData?.started_at || assessmentData?.created_at

  if (!startTime) return false

  const start = new Date(startTime).getTime()

  if (!Number.isFinite(start)) return false

  const expire = start + 120 * 60 * 60 * 1000

  return Date.now() > expire
}

const isAssessmentReadonly = (assessmentData) => {
  if (!assessmentData) return false

  // 只有整份评估最终提交完成，或超过120小时，才进入只读
  return assessmentData.status === 'completed' || isAssessmentExpired(assessmentData)
}

const readonlyTip = computed(() => {
  if (assessmentInfo.value?.status === 'completed') {
    return '评价已完成，当前为只读模式，无法修改数据'
  }

  if (isAssessmentExpired(assessmentInfo.value)) {
    return '本次评估已超过120小时填报期限，当前为只读模式，无法修改数据'
  }

  return ''
})

// 加载数据
const loadData = async () => {
  loading.value = true

  try {
    const token = localStorage.getItem('access_token')

    // 先获取评估状态
    const assessmentResponse = await fetch(`/api/assessments/${assessmentId.value}/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!assessmentResponse.ok) {
      throw new Error('评估信息加载失败')
    }

    const assessmentData = await assessmentResponse.json()

    assessmentInfo.value = assessmentData
    isReadonly.value = isAssessmentReadonly(assessmentData)

    // 获取数据资产数据
    const response = await fetch(`/api/assessments/${assessmentId.value}/asset/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('数据资产信息加载失败')
    }

    const data = await response.json()
    Object.assign(formData.value, data)

    // 兼容旧数据，避免新版字段为 null 时影响表单显示
    const statMethodFields = [
      'teaching_data_stat_method',
      'teacher_student_data_stat_method',
      'digital_resource_data_stat_method',
      'campus_admin_data_stat_method'
    ]

    statMethodFields.forEach((field) => {
      if (!formData.value[field]) {
        formData.value[field] = ''
      }
    })
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 保存数据
const handleSave = async () => {
  saving.value = true
  try {
    const response = await fetch(`/api/assessments/${assessmentId.value}/save_asset/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(formData.value)
    })
    
    if (response.ok) {
      ElMessage.success('保存成功')
    } else {
      throw new Error('保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 返回评估导航页面
const handleBack = () => {
  router.push('/school/assessment')
}

// 自动保存（只读模式下不自动保存）
let autoSaveTimer = null
const startAutoSave = () => {
  if (isReadonly.value) return
  autoSaveTimer = setInterval(() => {
    if (!isReadonly.value) {
      handleSave()
    }
  }, 120000) // 2分钟自动保存一次
}

onMounted(async () => {
  await loadData()
  startAutoSave()
})

onBeforeUnmount(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
})
</script>

<style scoped>
.data-asset-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.asset-form {
  margin-top: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin: 30px 0 20px 0;
  padding-left: 0;
  border-left: none;
}

.section-subtitle {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
}

.inline-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
  line-height: 1.6;
}

.data-volume-section {
  width: 100%;
  padding-left: 20px;
}

.data-volume-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.volume-hint {
  font-size: 12px;
  color: #909399;
  line-height: 1.6;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

:deep(.el-form-item) {
  margin-bottom: 34x;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  line-height: 1.6;
  white-space: normal;
  word-break: break-word;
  margin-bottom: 8px;
  color: #303133;
}

:deep(.el-form-item__content) {
  flex-wrap: wrap;
}

:deep(.el-input-number) {
  width: 150px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: center;
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

.label-with-hint {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.inline-radio-group {
  display: flex;
  gap: 30px;
  align-items: center;
}

.stat-method-group {
  width: 100%;
  display: flex;
  gap: 30px;
  align-items: center;
  margin-bottom: 12px;
}

.data-volume-section {
  width: 100%;
  padding-left: 0;
}

.data-volume-block {
  margin-bottom: 22px;
  padding: 18px;
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
}

.volume-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.data-volume-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.volume-label {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
}

.volume-hint,
.form-tip {
  width: 100%;
  margin-top: 14px;
  margin-bottom: 22px;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.8;
  color: #909399;
  box-sizing: border-box;
}

:deep(.el-form-item__content) {
  flex-wrap: wrap;
  align-items: flex-start;
}

/* 填写提示小标签样式 */
.hint-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 10px;
  font-size: 12px;
  color: #409eff;
  background-color: #ecf5ff;
  border: 1px solid #cfe5ff;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap; /* 强制标签不换行 */
  transition: all 0.2s;
  line-height: 1.2;
}

.hint-tag:hover {
  background-color: #409eff;
  color: #ffffff;
}

/* 弹出框内容样式 */
.hint-body {
  padding: 8px 4px;
}

.hint-text {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  margin-bottom: 10px;
}

.hint-example {
  font-size: 13px;
  line-height: 1.5;
  color: #909399;
}

.hint-example em {
  font-style: italic;
}

.data-volume-label-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 22px;
  line-height: 1.8;
}
</style>
