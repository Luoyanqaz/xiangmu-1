<template>
  <div class="data-technology-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
            <span class="title">数据技术评价</span>
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
        为全面评价您所在学校"数据技术"建设情况，请您按要求完成以下内容的填写。
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        label-position="top"
        class="technology-form"
        :hide-required-asterisk="true"
        :disabled="isReadonly"
      >
        <!-- 1. 数据基础设施 -->
        <div class="section-title">1. 数据基础设施</div>

        <el-form-item prop="has_independent_data_center">
          <template #label>
            <div class="label-with-hint">
              <span>学校是否设有独立数据中心？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">说明：数据中心指专门用于承载学校各类业务数据的集中存储、服务器部署、网络运维与安全保障的专用物理机房或云端专属服务环境。</p>
                </div>
              </el-popover>
            </div>
          </template>
          <el-radio-group v-model="formData.has_independent_data_center" class="horizontal-radio">
              <el-radio :value="false">未设立独立数据中心</el-radio>
              <el-radio :value="true">已设立独立数据中心</el-radio>
          </el-radio-group>
        </el-form-item>
        
                <el-form-item v-if="formData.has_independent_data_center === true" prop="data_center_standard">
          <template #label>
            <div class="label-with-hint">
              <span>已设立独立数据中心的情况下，数据中心指标达到B级要求的程度？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">学校数据中心的建设标准是否符合GB50174-2017《数据中心设计规范》的对应要求，按实际情况选择对应选项。</p>
                  <p class="hint-example"><em>示例：学校建有独立机房且各项指标完全满足 GB50174-2017 B级要求，则选择「完全达到B级要求」；学校有独立机房但仅部分指标符合B级要求，则选择「部分达到B级要求」；学校有独立机房但未达到 B 级要求，则选择「未达到B级要求」。</em></p>
                  <a
                    class="pdf-link"
                    type="primary"
                    :href="pdfUrl"
                    target="_blank"
                    :underline="false"
                    rel="noopener noreferrer"
                    >
                    查看附件：GB50174-2017《数据中心设计规范》
                   </a>
                </div>
              </el-popover>
            </div>
          </template>
          <el-radio-group v-model="formData.data_center_standard" class="horizontal-radio-with-desc">
            <el-radio value="fully_compliant">
              <div class="radio-content">
                <div class="radio-title">完全达到B级要求</div>
                <div class="radio-desc">设有独立数据中心且完全符合B级要求</div>
              </div>
            </el-radio>
            <el-radio value="partially_compliant">
              <div class="radio-content">
                <div class="radio-title">部分达到B级要求</div>
                <div class="radio-desc">设有独立数据中心且部分符合B级要求</div>
              </div>
            </el-radio>
            <el-radio value="not_compliant">
              <div class="radio-content">
                <div class="radio-title">未达到B级要求</div>
                <div class="radio-desc">设有独立数据中心但不符合B级要求</div>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>

      <!-- 3. 生机比 -->
      <el-form-item prop="student_device_ratio">
        <template #label>
          <div class="label-with-hint">
            <span>学校学生数字终端配备生机比（在校生人数与学生用机数量之比）？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写说明</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">学生数字终端：仅供学生独立自主操作、单人可用的计算机、平板等学习终端，例如学生专用台式电脑、学生平板、云桌面学生终端、学生机房计算机等。</p>
              </div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.student_device_ratio" class="horizontal-radio">
          <el-radio value="low">生机比 < 6:1</el-radio>
          <el-radio value="medium"> 6:1 ≤ 生机比 < 15:1</el-radio>
          <el-radio value="high">生机比 ≥ 15:1</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 4. 师机比 -->
      <el-form-item prop="teacher_device_ratio">
        <template #label>
          <div class="label-with-hint">
            <span>学校教师数字终端配备师机比（专任教师人数与专任教师用机数量之比）？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写说明</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">教师数字终端：可供教师备课、授课、教学使用的全部数字终端，包括教师个人办公设备、教师交互式教学大屏两类设备，例如教学一体机、智能黑板、希沃交互白板、教师办公电脑等。</p>
              </div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.teacher_device_ratio" class="horizontal-radio">
          <el-radio value="low">师机比 < 1:1</el-radio>
          <el-radio value="medium">1:1 ≤ 师机比 < 4:1</el-radio>
          <el-radio value="high">师机比 ≥ 4:1</el-radio>
        </el-radio-group>
      </el-form-item>

                <el-form-item prop="has_data_platform">
          <template #label>
            <div class="label-with-hint">
              <span>学校是否建设数据治理平台，如云平台、专享云服务等，进行数据集中归集、统一管理、共享调用？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">说明：依托区级统一教育平台、校外租用专业教育云服务、学校自主搭建校级云管理平台，实现校内数据集中管控与业务共享，均视为已建设数据治理平台。</p>
                </div>
              </el-popover>
            </div>
          </template>
          <el-radio-group v-model="formData.has_data_platform" class="horizontal-radio-with-desc">
            <el-radio :value="true">
              <div class="radio-content">
                <div class="radio-title">已建立</div>
                <div class="radio-desc">学校已建设数据治理相关平台</div>
              </div>
            </el-radio>
            <el-radio :value="false">
              <div class="radio-content">
                <div class="radio-title">未建立</div>
                <div class="radio-desc">学校未建设数据治理相关平台</div>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 2. 数据安全水平 -->
        <div class="section-title">2. 数据安全水平</div>

        <el-form-item prop="platform_build_mode">
        <template #label>
          <div class="label-with-hint">
            <span>学校部署的各类业务管理、教学平台的建设模式属于：</span>
            <el-popover placement="top-start" :width="420" trigger="hover" popper-class="custom-hint-popper">
            </el-popover>
          </div>
        </template>

        <el-radio-group v-model="formData.platform_build_mode" class="vertical-radio-group">
          <el-radio value="self_built">完全自建平台</el-radio>
          <el-radio value="external">完全接入外部平台</el-radio>
          <el-radio value="mixed">接入外部和自建平台并行</el-radio>
        </el-radio-group>
      </el-form-item>
                    <div class="volume-hint">
                说明：学校部署的各类业务管理或教学平台，主要指教务系统、校园一卡通、综合素质评价平台、考试管理与题库组卷平台、校园门禁出入管理系统等。
              </div>
        
        <template v-if="formData.platform_build_mode === 'self_built' || formData.platform_build_mode === 'mixed'">
        <el-form-item prop="security_certified_count">
            <template #label>
              <div class="label-with-hint">
                <span>学校部署的各类平台通过网络安全等级保护测评的数量？</span>
                <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">

                </el-popover>
              </div>
            </template>
            <div class="inline-inputs">
              <span>已认定</span>
              <el-input-number v-model="formData.security_certified_count" :min="0" :controls="false" />
              <span>个</span>
            </div>
          </el-form-item>

          <!-- 7. 安保等级认定比例 -->
          <el-form-item prop="security_certified_ratio">
            <template #label>
              <div class="label-with-hint">
                <span>学校部署的各类平台通过网络安全等级保护测评的比例</span>
                <el-popover placement="top-start" :width="380" trigger="hover" popper-class="custom-hint-popper">
                
                </el-popover>
              </div>
            </template>

            <el-radio-group
                v-model="formData.security_certified_ratio"
                class="horizontal-radio ratio-radio-group"
              >
                <el-radio value="zero">认定比例 = 0</el-radio>
                <el-radio value="low">0＜认定比例≤40%</el-radio>
                <el-radio value="medium">40%＜认定比例≤80%</el-radio>
                <el-radio value="high">认定比例＞80%</el-radio>
              </el-radio-group>
          </el-form-item>

          <div class="volume-hint">
            说明：请查阅学校部署的各类平台是否通过网络安全等级保护测评，持有二级及以上备案证明或等保测评报告。持有二级及以上材料视为通过，无相关材料或仅一级系统视为未通过。<br />
            定级依据：
            <a class="pdf-link" href="https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=63B89FFF7CC97EBBBED8A403396F0F00" target="_blank" rel="noopener noreferrer">GB/T 22240-2020《信息安全技术 网络安全等级保护定级指南》</a>。<br />
            达标依据：
            <a class="pdf-link" href="https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=BAFB47E8874764186BDB7865E8344DAF" target="_blank" rel="noopener noreferrer">GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》</a>。
          </div>

          </template>

          <!-- 8. 数据风险事件 -->
          <el-form-item prop="has_security_incident">
            <template #label>
              <div class="label-with-hint">
                <span>2023年到2025年，学校是否发生数据风险事件？</span>
                <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                  
                </el-popover>
              </div>
            </template>
            <el-radio-group v-model="formData.has_security_incident" class="horizontal-radio-with-desc">
              <el-radio :value="true">
                <div class="radio-content">
                  <div class="radio-title">有发生</div>
                  <div class="radio-desc">学校发生过数据风险事件</div>
                </div>
              </el-radio>
              <el-radio :value="false">
                <div class="radio-content">
                  <div class="radio-title">未发生</div>
                  <div class="radio-desc">学校未发生过数据风险事件</div>
                </div>
              </el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="volume-hint">
                说明：数据风险事件举例，如学生个人信息、家长联系方式、学籍档案等隐私数据外泄，学校的系统平台遭到外部攻击（如DDoS攻击、病毒攻击等），导致系统宕机或篡改。
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const assessmentId = computed(() => route.params.id)
const pdfUrl = new URL('@/assets/files/GB50174-2017.pdf', import.meta.url).href

