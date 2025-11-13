<template>
  <div class="experiment-card" :class="{ 'completed': status === 'completed' }">
    <!-- Card Header -->
    <div class="card-header">
      <div class="experiment-icon" :style="{ backgroundColor: experiment.icon_color + '20', borderColor: experiment.icon_color + '40' }">
        <component 
          :is="getIconComponent(experiment.icon || 'activity')" 
          :size="24" 
          :color="experiment.icon_color || '#3b82f6'"
        />
      </div>
      <div class="experiment-info">
        <h3 class="experiment-title">{{ experiment.title }}</h3>
        <p class="experiment-description" v-if="experiment.description">{{ experiment.description }}</p>
      </div>
      <div class="experiment-status">
        <span class="status-badge" :class="`status-${status}`">
          {{ statusLabel }}
        </span>
      </div>
    </div>

    <!-- Card Content -->
    <div class="card-content">
      <div class="experiment-metrics">
        <div class="metric-item">
          <span class="metric-label">Metric</span>
          <span class="metric-value">{{ formatMetricName(experiment.metric_of_interest) }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">Period</span>
          <span class="metric-value">{{ formatPeriod(experiment.period) }}</span>
        </div>
        <div class="metric-item" v-if="experiment.driver">
          <span class="metric-label">Driver</span>
          <span class="metric-value">{{ experiment.driver }}</span>
        </div>
      </div>

      <!-- Progress Bar for Ongoing Experiments -->
      <div v-if="status === 'ongoing'" class="progress-section">
        <div class="progress-header">
          <span class="progress-label">Progress</span>
          <span class="progress-percentage">{{ progressPercentage }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <div class="progress-dates">
          <span class="start-date">{{ formatDate(experiment.start_date) }}</span>
          <span class="end-date">{{ formatDate(experiment.end_date) }}</span>
        </div>
      </div>

      <!-- Results for Completed Experiments -->
      <div v-if="status === 'completed' && stats" class="results-section">
        <div class="result-item">
          <span class="result-label">Improvement</span>
          <span class="result-value" :class="getImprovementClass(stats.improvement_percentage)">
            {{ formatImprovement(stats.improvement_percentage) }}
          </span>
        </div>
        <div class="result-item">
          <span class="result-label">Benchmark</span>
          <span class="result-value">{{ stats.benchmark_value?.toFixed(1) || 'N/A' }}</span>
        </div>
      </div>
    </div>

    <!-- Card Actions -->
    <div class="card-actions">
      <button 
        v-if="status === 'ongoing'" 
        class="action-button complete-button"
        @click="$emit('complete', experiment)"
        title="Complete Experiment"
      >
        <Check :size="16" />
        Complete
      </button>
      
      <button 
        class="action-button view-button"
        @click="$emit('view', experiment)"
        title="View Details"
      >
        <Eye :size="16" />
        View
      </button>
      
      <button 
        class="action-button edit-button"
        @click="$emit('edit', experiment)"
        title="Edit Experiment"
      >
        <Edit :size="16" />
        Edit
      </button>
      
      <button 
        class="action-button delete-button"
        @click="$emit('delete', experiment)"
        title="Delete Experiment"
      >
        <Trash2 :size="16" />
        Delete
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Check, Eye, Edit, Trash2, Activity,
  // All experiment icons
  Heart, Zap, Brain, Clock, Calendar, Timer, Watch,
  BarChart3, LineChart, PieChart, TrendingUp, TrendingDown, Target,
  Book, BookOpen, FileText, Home, Coffee, Moon, Sun, Lightbulb,
  Dumbbell, Mountain, Smartphone, Laptop, Headphones, Wifi, Battery,
  Apple, Cloud, CloudRain, Snowflake, Leaf, Flower, Briefcase,
  Building, Calculator, Pill, Plus, Users, User, MessageCircle,
  Phone, Mail, Bell, Car, Plane, Train, FlaskConical, Smile,
  Frown, ThumbsUp, ThumbsDown, Star, Flag, Award, Gift, Key, Lock, Shield
} from 'lucide-vue-next'

const props = defineProps({
  experiment: {
    type: Object,
    required: true
  },
  stats: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['complete', 'view', 'edit', 'delete'])

// Computed properties
const status = computed(() => {
  if (!props.experiment.start_date || !props.experiment.end_date) {
    return 'not-started'
  }
  
  const today = new Date().toISOString().split('T')[0]
  const startDate = props.experiment.start_date
  const endDate = props.experiment.end_date
  
  if (today < startDate) {
    return 'not-started'
  } else if (today >= startDate && today <= endDate) {
    return 'ongoing'
  } else {
    return 'completed'
  }
})

const statusLabel = computed(() => {
  switch (status.value) {
    case 'not-started': return 'Not Started'
    case 'ongoing': return 'Ongoing'
    case 'completed': return 'Completed'
    default: return 'Unknown'
  }
})

const progressPercentage = computed(() => {
  if (status.value !== 'ongoing') return 0
  
  const start = new Date(props.experiment.start_date)
  const end = new Date(props.experiment.end_date)
  const today = new Date()
  
  const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
  const elapsedDays = Math.ceil((today - start) / (1000 * 60 * 60 * 24))
  
  const percentage = Math.min(Math.max((elapsedDays / totalDays) * 100, 0), 100)
  return percentage.toFixed(2)
})

// Helper functions
function formatMetricName(metricName) {
  if (!metricName) return 'Unknown'
  
  const exceptions = { hrv: "HRV", vo2: "VO2", rem: "REM" }
  let formatted = metricName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  
  Object.entries(exceptions).forEach(([key, value]) => {
    const regex = new RegExp(`\\b${key}\\b`, 'gi')
    formatted = formatted.replace(regex, value)
  })
  
  return formatted
}

function formatPeriod(period) {
  const periodMap = {
    '1-week': '1 Week',
    '2-weeks': '2 Weeks', 
    '1-month': '1 Month',
    'custom': 'Custom'
  }
  return periodMap[period] || period
}

function formatDate(dateString) {
  if (!dateString) return 'Not set'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric' 
  })
}

