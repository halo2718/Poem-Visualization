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
import { onMounted, ref, watch, reactive } from 'vue';
import axios from 'axios';
import * as d3 from 'd3';
import * as d3sankey from 'd3-sankey';
import _ from 'lodash';
import useResizeObserver from '@/use/resizeObserver';

export default {
  name: 'SankeyChart',
  props: {
    selectedTopics: Array,
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

      axios.get('/topic_keywords_chords.json').then((resp) => {
        allData.value = resp.data;
      });

      const updateValue = () => {
        const topics = props.selectedTopics;
        const keywords = props.selectedKeywords;

        const links = _.flatten(
          _.entries(allData.value).map(([topic, obj]) => {
            if (!topics.includes(Number(topic))) return [];
            return _.entries(obj)
              .filter(
                ([keyword, value]) => keywords.includes(keyword) && value > 1e-3
              )
              .map(([keyword, value]) => ({
                source: topic,
                target: keyword,
                value,
              }));
          })
        );
        const nodes = Array.from(
          new Set(_.flatten(links.map((item) => [item.source, item.target])))
        ).map((item) => ({ name: item }));
        valueData.value = {
          nodes,
          links,
        };
      };

      watch(
        [
          () => allData.value,
          () => props.selectedKeywords,
          () => props.selectedTopics,
        ],
        updateValue
      );

      /*
      axios.get('/sankey.json').then((resp) => {
        valueData.value = Object.fromEntries(Object.entries(resp.data));
      });
      */

      // whenever any dependencies (like data, resizeState) change, call this!

      watch([() => valueData.value], () => {
        if (!valueData.value) return;
        if (!valueData.value.nodes.length || !valueData.value.links.length)
          return;
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
        mainGroup.attr('transform', `translate(${margin.left}, ${margin.top})`);

        const colorScale = d3.scaleOrdinal(d3.schemeSet3);

        const sankey = d3sankey
          .sankey()
          .nodeWidth(30)
          .nodePadding(5)
          .size([innerWidth, innerHeight])
          .nodeId((d) => d.name);

        const { nodes, links } = sankey({
          nodes: valueData.value.nodes,
          links: valueData.value.links,
        });

        mainGroup
          .append('g')
          .selectAll()
          .data(nodes)
          .join('g')
          .attr('class', 'sankey-node')
          .attr('indexName', (d) => d.name)
          .append('rect')
          .attr('fill', (d) => colorScale(d.name))
          .attr('x', (d) => d.x0)
          .attr('y', (d) => d.y0)
          .attr('height', (d) => d.y1 - d.y0)
          .attr('width', (d) => d.x1 - d.x0)
          .append('title')
          .text((d) => `${d.name}`);

        mainGroup
          .append('g')
          .attr('fill', 'none')
          .selectAll()
          .data(links)
          .join('path')
          .attr('class', 'sankey-path')
          .attr('indexName', (d) => d.source.name + '-' + d.target.name)
          .attr('d', d3sankey.sankeyLinkHorizontal())
          .attr('stroke', (d) => colorScale(d.source.name))
          .attr('stroke-width', (d) => d.width)
          .attr('stroke-opacity', '0.5')
          .append('title')
          .text((d) => `${d.value.toLocaleString()}`);

        mainGroup
          .selectAll('.sankey-node')
          .append('text')
          .attr('class', 'sankey-text')
          .attr('x', (d) => (d.x0 + d.x1) / 2)
          .attr('y', (d) => (d.y0 + d.y1) / 2)
          .attr('stroke', '#000000')
          .attr('text-anchor', 'middle')
          .style('font-size', 12)
          .style('font-weight', 100)
          .attr('dy', 6)
          .text((d) => d.name);

        d3.selectAll('.sankey-path')
          .on('mouseover', function (e, d) {
            d3.selectAll('.sankey-node, .sankey-path')
              .attr('fill-opacity', '0.1')
              .attr('stroke-opacity', '0.1');

            d3.select(e.target).attr('stroke-opacity', '0.5');
            const sourcename = d.source.name;
            const targetname = d.target.name;
            d3.selectAll('.sankey-node').attr('fill-opacity', (d) =>
              d.name == sourcename || d.name == targetname ? 1 : 0.1
            );
            d3.selectAll('.sankey-node').attr('stroke-opacity', (d) =>
              d.name == sourcename || d.name == targetname ? 1 : 0.1
            );
          })
          .on('mouseleave', function () {
            d3.selectAll('.sankey-node, .sankey-path')
              .attr('fill-opacity', '1')
              .attr('stroke-opacity', '0.5');
          });
      });
    });

    return { svgRef, resizeRef };
  },
};
</script>
