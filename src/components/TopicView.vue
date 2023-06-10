<template>
  <div>
    <template v-if="selectedTopics.length">
      <el-row :gutter="20">
        <el-col
          v-for="(item, idx) in selectedTopics"
          :key="idx"
          :span="4"
          class="topic-item"
          >{{ item }}
        </el-col>
      </el-row>
      <div>{{ item }}</div>
    </template>
    <div v-else style="color: grey">(暂无选中主题)</div>
  </div>
</template>

<script>
export default {
  props: {
    selectedTopics: Array,
  },
};
</script>
<style>
.topic-item {
  font-size: 16px;
  margin-bottom: 8px;
}
</style>
