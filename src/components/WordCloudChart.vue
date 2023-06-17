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
import * as d3cloud from 'd3-cloud';
import useResizeObserver from '@/use/resizeObserver';

export default {
  name: 'WordCloudChart',
  props: {
    selectedTopics: Array,
  },
  setup(props) {
    // create ref to pass to D3 for DOM manipulation
    const svgRef = ref(null);
    const cloudData = reactive({ value: null });

    // create another ref to observe resizing, since observing SVGs doesn't work!
    const { resizeRef, resizeState } = useResizeObserver();

    onMounted(() => {
      // pass ref with DOM element to D3, when mounted (DOM available)
      const svg = d3.select(svgRef.value);

      axios.get('/wordcloud.json').then((resp) => {
        cloudData.value = Object.fromEntries(Object.entries(resp.data));
      });
      // whenever any dependencies (like data, resizeState) change, call this!

      watch([() => cloudData.value, () => props.selectedTopics], () => {
        if (!cloudData.value) return;
        const selectedTopics = props.selectedTopics || [];
        svg.selectAll('g').remove();
        if (!selectedTopics.length) return;
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

        const color = d3.scaleSequential(d3.interpolateCool).domain([0, 100]);
        var layout = d3cloud();
        function draw(words) {
          console.log(words);
          mainGroup
            .append('g')
            .attr(
              'transform',
              'translate(' +
                layout.size()[0] / 2 +
                ',' +
                layout.size()[1] / 2 +
                ')'
            )
            .selectAll('text')
            .data(words)
            .enter()
            .append('text')
            .style('font-size', function (d) {
              return d.size;
            })
            .style('fill', () => color(Math.random() * 100))
            .attr('text-anchor', 'middle')
            .style('font-family', 'Impact')
            .attr('transform', function (d) {
              return 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')';
            })
            .text(function (d) {
              return d.text;
            });
        }
        var topic = selectedTopics[selectedTopics.length - 1];
        const words = cloudData.value[topic];
        layout
          .size([innerWidth, innerHeight])
          .words(
            words.map(function (d) {
              return { text: d.word, size: Math.min(d.prob * 5000 + 2, 60)};
            })
          )
          .padding(5) //space between words
          .rotate(function () {
            return 0;
          })
          .fontSize(function (d) {
            return d.size;
          }) // font size of words
          .on('end', draw);
        layout.start();
      });
    });

    return { svgRef, resizeRef };
  },
};
</script>
