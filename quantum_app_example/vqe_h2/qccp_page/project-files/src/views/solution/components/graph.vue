<template>
  <div class="qcis-graph">
    <pre class="qcis-text">{{ qcis }}</pre>
  </div>
</template>

<script setup>
defineProps({
  qcis: {
    type: String,
    default: ''
  }
});
</script>

<style lang="scss" scoped>
.qcis-graph {
  background: #f4f7fc;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #dce0eb;
}
.qcis-text {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  color: #41464f;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}
</style>
