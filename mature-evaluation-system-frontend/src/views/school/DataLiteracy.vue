<template>
<el-col :span="8">
  <el-card shadow="hover" class="survey-card">
    <div class="survey-icon teacher">
      <el-icon :size="40"><User /></el-icon>
    </div>
    <h3>教师问卷</h3>
    <p class="survey-desc">评价教师数据素养及数据应用效果</p>
    
    <div v-if="teacherInstance" class="survey-info">
      <el-divider />
      <div class="info-item">
        <span>已收集：</span>
        <el-tag size="small" type="success">{{ teacherInstance.collected_count }}</el-tag>
      </div>
      <div class="info-item">
        <span>截止日期：</span>
        <el-tag size="small" type="warning">{{ formatExpiredTime(teacherInstance.expired_at) }}</el-tag>
      </div>
      
      <el-divider />
      
      <div class="share-area">
        <div class="share-left">
          <el-input v-model="teacherShareUrl" readonly size="small">
            <template #append>
              <el-button @click="copyLink(teacherShareUrl)">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
            </template>
          </el-input>
        </div>
        <div class="share-right">
          <div v-if="teacherQrUrl" class="qr-box">
            <img :src="teacherQrUrl" alt="二维码" class="qr-img" />
          </div>
          <div v-else class="qr-placeholder">二维码生成中...</div>
        </div>
      </div>
    </div>
    
    <div v-else class="no-instance">
      <el-button type="primary" @click="createInstance('teacher')" :loading="creating">
        生成分享链接
      </el-button>
    </div>
  </el-card>
</el-col>

<!-- 学生问卷区域 -->
<el-col :span="8">
  <el-card shadow="hover" class="survey-card">
    <div class="survey-icon student">
      <el-icon :size="40"><Reading /></el-icon>
    </div>
    <h3>学生问卷</h3>
    <p class="survey-desc">评价学生数据素养及数据应用效果</p>
    
    <div v-if="studentInstance" class="survey-info">
      <el-divider />
      <div class="info-item">
        <span>已收集：</span>
        <el-tag size="small" type="success">{{ studentInstance.collected_count }}</el-tag>
      </div>
      <div class="info-item">
        <span>截止日期：</span>
        <el-tag size="small" type="warning">{{ formatExpiredTime(studentInstance.expired_at) }}</el-tag>
      </div>
      
      <el-divider />
      
      <div class="share-area">
        <div class="share-left">
          <el-input v-model="studentShareUrl" readonly size="small">
            <template #append>
              <el-button @click="copyLink(studentShareUrl)">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
            </template>
          </el-input>
        </div>
        <div class="share-right">
          <div v-if="studentQrUrl" class="qr-box">
            <img :src="studentQrUrl" alt="二维码" class="qr-img" />
          </div>
          <div v-else class="qr-placeholder">二维码生成中...</div>
        </div>
      </div>
    </div>
    
    <div v-else class="no-instance">
      <el-button type="primary" @click="createInstance('student')" :loading="creating">
        生成分享链接
      </el-button>
    </div>
  </el-card>
</el-col>

<!-- 管理者问卷区域 -->
<el-col :span="8">
  <el-card shadow="hover" class="survey-card">
    <div class="survey-icon manager">
      <el-icon :size="40"><Management /></el-icon>
    </div>
    <h3>管理者问卷</h3>
    <p class="survey-desc">评价管理者数据素养及数据资产意识</p>
    
    <div v-if="managerInstance" class="survey-info">
      <el-divider />
      <div class="info-item">
        <span>已收集：</span>
        <el-tag size="small" type="success">{{ managerInstance.collected_count }}</el-tag>
      </div>
      <div class="info-item">
        <span>截止日期：</span>
        <el-tag size="small" type="warning">{{ formatExpiredTime(managerInstance.expired_at) }}</el-tag>
      </div>
      
      <el-divider />
      
      <div class="share-area">
        <div class="share-left">
          <el-input v-model="managerShareUrl" readonly size="small">
            <template #append>
              <el-button @click="copyLink(managerShareUrl)">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
            </template>
          </el-input>
        </div>
        <div class="share-right">
          <div v-if="managerQrUrl" class="qr-box">
            <img :src="managerQrUrl" alt="二维码" class="qr-img" />
          </div>
          <div v-else class="qr-placeholder">二维码生成中...</div>
        </div>
      </div>
    </div>
    
    <div v-else class="no-instance">
      <el-button type="primary" @click="createInstance('manager')" :loading="creating">
        生成分享链接
      </el-button>
    </div>
  </el-card>
</el-col>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Reading, Management, CopyDocument } from '@element-plus/icons-vue'
import { getAssessmentSurveys, createSurveyInstance } from '@/api/survey'
import { getAssessments, createAssessment } from '@/api/assessment'
import QRCode from 'qrcode'


const route = useRoute()
const assessmentId = ref(null)
const loading = ref(true)
const creating = ref(false)

