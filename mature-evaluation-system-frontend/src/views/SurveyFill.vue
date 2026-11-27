<template>
  <div class="survey-fill-container">
    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>加载问卷中...</p>
    </div>

    <!-- 2. 提交成功状态 (新增：提交后直接展示这个，替换掉表单) -->
    <div v-else-if="submitted" class="success-container">
      <el-result
        icon="success"
        title="问卷提交成功"
        sub-title="感谢您的参与！您的回答已安全提交，您可以放心关闭此页面。"
      >
        <template #extra>
          <div class="success-footer">
            <el-icon :size="50" color="#67c23a"><CircleCheck /></el-icon>
            <p>感谢您的支持！</p>
          </div>
        </template>
      </el-result>
    </div>

    <!-- 问卷内容 -->
    <div v-else-if="survey" class="survey-content">
      <div class="survey-header">
        <h1 class="survey-title">{{ survey.title }}</h1>
        <div class="survey-description" v-html="formatDescription(survey.description)"></div>
      </div>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        class="survey-form"
      >
        <div
          v-for="(question, index) in survey.questions"
          :key="question.id"
          class="question-item"
        >
          <div class="question-header">
            <span class="question-number">{{ index + 1 }}.</span>
            <span class="question-text">{{ question.question_text }}</span>
            <el-tag v-if="question.is_required" type="danger" size="small">必填</el-tag>
          </div>

          <!-- 单选题 -->
          <el-form-item
            v-if="question.question_type === 'single_choice'"
            :prop="`q${question.order}`"
            class="question-content"
          >
            <el-radio-group v-model="formData[`q${question.order}`]">
              <el-radio
                v-for="(option, optIndex) in question.options"
                :key="optIndex"
                :label="option"
                class="radio-option"
              >
                {{ option }}
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 多选题 -->
          <el-form-item
            v-else-if="question.question_type === 'multiple_choice'"
            :prop="`q${question.order}`"
            class="question-content"
          >
            <el-checkbox-group v-model="formData[`q${question.order}`]">
              <el-checkbox
                v-for="(option, optIndex) in question.options"
                :key="optIndex"
                :label="option"
                class="checkbox-option"
              >
                {{ option }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <!-- 量表题 -->
          <el-form-item
            v-else-if="question.question_type === 'scale'"
            :prop="`q${question.order}`"
            class="question-content"
          >
            <el-radio-group v-model="formData[`q${question.order}`]" class="scale-group">
              <el-radio
                v-for="(option, optIndex) in question.options"
                :key="optIndex"
                :label="option"
                class="scale-option"
              >
                {{ option }}
              </el-radio>
            </el-radio-group>
          </el-form-item>
        </div>

        <!-- 提交按钮 -->
        <div class="submit-section">
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            :disabled="submitting"
            @click="handleSubmit"
          >
            {{ submitting ? '提交中...' : '提交问卷' }}
          </el-button>
        </div>
      </el-form>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <el-result
        icon="error"
        :title="error"
        sub-title="请检查问卷链接是否正确或联系管理员"
      >
        <template #extra>
          <el-button type="primary" @click="reload">重新加载</el-button>
        </template>
      </el-result>
    </div>

    <!-- 提交成功 -->
    <el-dialog
      v-model="successDialogVisible"
      title="提交成功"
      width="400px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      center
    >
      <div class="success-content">
        <el-icon class="success-icon" :size="60" color="#67c23a">
          <CircleCheck />
        </el-icon>
        <p class="success-text">感谢您的参与！</p>
        <p class="success-subtext">您的问卷已成功提交</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="closeSuccess">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, CircleCheck } from '@element-plus/icons-vue'
import { getSurveyByUUID, submitSurvey } from '@/api/survey'

const route = useRoute()
const uuid = computed(() => route.params.uuid)

const loading = ref(true)
const error = ref('')
const survey = ref(null)
const formRef = ref(null)
const formData = reactive({})
const formRules = reactive({})
const submitting = ref(false)
const submitted = ref(false)
const successDialogVisible = ref(false)
let attempt
const storageKey = computed(() => 'survey-attempt:' + uuid.value)