const loading = ref(true)
const saving = ref(false)
const formRef = ref(null)
const isReadonly = ref(false)  // 只读模式
const assessmentInfo = ref(null)

// 表单数据
const formData = ref({
  has_independent_data_center: null,
  data_center_standard: null,

  // 旧字段先保留，但新版前端不再展示、不再参与计分
  cloud_dedicated_service: null,

  student_device_ratio: null,
  teacher_device_ratio: null,
  has_data_platform: null,

  // E21 新增：平台建设管理模式
  platform_build_mode: '',

  security_certified_count: null,
  security_certified_ratio: null,
  has_security_incident: null
})

const isAssessmentExpired = (assessmentData) => {
  const startTime = assessmentData?.started_at || assessmentData?.created_at

  if (!startTime) return false

  const start = new Date(startTime).getTime()

  if (!Number.isFinite(start)) return false

  const expire = start + 120 * 60 * 60 * 1000

  return Date.now() > expire
}

const isAssessmentReadonly = (assessmentData) => {
  if (!assessmentData) return false

  // 只有整份评估最终提交完成，或超过120小时，才只读
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

    // 获取数据技术数据
    const response = await fetch(`/api/assessments/${assessmentId.value}/technology/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('数据技术信息加载失败')
    }

    const data = await response.json()
    Object.assign(formData.value, data)

    // 兼容旧数据，避免新增字段为空时影响页面联动
    if (!formData.value.platform_build_mode) {
      formData.value.platform_build_mode = ''
    }
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
    const response = await fetch(`/api/assessments/${assessmentId.value}/save_technology/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(formData.value)
    })

    if (!response.ok) {
      throw new Error('保存失败')
    }

    const savedData = await response.json().catch(() => null)

    if (savedData && typeof savedData === 'object') {
      Object.assign(formData.value, savedData)
    }

    ElMessage.success('保存成功')
  } catch (error) {
    console.log('保存数据:', formData.value)
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败')
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

watch(() => formData.value.has_independent_data_center, (newVal) => {
  if (newVal === true) {
    formData.value.cloud_dedicated_service = null
  } else if (newVal === false) {
    formData.value.data_center_standard = null
    formData.value.cloud_dedicated_service = null
  }
})

watch(() => formData.value.platform_build_mode, (newVal) => {
  if (newVal === 'external') {
    formData.value.security_certified_count = null
    formData.value.security_certified_ratio = null
  }
})
</script>

<style scoped>
.data-technology-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.pdf-link {
  display: inline-block;
  margin-top: 8px;
  color: #409eff;
  text-decoration: none;
  font-size: 13px;
}

.pdf-link:hover {
  text-decoration: underline;
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

.technology-form {
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

.inline-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

:deep(.horizontal-radio) {
  flex-direction: row;
  gap: 20px;
  flex-wrap: wrap;
  padding: 15px;
  border-radius: 4px;
  width: 100%;
}

/* 调整只读模式下的样式，使其更清晰 */
.el-form-item.is-disabled :deep(.el-radio__label) {
  color: #606266;
}

.radio-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.radio-title {
  font-weight: 500;
  color: #303133;
}

.radio-desc {
  font-size: 12px;
  color: #909399;
}

:deep(.el-form-item) {
  margin-bottom: 34px;
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
  width: 120px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: center;
}

/* 默认纵向排列的单选按钮组 */
:deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

:deep(.el-radio) {
  margin-right: 0;
  height: auto;
  align-items: center;
}

:deep(.el-radio__input) {
  align-self: flex-start;
  margin-top: 2px;
}

:deep(.el-radio__label) {
  white-space: normal;
  line-height: 1.5;
  padding-left: 8px;
}

/* 横向排列的单选按钮组(简单选项) */
:deep(.horizontal-radio) {
  flex-direction: row;
  gap: 30px;
  flex-wrap: wrap;
}

:deep(.horizontal-radio .el-radio) {
  margin-right: 0;
}

/* 横向排列的单选按钮组(带描述) */
:deep(.horizontal-radio-with-desc) {
  flex-direction: row;
  gap: 30px;
  flex-wrap: wrap;
}

:deep(.horizontal-radio-with-desc .el-radio) {
  margin-right: 0;
  flex: 0 0 auto;
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

/* 标题与提示并列的布局容器 */
.label-with-hint {
  display: flex;
  align-items: center;
  flex-wrap: wrap; /* 如果标题太长，允许提示换行 */
  gap: 10px;
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

.volume-hint,
.form-tip {
  width: 100%;
  margin-top: 14px;
  margin-bottom: 22px;
  padding: 12px 20px;
  background-color: #fdf6ec;
  border-radius: 0;
  font-size: 14px;
  line-height: 1.8;
  color: #e6a23c;
  box-sizing: border-box;
}

.vertical-radio-group {
  width: 100%;
  display: flex !important;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.vertical-radio-group :deep(.el-radio) {
  width: 100%;
  height: auto;
  margin-right: 0;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}

.vertical-radio-group :deep(.el-radio__label) {
  white-space: normal;
  line-height: 1.6;
  text-align: left;
}

.form-tip {
  width: 100%;
  margin-top: 14px;
  margin-bottom: 22px;
  padding: 12px 20px;
  background-color: #fdf6ec;
  border-radius: 0;
  font-size: 16px;
  line-height: 1.8;
  color: #e6a23c;
  box-sizing: border-box;
}

:deep(.el-form-item__content) {
  flex-wrap: wrap;
  align-items: flex-start;
}

</style>
