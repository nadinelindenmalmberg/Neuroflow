<template>
  <div class="tabs-container">
    <div class="tabs-list" role="tablist">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="['tab-trigger', { active: activeTab === tab.value }]"
        @click="setActiveTab(tab.value)"
        role="tab"
        :aria-selected="activeTab === tab.value"
      >
        {{ tab.label }}
      </button>
    </div>
    
    <div class="tabs-content">
      <slot :activeTab="activeTab" />
    </div>
  </div>
</template>

<script setup>
import { ref, provide, watch } from 'vue'

const props = defineProps({
  tabs: {
    type: Array,
    required: true
  },
  defaultValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['tabChange'])

const activeTab = ref(props.defaultValue || props.tabs[0]?.value || '')

// Watch for changes in defaultValue (for route changes)
watch(() => props.defaultValue, (newValue) => {
  if (newValue && newValue !== activeTab.value) {
    activeTab.value = newValue
  }
}, { immediate: true })

function setActiveTab(value) {
  activeTab.value = value
  emit('tabChange', value)
}

provide('activeTab', activeTab)
</script>

<style scoped>
.tabs-container {
  width: 100%;
}

.tabs-list {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.5rem;
  padding: 0.25rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-trigger {
  flex: 1;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.tab-trigger:hover {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.05);
}

.tab-trigger.active {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.tabs-content {
  min-height: 200px;
}
</style>