// 加载问卷
const loadSurvey = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const data = await getSurveyByUUID(uuid.value)
    survey.value = data
    
    // 初始化表单数据和验证规则
    data.questions.forEach(question => {
      const fieldName = `q${question.order}`
      
      // 初始化表单数据
      if (question.question_type === 'multiple_choice') {
        formData[fieldName] = []
      } else {
        formData[fieldName] = ''
      }
      
      // 设置验证规则
      if (question.is_required) {
        formRules[fieldName] = [
          {
            required: true,
            message: '此题为必填项',
            trigger: 'change'
          }
        ]
      }
    })
  } catch (err) {
    console.error('加载问卷失败:', err)
    error.value = err.response?.data?.error || '加载问卷失败'
  } finally {
    loading.value = false
  }
  if (survey.value?.attempt) {
    await nextTick()
    const questions = JSON.stringify(survey.value.questions)
    let saved
    try { saved = JSON.parse(sessionStorage.getItem(storageKey.value)) } catch { /* Storage may be unavailable. */ }
    attempt = saved?.questions === questions && saved.token && Number.isFinite(saved.start)
      ? saved : { token: survey.value.attempt, start: Date.now(), questions }
    try { sessionStorage.setItem(storageKey.value, JSON.stringify(attempt)) } catch { /* Keep timing in memory. */ }
  }
}

// 格式化描述文本
const formatDescription = (text) => {
  return text.replace(/\n/g, '<br>')
}

// 提交问卷
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    // 验证表单
    await formRef.value.validate()
    
    submitting.value = true
    
    // 提交答案
    const timing = attempt ? { attempt: attempt.token, elapsed_ms: Math.max(0, Date.now() - attempt.start) } : {}
    await submitSurvey(uuid.value, formData, timing)
    try { sessionStorage.removeItem(storageKey.value) } catch { /* Storage may be unavailable. */ }
    
    submitted.value = true 
    // 显示成功对话框
    successDialogVisible.value = true
  } catch (err) {
    if (err !== false) {  // 不是验证错误
      console.error('提交问卷失败:', err)
      ElMessage.error(err.response?.data?.error || '提交问卷失败')
    }
  } finally {
    submitting.value = false
  }
}

// 重新加载
const reload = () => {
  loadSurvey()
}

// 关闭成功对话框
const closeSuccess = () => {
  successDialogVisible.value = false
  // 可以选择关闭窗口或跳转到其他页面
  window.close()
}

onMounted(() => {
  loadSurvey()
})
</script>

<style scoped>
.survey-fill-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.loading-container,
.error-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
}

.loading-container p {
  margin-top: 20px;
  font-size: 16px;
  color: #606266;
}

.survey-content {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.survey-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  text-align: center;
}

.survey-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 20px 0;
  line-height: 1.4;
}

.survey-description {
  font-size: 15px;
  line-height: 1.8;
  opacity: 0.95;
  max-width: 700px;
  margin: 0 auto;
  text-align: left;
}

.survey-description :deep(p) {
  text-indent: 2em;
  margin: 0.5em 0;
}

.survey-form {
  padding: 40px;
}

.question-item {
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 1px solid #ebeef5;
}

.question-item:last-of-type {
  border-bottom: none;
}

.question-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 20px;
}

.question-number {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  flex-shrink: 0;
}

.question-text {
  flex: 1;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  line-height: 1.6;
}

.question-content {
  margin-left: 24px;
}

.radio-option,
.checkbox-option {
  display: block;
  margin-bottom: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
  transition: all 0.3s;
}

.radio-option:hover,
.checkbox-option:hover {
  background: #ecf5ff;
}

.scale-group {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.scale-option {
  padding: 12px 8px;
  background: #f5f7fa;
  border-radius: 6px;
  text-align: center;
  transition: all 0.3s;
  white-space: nowrap;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .scale-group {
    grid-template-columns: 1fr;
  }
  
  .scale-option {
    font-size: 14px;
  }
}

.scale-option:hover {
  background: #ecf5ff;
}

.submit-section {
  margin-top: 40px;
  text-align: center;
  padding-top: 30px;
  border-top: 2px solid #ebeef5;
}

.submit-section .el-button {
  min-width: 200px;
  height: 48px;
  font-size: 16px;
}

.success-content {
  text-align: center;
  padding: 20px;
}

.success-icon {
  margin-bottom: 20px;
}

.success-text {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
}

.success-subtext {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 新增：提交成功结果页的样式 */
.success-container {
  max-width: 800px;
  margin: 40px auto;
  background: white;
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.success-footer {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #67c23a;
  font-weight: bold;
}

/* 优化提交按钮动画 */
.submit-section .el-button.is-loading {
  opacity: 0.8;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .survey-fill-container {
    padding: 20px 10px;
  }

  .survey-header {
    padding: 30px 20px;
  }

  .survey-title {
    font-size: 22px;
  }

  .survey-form {
    padding: 30px 20px;
  }

  .scale-group {
    flex-direction: column;
  }

  .scale-option {
    min-width: 100%;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-radio__label),
:deep(.el-checkbox__label) {
  white-space: normal;
  line-height: 1.6;
}

:deep(.el-form-item__error) {
  margin-left: 24px;
}
</style>