// 问卷实例数据
const teacherInstance = ref(null)
const studentInstance = ref(null)
const managerInstance = ref(null)

// 二维码 URL 状态
const teacherQrUrl = ref('')
const studentQrUrl = ref('')
const managerQrUrl = ref('')

// 统一二维码生成函数
const generateQr = async (url, title) => {
  if (!url) return ''
  try {
    // 1. 获取高质量原始二维码 (800px)
    const rawQrDataUrl = await QRCode.toDataURL(url, {
      width: 800,
      margin: 2,
      color: { dark: '#000000', light: '#ffffff' }
    })

    return new Promise((resolve) => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      
      // 设置画布大小 (宽 800, 高 1050，预留底部空间)
      const w = 800
      const h = 1050
      canvas.width = w
      canvas.height = h

      const img = new Image()
      img.src = rawQrDataUrl
      img.onload = () => {
        // --- 1. 绘制背景 ---
        ctx.fillStyle = '#FFFFFF'
        ctx.fillRect(0, 0, w, h)

        // --- 2. 绘制二维码 ---
        ctx.drawImage(img, 0, 0, w, w)

        // --- 3. 绘制中心学校名白块 (增强视觉) ---
        const boxSize = w * 0.25
        const bx = (w - boxSize) / 2
        const by = (w - boxSize) / 2
        
        ctx.fillStyle = '#FFFFFF'
        ctx.shadowColor = 'rgba(0,0,0,0.1)'
        ctx.shadowBlur = 10
        ctx.fillRect(bx, by, boxSize, boxSize)
        ctx.shadowBlur = 0 // 重置阴影

        // 绘制学校文字
        ctx.fillStyle = '#333333'
        const fontSize = Math.floor(boxSize * 0.2)
        ctx.font = `bold ${fontSize}px "Microsoft YaHei", sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        const nameLines = splitTextIntoLines(ctx, schoolName.value || '评估系统', boxSize * 0.85)
        const lineHeight = fontSize * 1.3
        const startY = (w / 2) - ((nameLines.length - 1) * lineHeight) / 2
        nameLines.forEach((line, i) => {
          ctx.fillText(line, w / 2, startY + i * lineHeight)
        })

        // --- 4. 绘制底部文字区域 (关键修改) ---
        // 绘制一条浅色分割线
        ctx.strokeStyle = '#f0f0f0'
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(50, w)
        ctx.lineTo(w - 50, w)
        ctx.stroke()

        // 绘制问卷标题
        ctx.fillStyle = '#303133'
        ctx.font = `bold 32px "Microsoft YaHei", sans-serif`
        ctx.textAlign = 'center'
        // 自动换行处理标题
        const titleLines = splitTextIntoLines(ctx, `《${title}》`, w - 100)
        titleLines.forEach((line, i) => {
          ctx.fillText(line, w / 2, w + 60 + i * 45)
        })

        // 绘制红色提醒字
        ctx.fillStyle = '#f56c6c' // Element UI 的红色
        ctx.font = `bold 28px "Microsoft YaHei", sans-serif`
        ctx.fillText('请在48小时内完成问卷填写！', w / 2, h - 60)

        resolve(canvas.toDataURL('image/png', 1.0))
      }
    })
  } catch (e) {
    return ''
  }
}

const isAssessmentExpired = (assessmentData) => {
  if (assessmentData?.check_survey_quality) return false
  if (!assessmentData?.created_at) return false

  const startTime = new Date(assessmentData.created_at).getTime()
  const expireTime = startTime + 120 * 60 * 60 * 1000

  return Date.now() > expireTime
}

// 辅助函数：文字换行
const splitTextIntoLines = (ctx, text, maxWidth) => {
  const words = text.split('')
  let line = ''
  const lines = []
  for (let n = 0; n < words.length; n++) {
    let testLine = line + words[n]
    if (ctx.measureText(testLine).width > maxWidth && n > 0) {
      lines.push(line)
      line = words[n]
    } else {
      line = testLine
    }
  }
  lines.push(line)
  return lines
}

// 监听分享链接变化，自动生成二维码
watch(teacherShareUrl, async (url) => {
  teacherQrUrl.value = await generateQr(url,"教师数据素养及数据应用效果调查问卷")
})

watch(studentShareUrl, async (url) => {
  studentQrUrl.value = await generateQr(url,"学生数据素养及数据应用效果调查问卷")
})

watch(managerShareUrl, async (url) => {
  managerQrUrl.value = await generateQr(url,"管理者数据素养及数据应用效果调查问卷")
})

// 分享链接
const teacherShareUrl = computed(() => {
  if (!teacherInstance.value) return ''
  return `${window.location.origin}${teacherInstance.value.share_url}`
})

const studentShareUrl = computed(() => {
  if (!studentInstance.value) return ''
  return `${window.location.origin}${studentInstance.value.share_url}`
})

const managerShareUrl = computed(() => {
  if (!managerInstance.value) return ''
  return `${window.location.origin}${managerInstance.value.share_url}`
})

// 获取或创建评估记录
const loadOrCreateAssessment = async () => {
  try {
    // 如果URL中有assessmentId，直接使用
    if (route.params.id) {
      assessmentId.value = parseInt(route.params.id)
      console.log('使用URL中的assessmentId:', assessmentId.value)
      return
    }
    
    // 获取评估列表
    console.log('获取评价列表...')
    const response = await getAssessments()
    console.log('评价列表响应:', response)
    
    // 确保response是数组
    const assessments = Array.isArray(response) ? response : (response.results || [])
    console.log('评价数组:', assessments)
    
    // 查找进行中的评估
    const ongoingAssessment = assessments.find(a => 
      ['draft', 'collecting', 'analyzing'].includes(a.status)
    )
    
    if (ongoingAssessment) {
      assessmentId.value = ongoingAssessment.id
      console.log('找到进行中的评价:', ongoingAssessment.id)
    } else {
      // 创建新评估
      console.log('创建新评价...')
      const newAssessment = await createAssessment()
      console.log('新评价创建成功:', newAssessment)
      assessmentId.value = newAssessment.id
      ElMessage.success('已创建新的评价记录')
    }
  } catch (error) {
    console.error('获取或创建评价失败:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error(error.response?.data?.error || '获取或创建评价失败，请刷新页面重试')
    loading.value = false
  }
}

// 加载问卷实例
const loadSurveys = async () => {
  if (!assessmentId.value) {
    console.log('assessmentId为空，跳过加载问卷')
    loading.value = false
    return
  }
  
  try {
    console.log('加载问卷实例，assessmentId:', assessmentId.value)
    const data = await getAssessmentSurveys(assessmentId.value)
    console.log('问卷实例数据:', data)
    
    // 重置实例
    teacherInstance.value = null
    studentInstance.value = null
    managerInstance.value = null
    
    // 分类存储
    if (Array.isArray(data)) {
      data.forEach(instance => {
        console.log('处理问卷实例:', instance.template_info?.survey_type)
        if (instance.template_info?.survey_type === 'teacher') {
          teacherInstance.value = instance
        } else if (instance.template_info?.survey_type === 'student') {
          studentInstance.value = instance
        } else if (instance.template_info?.survey_type === 'manager') {
          managerInstance.value = instance
        }
      })
    }
    
    console.log('问卷实例加载完成')
  } catch (error) {
    console.error('加载问卷实例失败:', error)
    if (error.response?.status !== 404) {
      ElMessage.error('加载问卷实例失败')
    }
  } finally {
    loading.value = false
  }
}

// 创建问卷实例（直接生成，无需输入目标数量）
const createInstance = async (surveyType) => {
  if (!assessmentId.value) {
    ElMessage.error('评价记录未加载，请刷新页面')
    return
  }
  
  creating.value = true
  try {
    console.log('创建问卷实例:', surveyType)
    await createSurveyInstance({
      assessment_id: assessmentId.value,
      survey_type: surveyType,
      target_count: 9999  // 默认值，对计分无影响
    })
    
    ElMessage.success('问卷链接生成成功')
    await loadSurveys()
  } catch (error) {
    console.error('创建问卷实例失败:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error(error.response?.data?.error || '生成链接失败，请重试')
  } finally {
    creating.value = false
  }
}

// 复制链接
const copyLink = async (url) => {
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    // 降级方案：使用传统方法
    const textarea = document.createElement('textarea')
    textarea.value = url
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('链接已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

// 格式化过期时间
const formatExpiredTime = (dateStr) => {
  if (!dateStr) return '无限期'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  })
}

onMounted(async () => {
  console.log('DataLiteracy组件挂载')
  await loadOrCreateAssessment()
  await loadSurveys()
})
</script>

<style scoped>
.data-literacy-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.survey-list {
  margin-top: 20px;
}

.survey-card {
  text-align: center;
  min-height: 380px;
}

.survey-icon {
  width: 80px;
  height: 80px;
  margin: 20px auto;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

/* 分享区域：链接 + 二维码 */
.share-area {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.share-left {
  flex: 1;
}

.share-right {
  width: 128px;
  text-align: center;
}

.share-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}

.qr-box {
  width: 140px;
  height: auto;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}

.qr-img {
  width: 140px;
  height: auto;
  display: block;
}

.qr-placeholder {
  font-size: 12px;
  color: #c0c4cc;
}

.survey-icon.teacher {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.survey-icon.student {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.survey-icon.manager {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.survey-card h3 {
  margin: 10px 0;
  font-size: 20px;
}

.survey-desc {
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.survey-info {
  text-align: left;
  padding: 0 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.info-item span {
  color: #606266;
  font-size: 14px;
}

.share-link {
  margin-bottom: 15px;
}

.no-instance {
  padding: 40px 0;
}
</style>
