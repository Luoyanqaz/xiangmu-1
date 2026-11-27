<template>
  <div class="data-institution-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
            <span class="title">数据制度评价</span>
            <el-tag v-if="isReadonly" type="info" style="margin-left: 10px">只读模式</el-tag>
          </div>
          <el-button type="primary" @click="handleSave" :loading="saving" :disabled="isReadonly" v-if="!isReadonly">
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
        为全面评价您所在学校"数据制度"建设情况，请您按要求完成以下内容的填写。
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        class="institution-form"
        :hide-required-asterisk="true"
        :disabled="isReadonly"
      >
        <!-- 1. 数据组织机构 -->
        <div class="section-title">1. 数据组织机构</div>
        
        <el-form-item prop="leadership_group_type">
        <template #label>
          <div class="label-with-hint">
            <span>学校是否设置对数据进行收集、存储与管理或整体规划的领导小组或工作小组？</span>
            <el-popover placement="top-start" :width="460" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写说明</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">
                  规范管理型：专人分工负责全校数据的体系化管理，涵盖数据的收集、存储、分析、应用和整体规划，职责分工明确。</p>
                <p class="hint-example"><em>例如：由校长担任总负责人，信息中心主任为分管负责人，其他行政部门、年级组指派专人组成小组，统筹全校各类教学、管理等数据的采集、归档、分析和规划。</em></p>
                <p class="hint-text">基础管理型：小组成员多为兼任人员，负责学校数据的日常登记、数据整理、常规维护等工作，但缺乏整体规划。</p>
                <p class="hint-example"><em>例如：由信息技术教师、机房管理人员、行政内勤等兼任的人员组成小组，负责设备登记、教学数据记录、电脑及机房设备借阅登记等基础工作。虽然为小组形式，但没有专门的负责人统筹管理。</em></p>
              </div>
            </el-popover>
          </div>
        </template>

        <el-radio-group v-model="formData.leadership_group_type" class="vertical-radio-group">
          <el-radio label="standard">已设置规范管理小组</el-radio>
          <el-radio label="basic">已设置基础管理小组</el-radio>
          <el-radio label="none">未设置相关小组</el-radio>
        </el-radio-group>
      </el-form-item>
        <el-form-item prop="meeting_activity_count">
          <template #label>
            <div class="label-with-hint">
              <span>2023年到2025年，上述数据小组围绕学校数据收集、分析、应用等方面开展会议或研讨的次数？</span>
              <el-popover placement="top-start" :width="300" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写说明</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">数据工作会议或研讨：包括但不限于数据存储与管理规范化、智慧校园数据体系建设规划、学籍数据质量自查、跨部门数据协同与应用、设备台账与信息化资产登记规范化等会议或研讨。</p>
                </div>
              </el-popover>
            </div>
          </template>
          <el-input-number v-model="formData.meeting_activity_count" :min="0" :controls="false" />
          <span class="unit">次</span>
        </el-form-item>
        <!-- 2. 数据人员配备 -->
        <div class="section-title">2. 数据人员配备</div>
        
        <el-form-item prop="has_data_staff">
        <template #label>
          <div class="label-with-hint">
            <span>学校是否安排专人或兼职人员，负责校内数据工作？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.has_data_staff">
          <el-radio :label="true">已配备</el-radio>
          <el-radio :label="false">未配备</el-radio>
        </el-radio-group>
      </el-form-item>
      <div class="form-tip">
           说明：①<strong>专职人员</strong>：如首席信息官、首席数据官、信息中心负责人等，专门负责数据管理工作；②<strong>兼职人员</strong>：如信息技术教师、教务管理人员等，兼任数据管理相关工作；③<strong>数据工作</strong>：包括但不限于数据收集、存储、整理，数据分析（如成绩分析、学情分析），数据安全与隐私保护，系统平台运维与技术保障，教学资源整理与数据赋能等。
          </div>
        <template v-if="formData.has_data_staff">
          <el-form-item label="学校数据专职/兼职管理人员数量？">
            <div class="inline-inputs">
              <span>专职成员</span>
              <el-input-number v-model="formData.fulltime_staff_count" :min="0" :controls="false" />
              <span>人</span>
              <span style="margin-left: 30px">兼职成员</span>
              <el-input-number v-model="formData.parttime_staff_count" :min="0" :controls="false" />
              <span>人</span>
            </div>
          </el-form-item>

          <el-form-item label="学校专职兼职数据管理人员是否有明确的职务职责？" prop="has_clear_responsibilities">
            <el-radio-group v-model="formData.has_clear_responsibilities">
              <el-radio :label="true">已明确</el-radio>
              <el-radio :label="false">未明确</el-radio>
            </el-radio-group>
          </el-form-item>
        </template>
                  
        <el-form-item prop="has_training">
        <template #label>
          <div class="label-with-hint">
            <span>2023年至2025年，学校数据专职或兼职人员是否参加过数据管理、数据分析、数据安全、数据应用等方面的培训或进修？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.has_training">
          <el-radio :label="true">有参与</el-radio>
          <el-radio :label="false">未参与</el-radio>
        </el-radio-group>
      </el-form-item>

        <template v-if="formData.has_training">
          <el-form-item label="2023年至2025年，学校数据专职或兼职人员进修或培训的次数？" prop="training_count">
            <el-input-number v-model="formData.training_count" :min="0" :controls="false" />
            <span class="unit">次</span>
          </el-form-item>

          <el-form-item label="2023年至2025年，相关人员获得的数据相关培训或进修证书数量？">
            <div class="inline-inputs">
              <span>国家级</span>
              <el-input-number v-model="formData.national_cert_count" :min="0" :controls="false" />
              <span>个</span>
              <span style="margin-left: 30px">省级</span>
              <el-input-number v-model="formData.provincial_cert_count" :min="0" :controls="false" />
              <span>个</span>
              <span style="margin-left: 30px">市级及以下</span>
              <el-input-number v-model="formData.city_cert_count" :min="0" :controls="false" />
              <span>个</span>
            </div>
          </el-form-item>
          <div class="form-tip">
            说明：①<strong>国家级认证或考核证书</strong>：国家部委/全国性行业统考认证，如BDA数据分析师、CDA数据分析师（Ⅰ/Ⅱ/Ⅲ级）、DCMM个人数据管理师、全国中小学教师数据素养能力等级证书（由国家级教培平台、全国教师发展机构统一颁发）；②<strong>省级认证或考核证书</strong>：省教育厅、省人社厅、省大数据局等省级行政机关发证或备案认定，如省级教师信息技术/数据素养专项培训证书。③<strong>市级及以下认证或考核证书</strong>：市教育局、市人社局、市大数据局等市级行政机关发证，如市级数据安全、校园数据合规培训证书、高校MOOC结业证书。
          </div>
        </template>

        <!-- 3. 数据管理文件 -->
        <div class="section-title">3. 数据管理文件</div>
        
        <el-form-item prop="management_doc_status">
        <template #label>
          <div class="label-with-hint">
            <span>学校是否在相关管理制度或规范文件中，对数据（如师生信息）的采集、使用、存储与共享等环节作出明确规定？</span>
            <el-popover placement="top-start" :width="460" trigger="hover" popper-class="custom-hint-popper">
            </el-popover>
          </div>
        </template>

        <el-radio-group v-model="formData.management_doc_status" class="vertical-radio-group">
          <el-radio label="clear_required">已在相关制度或规范文件中作出明确要求</el-radio>
          <el-radio label="follow_policy">未作明确要求，但遵循国家或区域相关文件执行</el-radio>
          <el-radio label="self_awareness">未作明确要求，主要依靠师生自主意识</el-radio>
        </el-radio-group>
      </el-form-item>

      <template v-if="formData.management_doc_status === 'clear_required'">
        <el-form-item label="学校出台的与数据管理相关文件的份数（如管理、办法、细则）？">
          <div class="inline-inputs">
            <el-input-number v-model="formData.management_doc_count" :min="0" :controls="false" />
            <span>份</span>
          </div>
        </el-form-item>

        <el-form-item label="上传数据管理相关文件：">
          <div class="upload-section">
            <el-upload
              v-if="!isReadonly"
              :action="uploadUrl"
              :headers="uploadHeaders"
              :data="{ file_type: 'management' }"
              :on-success="handleManagementUploadSuccess"
              :on-error="handleUploadError"
              :on-remove="handleManagementFileRemove"
              :file-list="managementFileList"
              :before-upload="beforeUpload"
            >
              <el-button type="primary">点击上传</el-button>
            </el-upload>
            <div v-else class="readonly-file-list">
              <div v-for="file in managementFileList" :key="file.uid" class="file-item">
                <el-link :href="file.url" target="_blank">{{ file.name }}</el-link>
              </div>
              <span v-if="!managementFileList.length" class="no-file">暂无文件</span>
            </div>
            <div class="upload-tip" v-if="!isReadonly">支持上传PDF、Word、图片等格式，单个文件不超过10MB</div>
          </div>
        </el-form-item>
      </template>

        <el-form-item prop="practice_doc_status">
  <template #label>
    <div class="label-with-hint">
      <span>学校是否发布指导师生使用数据的相关指南、操作说明或工作手册（如一体机使用手册，利用平台分析学情、优化教学等的指南）？</span>
      <el-popover placement="top-start" :width="460" trigger="hover" popper-class="custom-hint-popper">
        
      </el-popover>
    </div>
  </template>

  <el-radio-group v-model="formData.practice_doc_status" class="vertical-radio-group">
    <el-radio label="published">已发布指南、操作说明或工作手册</el-radio>
    <el-radio label="internal_training">未发布，但有内部培训进行指导</el-radio>
    <el-radio label="self_practice">未发布，主要依靠师生自主实践</el-radio>
  </el-radio-group>
