<template>
  <div class="school-type-report-page">
    <div class="page-heading"><h2>学校类型评估报告</h2><p>选择区域与学校类型，查看同区域同类型学校的评估结果。</p></div>
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" @submit.prevent="loadReport">
        <el-form-item label="所属区域">
          <el-select v-model="regionKey" filterable placeholder="请选择区域（可搜索）" :loading="optionsLoading" :disabled="exporting" style="width: 330px" @change="clearReport">
            <el-option v-for="region in regions" :key="region.key" :value="region.key" :label="region.label" />
          </el-select>
        </el-form-item>
        <el-form-item label="学校类型">
          <el-select v-model="schoolType" placeholder="请选择学校类型" :disabled="exporting" style="width: 160px" @change="clearReport">
            <el-option v-for="type in schoolTypes" :key="type.value" :value="type.value" :label="type.label" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" native-type="submit" :loading="loading" :disabled="!regionKey || !schoolType || exporting">查看报告</el-button></el-form-item>
        <el-form-item><el-button @click="exportPDF" :loading="exporting" :disabled="!report || loading">导出 PDF</el-button></el-form-item>
      </el-form>
      <el-alert v-if="optionsError" :title="optionsError" type="error" :closable="false"><el-button link type="primary" @click="loadOptions">重新加载选项</el-button></el-alert>
    </el-card>
    <div v-if="loading" class="state-panel" role="status" aria-live="polite">加载中，请稍等...</div>
    <el-alert v-else-if="error" :title="error" type="error" show-icon :closable="false" />
    <div v-else-if="report" ref="reportRef" class="report-shell"><SchoolTypeReportContent :report="report" /></div>
    <el-empty v-else description="请选择区域和学校类型，然后点击“查看报告”" />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import SchoolTypeReportContent from '@/components/SchoolTypeReportContent.vue'

const regions = ref([])
const schoolTypes = ref([])
const regionKey = ref('')
const schoolType = ref('')
const optionsLoading = ref(false)
const optionsError = ref('')
const loading = ref(false)
const exporting = ref(false)
const report = ref(null)
const reportRef = ref(null)
const error = ref('')
let requestVersion = 0

function clearReport() {
  requestVersion++
  loading.value = false
  report.value = null
  error.value = ''
}

async function loadOptions() {
  optionsLoading.value = true
  optionsError.value = ''
  try {
    const response = await request.get('/admin/school-type-report/options/')
    regions.value = response.data.regions.map(region => ({ ...region,
      key: region.id ? `id:${region.id}` : JSON.stringify([region.province, region.city, region.name]),
      label: [region.province, region.city, region.name].join(' / '),
    }))
    schoolTypes.value = response.data.school_types
  } catch {
    optionsError.value = '区域和学校类型加载失败，请重试。'
  } finally {
    optionsLoading.value = false
  }
}

async function loadReport() {
  const region = regions.value.find(item => item.key === regionKey.value)
  if (!region || !schoolType.value || exporting.value) return
  const version = ++requestVersion
  loading.value = true
  error.value = ''
  report.value = null
  const params = { school_type: schoolType.value, ...(region.id ? { region_id: region.id } : {
    province: region.province, city: region.city, district: region.name,
  }) }
  try {
    const response = await request.get('/admin/school-type-report/statistics/', { params, timeout: 120000 })
    if (version === requestVersion) report.value = response.data
  } catch {
    if (version === requestVersion) error.value = '报告加载失败，请检查网络后点击“查看报告”重试。'
  } finally {
    if (version === requestVersion) loading.value = false
  }
}

async function exportPDF() {
  if (!reportRef.value || !report.value || loading.value) return
  exporting.value = true
  try {
    const [{ default: html2canvas }, { jsPDF }] = await Promise.all([import('html2canvas'), import('jspdf')])
    await nextTick()
    await document.fonts.ready
    const canvas = await html2canvas(reportRef.value, {
      scale: 2, backgroundColor: '#ffffff', useCORS: true, logging: false,
      windowWidth: 1440,
      onclone: clonedDocument => {
        const shell = clonedDocument.querySelector('.school-type-report-page .report-shell')
        if (shell) { shell.style.width = '1120px'; shell.style.maxWidth = 'none' }
      },
    })
    // Match the regional report: full-width, continuous report PDF.
    const width = 210
    const height = canvas.height * width / canvas.width
    const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: [width, height] })
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, width, height)
    const scope = report.value
    const name = `${scope.region.province}${scope.region.city}${scope.region.name}_${scope.school_type_label}_学校类型评估报告`
    pdf.save(`${name.replace(/[\\/:*?"<>|]/g, '_')}.pdf`)
    ElMessage.success('报告已导出')
  } catch (err) {
    console.error('学校类型报告导出失败', err)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}

onMounted(loadOptions)
onBeforeUnmount(() => { requestVersion++ })
</script>

<style scoped>
.school-type-report-page { max-width: 1200px; margin: 0 auto; }
.page-heading h2 { color: #23456d; font-size: 24px; margin: 0 0 8px; }
.page-heading p { color: #7b8999; font-size: 14px; margin: 0 0 20px; }
.filter-card { margin-bottom: 24px; border-radius: 8px; }
.filter-card :deep(.el-form-item) { margin-bottom: 10px; margin-top: 10px; }
.report-shell { background: #fff; max-width: 1120px; margin: 0 auto; box-shadow: 0 3px 18px #2139570a; }
.state-panel { padding: 80px 24px; text-align: center; background: white; color: #7b8999; border-radius: 8px; }
</style>
