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
  name: 'TopicBubbleChart',
  props: {
    dynasty: String,
    selectedTopics: Array,
  },
  emits: ['clickTopic'],
  setup(props, context) {
    // create ref to pass to D3 for DOM manipulation
    const svgRef = ref(null);
    const bubbleData = reactive({ value: null });

    // create another ref to observe resizing, since observing SVGs doesn't work!
    const { resizeRef, resizeState } = useResizeObserver();

    onMounted(() => {
      // pass ref with DOM element to D3, when mounted (DOM available)
      const svg = d3.select(svgRef.value);

      axios.get('/bubble.json').then((resp) => {
        bubbleData.value = Object.fromEntries(
          Object.entries(resp.data).map(([key, value]) => [
            key,
            value.map((item) => ({
              ...item,
              x: 0.3 * (Math.random() - 0.5),
              y: 0.3 * (Math.random() - 0.5),
            })),
          ])
        );
      });
      // whenever any dependencies (like data, resizeState) change, call this!

      watch([() => bubbleData.value, () => props.dynasty], () => {
        if (!bubbleData.value) return;
        const initialSelectedTopics = props.selectedTopics || [];
        svg.selectAll('g').remove();
        const mainGroup = svg.append('g');
        // The following code is the typical routine of my d3.js code.
        const { width, height } = resizeState.dimensions;
        const margin = { top: 10, right: 10, bottom: 10, left: 10 };
        // const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;
        mainGroup.attr('transform', `translate(${width / 2}, ${height / 2})`);
        // const xValue = d => d.value;
        // const yValue = d => d.name;
        // const xScale = d3.scaleLinear();
        // const yScale = d3.scaleBand();
        const color = d3
          .scaleSequential(d3.interpolateRainbow)
          .domain([0, 100]);
        /*
        Loading data and preprocessing data.
        Note that you can also preprocessing data in your own way using your prefered language, e.g., Python.
        */

        let bubbles = null;
        let labels = null;

        // const context = DOM.context2d(width, height);
        const nodes = [
          ...bubbleData.value[props.dynasty].map((item) => ({ ...item })),
        ];
        const selected = Object.fromEntries(
          nodes.map((item) => [
            item.id,
            initialSelectedTopics.includes(item.id),
          ])
        );
        console.log(initialSelectedTopics);
        console.log(selected);
        const onClick = (e) => {
          const id = e.target.__data__.id;
          selected[id] = !selected[id];
          d3.select('#bubble' + id)
            .transition()
            .duration(300)
            .style('opacity', selected[id] ? '1' : '0.3');
          d3.select('#bubble-text' + id)
            .transition()
            .duration(300)
            .style('fill', selected[id] ? 'white' : 'black');
          context.emit('clickTopic', id);
        };
        const simInit = function () {
          bubbles = mainGroup
            .selectAll('bubble')
            .data(nodes)
            .enter()
            .append('circle')
            .attr('id', (d) => 'bubble' + d.id)
            .attr('cx', (d) => d.x * innerWidth * 0.8)
            .attr('cy', (d) => d.y * innerHeight * 0.8)
            .attr('r', (d) => d.score * 0.3 * innerHeight)
            .style('fill', (d) => color(d.id))
            .style('opacity', (d) => (selected[d.id] ? '1' : '0.3'))
            .on('click', onClick);

          labels = mainGroup
            .selectAll('bubble-text')
            .data(nodes)
            .enter()
            .append('text')
            .text((d) => d.id)
            .attr('id', (d) => 'bubble-text' + d.id)
            .attr('text-anchor', 'middle')
            .style('font-size', (d) => 50 * d.score + 10 + 'px')
            .attr('x', (d) => d.x * innerWidth * 0.8)
            .attr('y', (d) => d.y * innerHeight * 0.8 + 25 * d.score)
            .style('fill', (d) => (selected[d.id] ? 'white' : 'black'))
            .style('opacity', '0.7')
            .on('click', onClick);
        };

        function ticked() {
          bubbles.attr('cx', (d) => d.x).attr('cy', (d) => d.y);
          labels.attr('x', (d) => d.x).attr('y', (d) => d.y + 25 * d.score);
        }

        simInit();
        d3.forceSimulation(nodes)
          .alphaTarget(0.3) // stay hot
          .velocityDecay(0.1) // low friction
          .force('x', d3.forceX().strength(0.001))
          .force('y', d3.forceY().strength(0.001))
          .force(
            'collide',
            d3
              .forceCollide()
              .radius((d) => d.r * 1.2)
              .iterations(3)
          )

          .force('charge', d3.forceManyBody().strength(-width * 0.002))
          .on('tick', ticked);
      });
    });

    return { svgRef, resizeRef };
  },
};
</script>
