<template>
  <div v-if="isVisible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Select Metrics for {{ deviceName }}</h2>
        <button class="close-button" @click="closeModal">
          &times;
        </button>
      </div>
      
      <div class="modal-body">
        <p class="modal-description">
          Choose which metrics you want to display on your dashboard from {{ deviceName }}.
        </p>
        
        <div class="metrics-selection">
          <div class="metric-option" v-for="metric in availableMetrics" :key="metric.id">
            <label class="metric-checkbox">
              <input 
                type="checkbox" 
                :value="metric.id"
                v-model="selectedMetricIds"
                class="checkbox-input"
              />
              <span class="checkbox-custom"></span>
              <div class="metric-info">
                <span class="metric-name">{{ metric.name }}</span>
                <span class="metric-description">{{ metric.description }}</span>
              </div>
            </label>
          </div>
        </div>
        
        <div class="modal-actions">
          <button class="cancel-button" @click="closeModal">
            Cancel
          </button>
          <button class="save-button" @click="saveSelection">
            Save Selection
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  deviceName: {
    type: String,
    required: true
  },
  availableMetrics: {
    type: Array,
    required: true
  },
  selectedMetrics: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save'])

const selectedMetricIds = ref([])

// Watch for changes in selectedMetrics prop
watch(() => props.selectedMetrics, (newSelected) => {
  selectedMetricIds.value = newSelected.map(metric => metric.id || metric)
}, { immediate: true })

function closeModal() {
  emit('close')
}

function saveSelection() {
  const selectedMetrics = props.availableMetrics.filter(metric => 
    selectedMetricIds.value.includes(metric.id)
  )
  emit('save', selectedMetrics)
  closeModal()
}

// Helper function to format metric names for display
function formatMetricName(metricName) {
  const exceptions = {
    hrv: "HRV",
    vo2: "VO2",
    rem: "REM"
  };
  
  // Replace underscores with spaces and capitalize words
  let formatted = metricName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  
  // Apply exceptions
  Object.entries(exceptions).forEach(([key, value]) => {
    const regex = new RegExp(`\\b${key}\\b`, 'gi');
    formatted = formatted.replace(regex, value);
  });
  
  return formatted;
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(16px);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow-y: auto;
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: white;
}

.close-button {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  space-y: 1.5rem;
}

.modal-description {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 1.5rem 0;
  line-height: 1.5;
}

.metrics-selection {
  max-height: 300px;
  overflow-y: auto;
  space-y: 0.75rem;
}

.metric-option {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.metric-option:hover {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.02);
}

.metric-checkbox {
  display: flex;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  gap: 0.75rem;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.25rem;
  position: relative;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.checkbox-input:checked + .checkbox-custom {
  background: #3b82f6;
  border-color: #3b82f6;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
}

.metric-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-name {
  font-weight: 500;
  color: white;
  font-size: 0.875rem;
}

.metric-description {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.4;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.cancel-button {
  padding: 0.75rem 1.5rem;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.save-button {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.save-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .cancel-button,
  .save-button {
    width: 100%;
  }
}
</style>
