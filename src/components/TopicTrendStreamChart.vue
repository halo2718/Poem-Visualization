<template>
  <div ref="resizeRef">
    <svg
      ref="svgRef"
      style="min-height: 300px; overflow: hidden; background-color: white"
    >
      <g class="x-axis" />
      <g class="y-axis" />
    </svg>
  </div>
</template>

<script>
import { onMounted, ref, watch, reactive } from 'vue';
import axios from 'axios';
import * as d3 from 'd3';
import useResizeObserver from '@/use/resizeObserver';

export default {
  name: 'TopicTrendStreamChart',
  props: {
    dynasty: String,
    selectedTopics: Array,
  },
  setup(props) {
    // create ref to pass to D3 for DOM manipulation
    const svgRef = ref(null);
    const trendData = reactive({ value: null });

    // create another ref to observe resizing, since observing SVGs doesn't work!
    const { resizeRef, resizeState } = useResizeObserver();

    onMounted(() => {
      // pass ref with DOM element to D3, when mounted (DOM available)
      const svg = d3.select(svgRef.value);

      axios.get('/topic_trend.json').then((resp) => {
        trendData.value = Object.fromEntries(Object.entries(resp.data));
      });
      // whenever any dependencies (like data, resizeState) change, call this!

      watch([() => trendData.value, () => props.selectedTopics], () => {
        if (!trendData.value) return;
        const selectedTopics = props.selectedTopics || [];
        svg.selectAll('g').remove();
        const mainGroup = svg
          .append('g')
          .attr('width', '100%')
          .attr('height', '100%');
        // The following code is the typical routine of my d3.js code.
        const { width, height } = resizeState.dimensions;
        const margin = { top: 30, right: 30, bottom: 30, left: 30 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;
        mainGroup.attr('transform', `translate(${margin.left}, ${margin.top})`);

        const data = [];
        const topics = [];
        for (let i in selectedTopics) {
          data.push(trendData.value[selectedTopics[i]]);
          topics.push(selectedTopics[i]);
        }

        const xlist = [
          'XianQin',
          'Qin',
          'Han',
          'WeiJin',
          'NanBei',
          'Sui',
          'Tang',
          'Song',
          'Liao',
          'Jin',
          'Yuan',
          'Ming',
          'Qing',
          'Jindai',
          'Dangdai',
        ];

        const xticklist = {
          XianQin: '先秦',
          Qin: '秦',
          Han: '汉',
          WeiJin: '魏晋',
          NanBei: '南北',
          Sui: '隋',
          Tang: '唐',
          Song: '宋',
          Liao: '辽',
          Jin: '金',
          Yuan: '元',
          Ming: '明',
          Qing: '清',
          Jindai: '近代',
          Dangdai: '当代',
        };

        const xScale = d3.scalePoint().domain(xlist).range([0, innerWidth]);

        mainGroup
          .append('g')
          .attr('transform', 'translate(0,' + innerHeight + ')')
          .call(d3.axisBottom(xScale).tickFormat((d) => xticklist[d]));

        // Add Y axis
        if (!data.length) return;
        const mat = data.map((item) => Object.values(item));
        const iterX = new Array(mat.length).fill(0);
        const iterY = new Array(mat[0].length).fill(0);
        const yScale = d3
          .scaleLinear()
          .domain([
            0,
            iterY
              .map((_, j) =>
                iterX.map((_, i) => mat[i][j]).reduce((a, b) => a + b)
              )
              .reduce((a, b) => Math.max(a, b)),
          ])
          .range([innerHeight, 0]);

        const data_array = [];
        const keys = [];
        for (let i in data) {
          keys.push(i);
        }

        for (let i in xlist) {
          let item = new Object();
          for (let j in keys) {
            let idx = keys[j];
            item[idx] = data[idx][xlist[i]];
          }
          item['dynasty'] = xlist[i];
          data_array.push(item);
        }

        const color = d3.scaleOrdinal().domain(keys).range(d3.schemeSet1);

        const stackedData = d3.stack().keys(keys)(data_array);

        const areaGen = d3
          .area()
          .x((d) => xScale(d.data.dynasty))
          .y0((d) => yScale(d[0]))
          .y1((d) => yScale(d[1]));

        var tooltip = mainGroup
          .append('text')
          .attr('id', 'tooltip')
          .attr('transform', 'translate(' + innerWidth * 0.9 + ', 0)')
          .style('fill', 'black')
          .style('opacity', 0)
          .style('font-size', 17);

        var mouseover = function (d) {
          tooltip.style('opacity', 1);
          d3.selectAll('#stream').style('opacity', 0.5);
          d3.select(d.target).style('opacity', 1);
        };
        var mousemove = function (d, i) {
          // console.log(d, i)
          let grp = topics[i.key];
          tooltip.text(grp);
        };
        var mouseleave = function () {
          tooltip.style('opacity', 0);
          d3.selectAll('#stream').style('opacity', 1);
        };

        mainGroup.append('g').attr('id', 'stream-group');
        d3.select('#stream-group')
          .selectAll('.areas')
          .data(stackedData)
          .join('path')
          .attr('d', areaGen)
          .attr('id', 'stream')
          .on('mouseover', mouseover)
          .on('mousemove', mousemove)
          .on('mouseleave', mouseleave)
          .attr('fill', (d) => color(d.key));
      });
    });

    return { svgRef, resizeRef };
  },
};
</script>