</el-form-item>

<template v-if="formData.practice_doc_status === 'published'">
  <el-form-item label="学校出台的与数据实践指导相关文件的份数（如规范、标准、指南）？">
    <div class="inline-inputs">
      <el-input-number v-model="formData.practice_doc_count" :min="0" :controls="false" />
      <span>份</span>
    </div>
  </el-form-item>

  <el-form-item label="上传数据实践指导相关文件：">
    <div class="upload-section">
      <el-upload
        v-if="!isReadonly"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :data="{ file_type: 'practice' }"
        :on-success="handlePracticeUploadSuccess"
        :on-error="handleUploadError"
        :on-remove="handlePracticeFileRemove"
        :file-list="practiceFileList"
        :before-upload="beforeUpload"
      >
        <el-button type="primary">点击上传</el-button>
      </el-upload>
      <div v-else class="readonly-file-list">
        <div v-for="file in practiceFileList" :key="file.uid" class="file-item">
          <el-link :href="file.url" target="_blank">{{ file.name }}</el-link>
        </div>
        <span v-if="!practiceFileList.length" class="no-file">暂无文件</span>
      </div>
      <div class="upload-tip" v-if="!isReadonly">支持上传PDF、Word、图片等格式，单个文件不超过10MB</div>
    </div>
  </el-form-item>