function formatImprovement(percentage) {
  if (percentage === null || percentage === undefined) return 'N/A'
  const sign = percentage >= 0 ? '+' : ''
  return `${sign}${percentage.toFixed(1)}%`
}

function getImprovementClass(percentage) {
  if (percentage === null || percentage === undefined) return ''
  if (percentage > 0) return 'improvement-positive'
  if (percentage < 0) return 'improvement-negative'
  return ''
}

function getIconComponent(iconName) {
  const iconMap = {
    'activity': Activity, 'heart': Heart, 'zap': Zap, 'brain': Brain, 'eye': Eye,
    'clock': Clock, 'calendar': Calendar, 'timer': Timer, 'watch': Watch,
    'bar-chart': BarChart3, 'line-chart': LineChart, 'pie-chart': PieChart,
    'trending-up': TrendingUp, 'trending-down': TrendingDown, 'target': Target,
    'book': Book, 'book-open': BookOpen, 'file-text': FileText,
    'home': Home, 'coffee': Coffee, 'moon': Moon, 'sun': Sun, 'lightbulb': Lightbulb,
    'dumbbell': Dumbbell, 'mountain': Mountain, 'smartphone': Smartphone,
    'laptop': Laptop, 'headphones': Headphones, 'wifi': Wifi, 'battery': Battery,
    'apple': Apple, 'cloud': Cloud, 'cloud-rain': CloudRain, 'snowflake': Snowflake,
    'leaf': Leaf, 'flower': Flower, 'briefcase': Briefcase, 'building': Building,
    'calculator': Calculator, 'pill': Pill, 'plus': Plus, 'users': Users,
    'user': User, 'message-circle': MessageCircle, 'phone': Phone, 'mail': Mail,
    'bell': Bell, 'car': Car, 'plane': Plane, 'train': Train, 'flask': FlaskConical,
    'smile': Smile, 'frown': Frown, 'thumbs-up': ThumbsUp, 'thumbs-down': ThumbsDown,
    'star': Star, 'flag': Flag, 'award': Award, 'gift': Gift, 'key': Key,
    'lock': Lock, 'shield': Shield
  }
  return iconMap[iconName] || Activity
}
</script>

<style scoped>
.experiment-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.experiment-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.experiment-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.experiment-card:hover::before {
  opacity: 1;
}

.experiment-card.completed {
  border-color: rgba(34, 197, 94, 0.3);
}

.experiment-card.completed::before {
  background: linear-gradient(90deg, #10b981, #34d399);
  opacity: 1;
}

/* Card Header */
.card-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.experiment-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid;
  flex-shrink: 0;
}

.experiment-info {
  flex: 1;
  min-width: 0;
}

.experiment-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 0.25rem 0;
  line-height: 1.4;
}

.experiment-description {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.experiment-status {
  flex-shrink: 0;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid;
}

.status-not-started {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.status-ongoing {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}

.status-completed {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #86efac;
}

/* Card Content */
.card-content {
  margin-bottom: 1.5rem;
}

.experiment-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

/* Progress Section */
.progress-section {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.progress-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.progress-percentage {
  font-size: 0.875rem;
  font-weight: 600;
  color: #fbbf24;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-dates {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

/* Results Section */
.results-section {
  background: rgba(34, 197, 94, 0.05);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid rgba(34, 197, 94, 0.1);
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.result-item:last-child {
  margin-bottom: 0;
}

.result-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.result-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.improvement-positive {
  color: #10b981 !important;
}

.improvement-negative {
  color: #ef4444 !important;
}

/* Card Actions */
.card-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  background: transparent;
}

.complete-button {
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.3);
}

.complete-button:hover {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.5);
}

.view-button {
  color: rgba(255, 255, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.2);
}

.view-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.edit-button {
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.3);
}

.edit-button:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.5);
}

.delete-button {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

.delete-button:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.5);
}

/* Responsive Design */
@media (max-width: 768px) {
  .experiment-card {
    padding: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .experiment-metrics {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .action-button {
    justify-content: center;
  }
}
</style>

