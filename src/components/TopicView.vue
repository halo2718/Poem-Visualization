<template>
  <div>
    <template v-if="selectedTopics.length">
      <el-row :gutter="20">
        <template v-for="(item, idx) in selectedTopics" :key="idx">
          <el-col
            :span="2"
            :offset="2"
            class="topic-item"
            style="font-weight: 700"
          >
            {{ item }}:
          </el-col>
          <el-col :span="20" class="topic-item">
            {{ keywordsMap[item] }}
          </el-col>
        </template>
      </el-row>
    </template>
    <div v-else style="color: grey">(暂无选中主题)</div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    selectedTopics: Array,
  },
  data() {
    return {
      keywordsMap: {},
    };
  },
  mounted() {
    axios.get('/topic_keywords.json').then((resp) => {
      this.keywordsMap = resp.data;
    });
  },
};
</script>
<style>
.topic-item {
  font-size: 16px;
  margin-bottom: 8px;
}
</style>