</template>
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
  // B11 新版字段
  leadership_group_type: '',

  // 旧字段先保留，避免旧数据报错
  has_leadership_group: null,

  meeting_activity_count: null,

  has_data_staff: null,
  fulltime_staff_count: null,
  parttime_staff_count: null,
  has_clear_responsibilities: null,

  has_training: null,
  training_count: null,
  national_cert_count: null,
  provincial_cert_count: null,
  city_cert_count: null,

  // B31 新版字段
  management_doc_status: '',

  // 旧字段先保留
  has_management_doc: null,
  management_doc_count: null,
  management_doc_files: [],

  // B32 新版字段
  practice_doc_status: '',

  // 旧字段先保留
  has_practice_doc: null,
  practice_doc_count: null,
  practice_doc_files: []
})

// 表单验证规则
const formRules = {
  has_clear_responsibilities: [
    { required: true, message: '请选择是否有明确职务职责', trigger: 'change' }
  ]
}

// 文件列表
const managementFileList = computed(() => {
  return (formData.value.management_doc_files || []).map((file, index) => ({
    name: file.name,
    url: file.url,
    uid: file.path || index,  // 使用path作为唯一标识
    path: file.path  // 保存path用于删除
  }))
})

const practiceFileList = computed(() => {
  return (formData.value.practice_doc_files || []).map((file, index) => ({
    name: file.name,
    url: file.url,
    uid: file.path || index,
    path: file.path
  }))
})

