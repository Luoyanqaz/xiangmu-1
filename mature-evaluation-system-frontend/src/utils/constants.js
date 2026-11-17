/**
 * 系统常量配置
 */

// 用户角色
export const USER_ROLES = {
  SCHOOL: 'school',
  ADMIN: 'admin'
}

// 评估状态
export const ASSESSMENT_STATUS = {
  DRAFT: 'draft',
  COLLECTING: 'collecting',
  ANALYZING: 'analyzing',
  COMPLETED: 'completed'
}

// 评估状态文本映射
export const ASSESSMENT_STATUS_TEXT = {
  draft: '草稿',
  collecting: '数据收集中',
  analyzing: '分析中',
  completed: '已完成'
}

// 评估状态颜色映射
export const ASSESSMENT_STATUS_COLOR = {
  draft: 'info',
  collecting: 'warning',
  analyzing: 'primary',
  completed: 'success'
}

// 问卷类型
export const SURVEY_TYPES = {
  TEACHER: 'teacher',
  STUDENT: 'student',
  MANAGER: 'manager'
}

// 问卷类型文本映射
export const SURVEY_TYPE_TEXT = {
  teacher: '教师问卷',
  student: '学生问卷',
  manager: '管理者问卷'
}

// 成熟度等级
export const MATURITY_LEVELS = {
  INITIAL: 'initial',
  GROWING: 'growing',
  MATURE: 'mature',
  LEADING: 'leading'
}

// 成熟度等级文本映射
export const MATURITY_LEVEL_TEXT = {
  initial: '初始级',
  growing: '成长级',
  mature: '成熟级',
  leading: '创新级'
}

// 成熟度等级颜色映射
export const MATURITY_LEVEL_COLOR = {
  initial: '#f27b7b',
  growing: '#f0ab4d',
  mature: '#67c98a',
  leading: '#5ca4d9'
}

export const MATURITY_LEVEL_RANGES = {
  initial: '[0.0, 1.5)',
  growing: '[1.5, 3.0)',
  mature: '[3.0, 4.0)',
  leading: '[4.0, 5.0]'
}

export function scoreToMaturityLevel(value) {
  if (value == null || typeof value === 'boolean' || String(value).trim() === '') return ''
  const score = Number(value)
  if (!Number.isFinite(score) || score < 0 || score > 5) return ''
  if (score < 1.5) return 'initial'
  if (score < 3) return 'growing'
  if (score < 4) return 'mature'
  return 'leading'
}

// 评估维度
export const ASSESSMENT_DIMENSIONS = [
  { key: 'literacy', name: '数据素养' },
  { key: 'institution', name: '数据制度' },
  { key: 'behavior', name: '数据行为' },
  { key: 'asset', name: '数据资产' },
  { key: 'technology', name: '数据技术' }
]

// 学校类型
export const SCHOOL_TYPES = [
  { value: 'primary', label: '小学' },
  { value: 'junior', label: '初中' },
  { value: 'senior', label: '高中' },
  { value: 'nine_year', label: '九年一贯制' },
  { value: 'twelve_year', label: '十二年一贯制' }
]

// 数据存储方式
export const STORAGE_TYPES = [
  { value: 'local', label: '本地服务器' },
  { value: 'cloud', label: '云服务' },
  { value: 'hybrid', label: '混合云' }
]

// 申请状态
export const APPLICATION_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected'
}

// 申请状态文本映射
export const APPLICATION_STATUS_TEXT = {
  pending: '待审批',
  approved: '已通过',
  rejected: '已拒绝'
}

// 申请状态颜色映射
export const APPLICATION_STATUS_COLOR = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger'
}
