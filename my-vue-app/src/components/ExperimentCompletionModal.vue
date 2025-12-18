<template>
  <div v-if="isVisible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop data-debug="single-modal">
      <!-- All Content in One Section -->
      <div class="modal-content">
        <!-- Header Inside Content -->
        <div class="content-header">
          <h2 class="modal-title">Conclude Experiment</h2>
          <button class="close-button" @click="closeModal">
            <X class="w-4 h-4" />
          </button>
        </div>

        <div class="instruction">
          <p>Do you want to drop any of the experiment data points?</p>
        </div>

        <!-- Data Points Grid -->
        <div class="data-points-section">
          <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading experiment data...</p>
          </div>
          
          <div v-else-if="error" class="error-state">
            <p class="error-message">{{ error }}</p>
          </div>

          <div v-else class="data-points-grid">
            <button
              v-for="(dataPoint, index) in dataPoints"
              :key="index"
              class="data-point-button"
              :class="{ 
                'excluded': !dataPoint.included,
                'included': dataPoint.included 
              }"
              @click="dataPoint.hasData ? toggleDataPoint(index) : null"
              :title="dataPoint.hasData ? `${dataPoint.date}: ${dataPoint.value}` : `${dataPoint.date}: No data yet`"
            >
              <div class="data-point-value">{{ dataPoint.value }}</div>
              <div class="data-point-date">{{ formatDate(dataPoint.date) }}</div>
            </button>
          </div>
        </div>

        <!-- Statistics Preview -->
        <div v-if="!loading && !error" class="statistics-preview">
          <div class="stat-item">
            <span class="stat-label">Selected points</span>
            <span class="stat-value">{{ totalRealDataCount === 0 ? '—' : `${includedCount} / ${totalRealDataCount}` }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Average</span>
            <span class="stat-value">{{ calculatedAverage }}</span>
          </div>
        </div>

        <!-- Actions Inside Content -->
        <div class="content-actions">
          <button 
            type="button" 
            class="button-primary" 
            @click="concludeExperiment"
            :disabled="totalRealDataCount === 0 || includedCount === 0 || loading"
          >
            {{ totalRealDataCount === 0 ? 'No Data to Conclude' : 'Complete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { X } from 'lucide-vue-next';
import { getApiUrl } from '../config';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  experiment: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'complete']);

// State
const dataPoints = ref([]);
const loading = ref(false);
const error = ref(null);

// Computed properties
const includedCount = computed(() => {
  return dataPoints.value.filter(point => point.included && point.hasData).length;
});

const totalRealDataCount = computed(() => {
  return dataPoints.value.filter(point => point.hasData).length;
});

const calculatedAverage = computed(() => {
  const includedPoints = dataPoints.value.filter(point => point.included && point.hasData);
  if (includedPoints.length === 0) return '—';
  
  const sum = includedPoints.reduce((acc, point) => acc + point.value, 0);
  return (sum / includedPoints.length).toFixed(1);
});

// Watch for modal visibility - only trigger when modal opens
watch(() => props.isVisible, (visible) => {
  if (visible && props.experiment && !loading.value) {
    fetchExperimentData();
  }
});

// Methods
async function fetchExperimentData() {
  if (!props.experiment) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(getApiUrl(`/experiments/${props.experiment.id}/datapoints`));
    
    if (!response.ok) {
      throw new Error('Failed to fetch experiment data');
    }
    
    const data = await response.json();
    
    // Transform data to include selection state
    const realDataPoints = data.datapoints.map(point => ({
      date: point.date,
      value: point.value,
      included: true,
      hasData: true
    }));
    
    // Generate full experiment period data with placeholders
    dataPoints.value = generateExperimentPeriodData(realDataPoints);
    
  } catch (err) {
    console.error('Error fetching experiment data:', err);
    error.value = 'Failed to load experiment data. Please try again.';
  } finally {
    loading.value = false;
  }
}

function generateExperimentPeriodData(realDataPoints) {
  if (!props.experiment?.start_date || !props.experiment?.end_date) {
    return realDataPoints;
  }
  
  const startDate = new Date(props.experiment.start_date);
  const endDate = new Date(props.experiment.end_date);
  const periodData = [];
  const realDataMap = new Map();
  
  realDataPoints.forEach(point => {
    realDataMap.set(point.date, point);
  });
  
  let currentDate = new Date(startDate);
  while (currentDate <= endDate) {
    const dateString = currentDate.toISOString().split('T')[0];
    
    if (realDataMap.has(dateString)) {
      periodData.push(realDataMap.get(dateString));
    } else {
      periodData.push({
        date: dateString,
        value: '—',
        included: false,
        hasData: false
      });
    }
    
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return periodData;
}

function toggleDataPoint(index) {
  if (dataPoints.value[index].hasData) {
    dataPoints.value[index].included = !dataPoints.value[index].included;
  }
}

function formatDate(dateString) {
  const date = new Date(dateString);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return 'Today';
  } else if (date.toDateString() === yesterday.toDateString()) {
    return 'Yesterday';
  }
  
  const month = date.getMonth() + 1;
  const day = date.getDate();
  return `${month}/${day}`;
}

function closeModal() {
  emit('close');
  resetModal();
}

function resetModal() {
  dataPoints.value = [];
  loading.value = false;
  error.value = null;
}

async function concludeExperiment() {
  if (totalRealDataCount.value === 0 || includedCount.value === 0) return;
  
  const includedPoints = dataPoints.value.filter(point => point.included && point.hasData);
  
  try {
    const response = await fetch(getApiUrl(`/experiments/${props.experiment.id}/complete`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        included_datapoints: includedPoints,
        final_average: calculatedAverage.value === '—' ? null : parseFloat(calculatedAverage.value)
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to complete experiment');
    }
    
    const result = await response.json();
    emit('complete', result);
    closeModal();
    
  } catch (err) {
    console.error('Error completing experiment:', err);
    error.value = 'Failed to complete experiment. Please try again.';
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.modal-container {
  background: #1f1f2e;
  border-radius: 12px;
  width: 600px;
  max-width: 90vw;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-content {
  padding: 1.5rem;
  overflow: hidden;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: white;
}

.close-button {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.instruction {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.instruction p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  font-size: 0.875rem;
}

.data-points-section {
  margin-bottom: 1.5rem;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.7);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: #ef4444;
  text-align: center;
  margin: 0;
}

.data-points-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.75rem;
  max-height: 270px;
  overflow-y: scroll;
  overflow-x: hidden;
  padding-right: 0.25rem;
}

.data-points-grid::-webkit-scrollbar {
  width: 6px;
}

.data-points-grid::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.data-points-grid::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.data-points-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.data-point-button {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
  font-family: inherit;
}

.data-point-button:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.data-point-button.included {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.2);
  color: white;
}

.data-point-button.excluded {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  color: rgba(255, 255, 255, 0.4);
}

.data-point-button:not(.included):not(.excluded) {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  color: rgba(255, 255, 255, 0.4);
  cursor: default;
}

.data-point-value {
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1;
}

.data-point-date {
  font-size: 0.625rem;
  font-weight: 400;
  opacity: 0.8;
  line-height: 1;
}

.statistics-preview {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 0.875rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 400;
}

.stat-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: white;
}

.content-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.button-primary {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.button-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.button-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style> 