// 上传配置
const uploadUrl = computed(() => {
  return `/api/assessments/${assessmentId.value}/institution/upload/`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('access_token')
  return {
    'Authorization': `Bearer ${token}`
  }
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

    // 获取数据制度数据
    const response = await fetch(`/api/assessments/${assessmentId.value}/institution/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('数据制度信息加载失败')
    }

    const data = await response.json()
    Object.assign(formData.value, data)

    // 兼容旧数据，避免新字段为空时影响表单显示
    if (!formData.value.leadership_group_type) {
      formData.value.leadership_group_type = ''
    }

    if (!formData.value.management_doc_status) {
      formData.value.management_doc_status = ''
    }

    if (!formData.value.practice_doc_status) {
      formData.value.practice_doc_status = ''
    }

    if (!Array.isArray(formData.value.management_doc_files)) {
      formData.value.management_doc_files = []
    }

    if (!Array.isArray(formData.value.practice_doc_files)) {
      formData.value.practice_doc_files = []
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
  if (!formRef.value) return

  saving.value = true

  try {
    await formRef.value.validate()

    const response = await fetch(`/api/assessments/${assessmentId.value}/save_institution/`, {
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

    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 文件上传
const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB')
  }
  return isLt10M
}

const handleManagementUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
  formData.value.management_doc_files = formData.value.management_doc_files || []
  formData.value.management_doc_files.push(response.file)
}

const handlePracticeUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
  formData.value.practice_doc_files = formData.value.practice_doc_files || []
  formData.value.practice_doc_files.push(response.file)
}

const handleUploadError = (error) => {
  console.error('上传失败:', error)
  ElMessage.error('文件上传失败')
}

// 删除管理制度文件
const handleManagementFileRemove = async (file) => {
  try {
    const filePath = file.path || file.response?.file?.path
    if (!filePath) {
      ElMessage.error('无法获取文件路径')
      return
    }

    // 调用后端删除接口
    const response = await fetch(`/api/assessments/${assessmentId.value}/institution/delete-file/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        file_type: 'management',
        file_path: filePath
      })
    })

    if (response.ok) {
      // 从本地数据中删除
      formData.value.management_doc_files = formData.value.management_doc_files.filter(
        f => f.path !== filePath
      )
      ElMessage.success('文件删除成功')
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    console.error('删除文件失败:', error)
    ElMessage.error('文件删除失败')
  }
}

// 删除实践指导文件
const handlePracticeFileRemove = async (file) => {
  try {
    const filePath = file.path || file.response?.file?.path
    if (!filePath) {
      ElMessage.error('无法获取文件路径')
      return
    }

    // 调用后端删除接口
    const response = await fetch(`/api/assessments/${assessmentId.value}/institution/delete-file/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        file_type: 'practice',
        file_path: filePath
      })
    })

    if (response.ok) {
      // 从本地数据中删除
      formData.value.practice_doc_files = formData.value.practice_doc_files.filter(
        f => f.path !== filePath
      )
      ElMessage.success('文件删除成功')
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    console.error('删除文件失败:', error)
    ElMessage.error('文件删除失败')
  }
}

// 返回评估列表
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
.data-institution-container {
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

.institution-form {
  margin-top: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin: 30px 0 20px 0;
  padding-left: 0;   /* 去掉左侧内边距，让文字对齐左侧 */
  border-left: none; /* 去掉蓝色竖线 */
}

.inline-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-count-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px 30px;
}

.upload-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.unit {
  margin-left: 10px;
  color: #606266;
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

:deep(.el-upload__tip) {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

:deep(.el-input-number) {
  width: 120px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: center;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 30px;
}

:deep(.el-radio) {
  margin-right: 0;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-list) {
  margin-top: 10px;
}

.readonly-file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.readonly-file-list .file-item {
  padding: 5px 0;
}

.readonly-file-list .no-file {
  color: #909399;
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
  font-size: 14px;
  line-height: 1.8;
  color: #e6a23c;
  box-sizing: border-box;
}

:deep(.el-form-item__content) {
  flex-wrap: wrap;
  align-items: flex-start;
}
</style>
