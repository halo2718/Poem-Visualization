<template>
  <div>
    <el-slider
      :model-value="modelValue"
      @input="(v) => $emit('update:modelValue', v)"
      :format-tooltip="formatValue"
      :min="0"
      :max="dynasties.length - 1"
      :marks="marks"
      show-stops
    />
  </div>
</template>

<script>
export default {
  name: 'DynastyBar',
  props: {
    dynasties: Object,
    modelValue: Number,
  },
  emits: ['update:modelValue'],
  computed: {
    marks() {
      return Object.fromEntries(
        this.dynasties.map((item, idx) => [idx, item[0]])
      );
    },
  },
  methods: {
    formatValue(value) {
      if (
        !Number.isInteger(value) ||
        value < 0 ||
        value >= this.dynasties.length
      ) {
        return '';
      }
      return this.dynasties[value][0];
    },
  },
};
</script>

<style></style>
