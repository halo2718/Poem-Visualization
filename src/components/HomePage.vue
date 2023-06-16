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
        <el-col :span="8">
          <div class="grid-content">
            <el-card class="bubble first chart">
              <template #header>
                <div class="card-header">
                  <h3>主题气泡图</h3>
                </div>
              </template>
              <TopicBubbleChart
                :dynasty="dynasties[dynastyIndex][1]"
                :selected-topics="selectedTopics"
                @click-topic="onTopicToggle"
              />
            </el-card>
            <el-card class="chart">
              <template #header>
                <div class="card-header">
                  <h3>已选中的主题</h3>
                </div>
              </template>
              <topic-view :selected-topics="selectedTopics" />
            </el-card>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="grid-content">
            <el-card class="keyword-rank first chart">
              <template #header>
                <div class="card-header">
                  <h3>意象排序图</h3>
                </div>
              </template>
              <KeywordsRankChart
                :dynasty="dynasties[dynastyIndex][1]"
                :selected-keywords="selectedKeywords"
                @click-keyword="onKeywordToggle"
              />
            </el-card>
            <el-card class="chart">
              <template #header>
                <div class="card-header">
                  <h3>已选中的意象</h3>
                </div>
              </template>
              <keyword-view :selected-keywords="selectedKeywords" />
            </el-card>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="grid-content">
            <el-card class="menu first chart">
              <el-menu
                :default-active="activeIndex"
                class="el-menu-demo"
                mode="horizontal"
                :ellipsis="false"
                @select="handleSelect"
              >
                <el-menu-item index="1"><h3>主题河流图</h3></el-menu-item>
                <el-menu-item index="2"><h3>主题-意向关联图</h3></el-menu-item>
                <el-menu-item index="3"><h3>意向-意向关联图</h3></el-menu-item>
              </el-menu>
              <div v-if="activeIndex == 1" class="topic-stream submenu">
                <TopicTrendStreamChart
                  :dynasty="dynasties[dynastyIndex][1]"
                  :selected-topics="selectedTopics"
                />
              </div>
              <div v-if="activeIndex == 2" class="sankey submenu">
                <SankeyChart
                  :selected-topics="selectedTopics"
                  :selected-keywords="selectedKeywords"
                />
              </div>
              <div v-if="activeIndex == 3" class="sankey submenu">
                <KeywordsChordChart :selected-keywords="selectedKeywords" />
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script>
import DynastyBar from './DynastyBar.vue';
import KeywordsRankChart from './KeywordsRankChart.vue';
import SankeyChart from './SankeyChart.vue';
import TopicBubbleChart from './TopicBubbleChart.vue';
import TopicTrendStreamChart from './TopicTrendStreamChart.vue';
import TopicView from './TopicView.vue';
import KeywordView from './KeywordView.vue';
import KeywordsChordChart from './KeywordsChordChart.vue';

export default {
  name: 'HomePage',
  components: {
    DynastyBar,
    TopicBubbleChart,
    TopicView,
    KeywordView,
    TopicTrendStreamChart,
    KeywordsRankChart,
    SankeyChart,
    KeywordsChordChart,
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
      selectedKeywords: [],
      activeIndex: 1,
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
    onKeywordToggle(v) {
      let keywords = this.selectedKeywords;
      if (keywords.includes(v)) {
        const idx = keywords.findIndex((item) => item === v);
        keywords.splice(idx, 1);
      } else {
        keywords.push(v);
      }
      this.selectedKeywords = [...keywords];
      console.log(this.selectedKeywords);
    },
    handleSelect(idx) {
      this.activeIndex = idx;
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

.chart {
  margin-top: 20px;
}

.first.chart {
  margin-top: 0;
}

.menu.chart .el-card__body {
  padding: 0 !important;
}

h3 {
  font-size: 16px !important;
}

.menu.chart .el-menu-item h3 {
  margin-block-start: -1px;
  margin-block-end: -1px;
}

.submenu {
  padding: 20px;
}
</style>
