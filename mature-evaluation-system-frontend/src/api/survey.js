/**
 * 问卷系统API
 */
import request from './request'

/**
 * 获取某个评估的所有问卷实例
 * @param {number} assessmentId - 评估ID
 */
export function getAssessmentSurveys(assessmentId) {
  return request({
    url: `/surveys/assessment/${assessmentId}/`,
    method: 'get'
  })
}

/**
 * 创建问卷实例
 * @param {object} data - 问卷实例数据
 * @param {number} data.assessment_id - 评估ID
 * @param {string} data.survey_type - 问卷类型 (teacher/student/manager)
 * @param {number} data.target_count - 目标收集数量
 */
export function createSurveyInstance(data) {
  return request({
    url: '/surveys/instances/',
    method: 'post',
    data
  })
}

/**
 * 获取问卷实例详情
 * @param {number} instanceId - 问卷实例ID
 */
export function getSurveyInstance(instanceId) {
  return request({
    url: `/surveys/instances/${instanceId}/`,
    method: 'get'
  })
}

/**
 * 更新问卷实例
 * @param {number} instanceId - 问卷实例ID
 * @param {object} data - 更新数据
 */
export function updateSurveyInstance(instanceId, data) {
  return request({
    url: `/surveys/instances/${instanceId}/`,
    method: 'patch',
    data
  })
}

/**
 * 重新生成问卷分享链接
 * @param {number} instanceId - 问卷实例ID
 */
export function regenerateSurveyLink(instanceId) {
  return request({
    url: `/surveys/instances/${instanceId}/regenerate_link/`,
    method: 'post'
  })
}

/**
 * 获取问卷统计信息
 * @param {number} instanceId - 问卷实例ID
 */
export function getSurveyStatistics(instanceId) {
  return request({
    url: `/surveys/instances/${instanceId}/statistics/`,
    method: 'get'
  })
}

/**
 * 通过UUID获取问卷内容（公开接口）
 * @param {string} uuid - 问卷UUID
 */
export function getSurveyByUUID(uuid) {
  return request({
    url: `/surveys/public/${uuid}/`,
    method: 'get'
  })
}

/**
 * 提交问卷答案（公开接口）
 * @param {string} uuid - 问卷UUID
 * @param {object} answers - 答案数据
 */
export function submitSurvey(uuid, answers, timing = {}) {
  return request({
    url: `/surveys/public/${uuid}/submit/`,
    method: 'post',
    data: { answers, ...timing }
  })
}
