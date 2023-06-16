<template>
  <div ref="resizeRef">
    <svg
      ref="svgRef"
      style="min-height: 400px; overflow: hidden; background-color: white"
    >
      <g class="x-axis" />
      <g class="y-axis" />
    </svg>
  </div>
</template>

<script>
import { onMounted, ref, watch } from 'vue';
import axios from 'axios';
import * as d3 from 'd3';
import useResizeObserver from '@/use/resizeObserver';

export default {
  name: 'KeywordsRankChart',
  props: {
    dynasty: String,
    selectedKeywords: Array,
  },
  setup(props, context) {
    // create ref to pass to D3 for DOM manipulation
    const svgRef = ref(null);

    // create another ref to observe resizing, since observing SVGs doesn't work!
    const { resizeRef, resizeState } = useResizeObserver();
    const cache = {};
    const fetchData = async (key) => {
      if (cache[key]) {
        return cache[key];
      }
      const resp = await axios.get('/fullinfo_' + props.dynasty + '.csv');
      const { data } = resp;
      const processedData = d3
        .csvParse(data)
        .sort((a, b) => b.Val - a.Val)
        .slice(0, 20)
        .map((item, idx) => ({
          ...item,
          id: idx,
        }));
      cache[key] = processedData;
      return processedData;
    };
    onMounted(() => {
      // pass ref with DOM element to D3, when mounted (DOM available)
      const svg = d3.select(svgRef.value);

      const update = () => {
        fetchData(props.dynasty).then((kwdData) => {
          if (!kwdData) return;
          const initialSelectedKeywords = props.selectedKeywords || [];
          const selected = Object.fromEntries(
            kwdData.map((item) => [
              item.Name,
              initialSelectedKeywords.includes(item.Name),
            ])
          );
          svg.selectAll('g').remove();
          const mainGroup = svg
            .append('g')
            .attr('width', '100%')
            .attr('height', '100%');
          // The following code is the typical routine of my d3.js code.
          const { width, height } = resizeState.dimensions;
          const margin = { top: 10, right: 30, bottom: 30, left: 30 };
          const innerWidth = width - margin.left - margin.right;
          const innerHeight = height - margin.top - margin.bottom;
          mainGroup.attr(
            'transform',
            `translate(${margin.left}, ${margin.top})`
          );
          const xScale = d3.scaleLinear();
          const yScale = d3.scaleBand();

          // var a = d3.rgb(255, 153, 51); //浅绿
          // var b = d3.rgb(0, 0, 255); //深绿
          // var color = d3.interpolate(a, b); //颜色插值函数
          var color = d3.interpolatePRGn;

          // calculationg scales:
          yScale
            .domain(kwdData.map((d) => d.Name))
            .range([0, innerHeight])
            .padding(0.1);
          xScale
            .domain([0, d3.max(kwdData, (d) => d.Val)])
            .range([0, innerWidth]);

          // console.log(data.Emotion);
          /*
          const linear = d3
            .scaleLinear()
            .domain(kwdData.map((d) => d.Emotion))
            .range([0, 1]);
          */
          // data-join for rectangles:

          mainGroup
            .selectAll('rect')
            .data(kwdData)
            .join('rect')
            .attr('stroke-width', 2)
            .attr('stroke', (d) => (selected[d.Name] ? 'orange' : 'white'))
            .on('click', (e) => {
              const id = e.target.__data__.Name;
              selected[id] = !selected[id];
              d3.select(e.target)
                .transition()
                .duration(500)
                .attr('stroke', selected[id] ? 'orange' : 'white');
              context.emit('clickKeyword', id);
            })
            .attr('height', yScale.bandwidth())
            .attr('x', 0)
            .attr('y', (d) => yScale(d.Name))
            .attr('fill', function (d) {
              if (d.Emotion < 0) {
                return d3.rgb(0, 0, 0);
              }
              return color(d.Emotion);
            })
            .transition()
            .ease(d3.easeCubic)
            .duration(1000)
            .attr('width', (d) => xScale(d.Val));
          // adding axes:
          const xAxisMethod = d3.axisBottom(xScale);
          const yAxisMethod = d3.axisLeft(yScale);
          const xAxisGroup = mainGroup.append('g').call(xAxisMethod);
          mainGroup.append('g').call(yAxisMethod);
          xAxisGroup.attr('transform', `translate(${0}, ${innerHeight})`);
        });
      };
      update();
      watch([() => props.dynasty], update);
    });
    return { svgRef, resizeRef };
  },
};
</script>
