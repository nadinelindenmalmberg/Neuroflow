<template>
  <div v-if="isActive" class="tab-content">
    <slot />
  </div>
</template>

<script setup>
import { inject, computed } from 'vue'

const props = defineProps({
  value: {
    type: String,
    required: true
  }
})

const activeTab = inject('activeTab')
const isActive = computed(() => activeTab.value === props.value)
</script>

<style scoped>
.tab-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
