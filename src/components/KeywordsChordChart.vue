<template>
  <div ref="resizeRef">
    <svg
      ref="svgRef"
      style="min-height: 450px; overflow: hidden; background-color: white"
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
  name: 'KeywordsChordChart',
  props: {
    selectedKeywords: Array,
  },
  setup(props) {
    // create ref to pass to D3 for DOM manipulation
    const svgRef = ref(null);
    const allData = reactive({ value: null });
    const valueData = reactive({ value: null });

    // create another ref to observe resizing, since observing SVGs doesn't work!
    const { resizeRef, resizeState } = useResizeObserver();

    onMounted(() => {
      // pass ref with DOM element to D3, when mounted (DOM available)
      const svg = d3.select(svgRef.value);
      Promise.all([axios.get('/z.csv'), axios.get('/chord.json')]).then(
        ([resp1, resp2]) => {
          allData.value = {
            nodes: d3.csvParse(resp1.data),
            matrix: resp2.data,
          };
        }
      );
      // whenever any dependencies (like data, resizeState) change, call this!

      watch([() => allData.value, () => props.selectedKeywords], () => {
        if (!allData.value) return;
        const idxList = allData.value.nodes
          .map((item, idx) =>
            props.selectedKeywords.includes(item.name) ? idx : -1
          )
          .filter((idx) => idx >= 0);
        valueData.value = {
          nodes: idxList.map((idx) => allData.value.nodes[idx]),
          matrix: idxList.map((idx) =>
            idxList.map((idx2) => allData.value.matrix[idx][idx2])
          ),
        };
      });
      watch([() => valueData.value], () => {
        if (!valueData.value) return;
        // const selectedTopics = props.selectedTopics || [];
        // const selectedKeywords = props.selectedKeywords || [];
        const { nodes, matrix } = valueData.value;
        if (!nodes.length) return;
        svg.selectAll('g').remove();
        const mainGroup = svg
          .append('g')
          .attr('width', '100%')
          .attr('height', '100%');
        // The following code is the typical routine of my d3.js code.
        const { width, height } = resizeState.dimensions;
        const margin = { top: 0, right: 0, bottom: 0, left: 0 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;
        mainGroup.attr(
          'transform',
          `translate(${innerWidth / 2}, ${innerHeight / 2})`
        );
        const RADIUS = 120;

        const colorScale = d3
          .scaleSequential(d3.interpolateRainbow)
          .domain([0, nodes.length]);
        // adding ribbons between nodes.
        let chord = d3.chord().padAngle(0);
        let ribbons = chord(matrix);
        let drawRibbon = d3.ribbon().radius(RADIUS);

        mainGroup
          .append('g')
          .attr('class', 'ribbonGroup')
          .selectAll('.myRibbon')
          .data(ribbons)
          .join('path')
          .attr(
            'class',
            (d) => `myRibbon ribbon-${d.source.index} ribbon-${d.target.index} `
          )
          .attr('d', drawRibbon)
          .attr('fill', (d) =>
            d.source.value > d.target.value
              ? colorScale(d.source.index)
              : colorScale(d.target.index)
          )
          .attr('opacity', 0.5);

        // adding arcs representing nodes.
        let arc = d3
          .arc()
          .innerRadius(RADIUS)
          .outerRadius(RADIUS + 50);
        mainGroup
          .append('g')
          .attr('class', 'arcGroup')
          .selectAll('.myArc')
          .data(ribbons.groups)
          .join('path')
          .attr('class', 'myArc')
          .attr('d', arc)
          .attr('fill', (d) => colorScale(d.index))
          .on('mouseover', function (e) {
            d3.selectAll('.myArc').attr('fill-opacity', 0.2);
            d3.select(e.target).attr('fill-opacity', 1);
            d3.selectAll('.myRibbon').attr('fill-opacity', 0.3);
            d3.selectAll(`.ribbon-${e.target.__data__.index}`).attr(
              'fill-opacity',
              0.8
            );
          })
          .on('mouseleave', function () {
            d3.selectAll('.myArc').attr('fill-opacity', 1);
            d3.selectAll('.myRibbon').attr('fill-opacity', 0.5);
          });

        // adding texts representing nodes.
        mainGroup
          .append('g')
          .attr('class', 'textGroup')
          .selectAll('.myText')
          .data(ribbons.groups)
          .join('text')
          .attr('stroke', '#000000')
          .style('font-size', 12)
          .style('font-weight', 100)
          .attr('class', 'myText')
          .attr(
            'transform',
            (d) => `
            rotate(${(d.startAngle * 180) / Math.PI - 90})
            translate(${RADIUS + 50}, 0)
            rotate(${(d.startAngle * 180) / Math.PI < 180 ? 0 : 180})`
          )
          .attr('text-anchor', (d) =>
            (d.startAngle * 180) / Math.PI < 180 ? 'start' : 'end'
          )
          .attr('dx', (d) => ((d.startAngle * 180) / Math.PI < 180 ? 5 : -5))
          .text((d) => nodes[d.index].name);
      });
    });

    return { svgRef, resizeRef };
  },
};
</script>
