<template>
  <div class="device-card">
    <div class="device-header">
      <div class="device-info">
        <div class="device-logo" :class="status">
          <component :is="logo" class="logo-icon" />
        </div>
        <div class="device-details">
          <h3 class="device-name">{{ name }}</h3>
          <p class="device-status" :class="status">
            {{ status === 'active' ? 'Connected' : 'Disconnected' }}
          </p>
        </div>
      </div>
      <div class="device-actions">
        <button 
          v-if="status === 'active'" 
          class="action-button sync"
          @click="$emit('syncNow')"
          :disabled="syncing"
        >
          {{ syncing ? 'Syncing...' : 'Sync Now' }}
        </button>
        <button 
          v-if="status === 'active'" 
          class="action-button disconnect"
          @click="$emit('disconnect')"
        >
          Disconnect
        </button>
        <button 
          v-else 
          class="action-button connect"
          @click="$emit('connect')"
        >
          Connect
        </button>
      </div>
    </div>
    
    <div class="device-content">
      <div class="device-stats">
        <div class="stat">
          <span class="stat-label">Data Points</span>
          <span class="stat-value">{{ dataPoints.toLocaleString() }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Last Sync</span>
          <span class="stat-value">{{ lastSync }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Sync Frequency</span>
          <span class="stat-value">{{ syncFrequency }}</span>
        </div>
      </div>
      
      <div class="device-metrics">
        <div class="metrics-header">
          <h4 class="metrics-title">Available Metrics</h4>
          <button 
            v-if="status === 'active'" 
            class="select-metrics-btn"
            @click="$emit('selectMetrics', name)"
          >
            Select Metrics
          </button>
        </div>
        <div class="metrics-list">
          <span 
            v-for="metric in availableMetrics" 
            :key="metric.id" 
            class="metric-tag"
            :class="{ 'selected': selectedMetrics.includes(metric.id) }"
          >
            {{ metric.name }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Watch, Zap, Shield } from 'lucide-vue-next'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  logo: {
    type: [String, Object],
    required: true
  },
  connected: {
    type: Boolean,
    default: false
  },
  lastSync: {
    type: String,
    required: true
  },
  metrics: {
    type: Array,
    required: true
  },
  syncFrequency: {
    type: String,
    required: true
  },
  dataPoints: {
    type: Number,
    default: 0
  },
  selectedMetrics: {
    type: Array,
    default: () => []
  },
  availableMetrics: {
    type: Array,
    default: () => []
  },
  syncing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['connect', 'disconnect', 'selectMetrics', 'syncNow'])

const status = computed(() => props.connected ? 'active' : 'inactive')

// Helper function to get metric display name
function getMetricDisplayName(metricId) {
  const metric = props.availableMetrics.find(m => m.id === metricId)
  return metric?.name || formatMetricName(metricId)
}

// Fallback function to format metric names
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
.device-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.device-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, transparent 50%);
  pointer-events: none;
}

.device-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.device-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.device-logo {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.device-logo.active {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.device-logo.inactive {
  background: rgba(107, 114, 128, 0.2);
  color: #6b7280;
}

.logo-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.device-details {
  flex: 1;
}

.device-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.25rem 0;
}

.device-status {
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0;
}

.device-status.active {
  color: #22c55e;
}

.device-status.inactive {
  color: #6b7280;
}

.device-actions {
  flex-shrink: 0;
}

.action-button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.action-button.connect {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-button.connect:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.action-button.sync {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  margin-right: 0.5rem;
}

.action-button.sync:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.action-button.sync:disabled {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  cursor: not-allowed;
  opacity: 0.6;
}

.action-button.disconnect {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.action-button.disconnect:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: translateY(-1px);
}

.device-content {
  space-y: 1.5rem;
}

.device-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.stat-value {
  display: block;
  font-size: 0.875rem;
  color: white;
  font-weight: 600;
}

.device-metrics {
  space-y: 0.75rem;
}

.metrics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.metrics-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.select-metrics-btn {
  padding: 0.25rem 0.5rem;
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.select-metrics-btn:hover {
  background: rgba(59, 130, 246, 0.3);
  transform: translateY(-1px);
}

.metrics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.metric-tag {
  padding: 0.25rem 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  transition: all 0.2s ease;
}

.metric-tag.selected {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.4);
  color: #22c55e;
}

/* Responsive Design */
@media (max-width: 768px) {
  .device-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .device-stats {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .metrics-list {
    justify-content: flex-start;
  }
}
</style>
