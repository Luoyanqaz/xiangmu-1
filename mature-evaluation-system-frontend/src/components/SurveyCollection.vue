<template>
  <div v-if="counts" class="survey-collection">
    <div v-for="(label, role) in roles" :key="role">
      {{ label }}问卷：回收 {{ counts[role].received }} 份，{{ counts[role].valid === null ? '有效数未判定' : '有效 ' + counts[role].valid + ' 份' }}
      <span v-if="counts[role].unjudged">（含历史未判定 {{ counts[role].unjudged }} 份）</span>
      <strong v-if="!counts.shortages && counts[role].valid === 0"> · 有效样本不足</strong>
    </div>
    <div v-if="counts.shortages">有效样本不足学校：仅教师 {{ counts.shortages.teacher }} 所，仅学生 {{ counts.shortages.student }} 所，两类均不足 {{ counts.shortages.both }} 所。</div>
    <strong v-else-if="counts.teacher.valid === 0 && counts.student.valid === 0">两类有效问卷均为 0，问卷指标记 0 分，其他指标按实得分计入总分。</strong>
  </div>
</template>

<script setup>
defineProps({ counts: Object })
const roles = { teacher: '教师', student: '学生' }
</script>

<style scoped>
.survey-collection { line-height: 1.7; }
.survey-collection strong { color: #9a5414; }
</style>
