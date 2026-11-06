<template>
  <span class="school-report-rank" :class="{ inline }" :title="reason || undefined">
    <span class="rank-entry"><span>同类型学校位次：</span><strong>{{ display(ranking?.same_type) }}</strong></span>
    <span class="rank-entry"><span>区域位次：</span><strong>{{ display(ranking?.region) }}</strong></span>
  </span>
</template>

<script setup>
defineProps({ ranking: Object, reason: String, inline: Boolean })
function display(value) {
  return value?.rank != null && value.total > 0 ? `${value.rank}/${value.total}` : '—'
}
</script>

<style scoped>
.school-report-rank { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; color: #315d96; font-size: 13px; }
.rank-entry { display: flex; justify-content: space-between; align-items: baseline; gap: 6px; padding: 7px 8px; background: #eaf2ff; border-radius: 3px; }
.rank-entry strong { white-space: nowrap; font-variant-numeric: tabular-nums; }
.inline { display: inline-flex; flex-direction: row; flex-wrap: wrap; gap: 6px 14px; margin: 0 0 0 8px; font-size: inherit; vertical-align: baseline; text-indent: 0; }
.inline .rank-entry { display: inline-flex; padding: 0; background: transparent; gap: 0; }
@media print { .school-report-rank { print-color-adjust: exact; } }
</style>
