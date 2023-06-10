<template>
  <el-container>
    <el-header>
      <h2>中国古代诗词数据可视化</h2>
    </el-header>
    <el-main>
      <el-row>
        <el-col :span="24" class="dynasty-bar">
          <dynasty-bar :dynasties="dynasties" v-model="dynastyIndex" />
        </el-col>
      </el-row>
      <el-row :gutter="20" class="charts">
        <el-col :span="12">
          <div class="grid-content">
            <el-card class="bubble-card">
              <template #header>
                <div class="card-header">
                  <h3>气泡图</h3>
                </div>
              </template>
              <TopicBubbleChart
                :dynasty="dynasties[dynastyIndex][1]"
                :selected-topics="selectedTopics"
                @click-topic="onTopicToggle"
              />
            </el-card>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="grid-content">
            <el-card>
              <template #header>
                <div class="card-header">
                  <h3>已选中的主题</h3>
                </div>
              </template>
              <topic-view :selected-topics="selectedTopics" />
            </el-card>
          </div>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script>
import DynastyBar from './DynastyBar.vue';
import TopicBubbleChart from './TopicBubbleChart.vue';
import TopicView from './TopicView.vue';

export default {
  name: 'HomePage',
  components: {
    DynastyBar,
    TopicBubbleChart,
    TopicView,
  },
  data() {
    return {
      dynasties: [
        ['先秦', 'XianQin'],
        ['秦', 'Qin'],
        ['汉', 'Han'],
        ['魏晋', 'WeiJin'],
        ['南北', 'NanBei'],
        ['隋', 'Sui'],
        ['唐', 'Tang'],
        ['宋', 'Song'],
        ['辽', 'Liao'],
        ['金', 'Jin'],
        ['元', 'Yuan'],
        ['明', 'Ming'],
        ['清', 'Qing'],
        ['近代', 'Jindai'],
        ['当代', 'Dangdai'],
      ],
      dynastyIndex: 0,
      selectedTopics: [],
    };
  },
  methods: {
    onTopicToggle(v) {
      let topics = this.selectedTopics;
      if (topics.includes(v)) {
        const idx = topics.findIndex((item) => item === v);
        topics.splice(idx, 1);
      } else {
        topics.push(v);
      }
      this.selectedTopics = [...topics];
    },
  },
};
</script>

<style>
.el-container {
  width: 100%;
  height: 100%;
  padding: 20px 60px;
}

.dynasty-bar {
  padding: 0 20px;
}
.charts {
  margin-top: 60px;
}

.el-card__header {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

.bubble-card .el-card__body {
  padding: 0 !important;
}
</style>
