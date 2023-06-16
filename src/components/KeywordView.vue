<template>
  <div>
    <template v-if="selectedKeywords.length">
      <el-row :gutter="20">
        <el-col
          v-for="(item, idx) in selectedKeywords"
          :key="idx"
          :span="2"
          class="keyword-item"
          >{{ item }}
        </el-col>
      </el-row>
    </template>
    <div v-else style="color: grey">(暂无选中意象)</div>
  </div>
</template>

<script>
export default {
  props: {
    selectedKeywords: Array,
  },
};
</script>
<style>
.keyword-item {
  font-size: 16px;
  margin-bottom: 8px;
}
</style>
