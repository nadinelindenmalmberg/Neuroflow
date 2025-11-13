<template>
  <transition name="modal-fade">
    <div v-if="isVisible" class="modal-overlay" @click="closeModal">
      <div class="modal-wrapper" @click.stop>
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-content">
              <div class="header-icon" :style="{ backgroundColor: experiment.icon_color + '20', borderColor: experiment.icon_color + '40' }">
                <component 
                  :is="getIconComponent(experiment.icon || 'activity')" 
                  :size="20" 
                  :color="experiment.icon_color || '#3b82f6'"
                />
              </div>
              <div class="header-text">
                <h2 class="modal-title">{{ experiment.title }}</h2>
                <p class="modal-subtitle">Experiment Analytics & Insights</p>
              </div>
            </div>
            <button class="close-button" @click="closeModal">
              <X :size="20" />
            </button>
          </div>

          <!-- Content -->
          <div class="modal-content">
            <!-- Experiment Title -->
            <div class="experiment-title-section">
              <h1 class="experiment-title">{{ experiment.title }}</h1>
              <p class="experiment-description" v-if="experiment.description">{{ experiment.description }}</p>
            </div>

            <!-- Experiment Overview -->
            <div class="overview-section">
              <div class="overview-grid">
                <div class="overview-item">
                  <div class="overview-label">Status</div>
                  <div class="overview-value">
                    <span class="status-badge" :class="`status-${experimentStatus}`">
                      {{ statusLabel }}
                    </span>
                  </div>
                </div>
                <div class="overview-item">
                  <div class="overview-label">Duration</div>
                  <div class="overview-value">{{ formatPeriod(experiment.period) }}</div>
                </div>
                <div class="overview-item">
                  <div class="overview-label">Benchmark</div>
                  <div class="overview-value">{{ formatBenchmark(experiment.benchmark) }}</div>
                </div>
                <div class="overview-item">
                  <div class="overview-label">Progress</div>
                  <div class="overview-value">{{ progressPercentage }}%</div>
                </div>
              </div>
            </div>

            <!-- Primary Metric Analytics -->
            <div class="analytics-section">
              <div class="section-header">
                <h3 class="section-title">Primary Metric: {{ formatMetricName(experiment.primary_metric_of_interest || experiment.metric_of_interest) }}</h3>
                <div class="section-subtitle">Performance against benchmark</div>
              </div>
              
              <div class="metric-analytics">
                <div class="metric-overview">
                  <div class="metric-stat">
                    <div class="stat-label">Current Value</div>
                    <div class="stat-value">{{ getCurrentValue(experiment.primary_metric_of_interest || experiment.metric_of_interest) }}</div>
                  </div>
                  <div class="metric-stat">
                    <div class="stat-label">Baseline</div>
                    <div class="stat-value">{{ getBaselineValue(experiment.primary_metric_of_interest || experiment.metric_of_interest) }}</div>
                  </div>
                  <div class="metric-stat">
                    <div class="stat-label">Improvement</div>
                    <div class="stat-value" :class="getImprovementClass(getImprovement(experiment.primary_metric_of_interest || experiment.metric_of_interest))">
                      {{ getImprovement(experiment.primary_metric_of_interest || experiment.metric_of_interest) }}
                    </div>
                  </div>
                </div>

                <!-- Daily Breakdown -->
                <div class="daily-breakdown">
                  <h4 class="breakdown-title">Daily Progress</h4>
                  <div class="breakdown-list">
                    <div 
                      v-for="(day, index) in getDailyData(experiment.primary_metric_of_interest || experiment.metric_of_interest)" 
                      :key="index"
                      class="breakdown-item"
                    >
                      <div class="day-info">
                        <span class="day-label">Day {{ index + 1 }}</span>
                        <span class="day-date">{{ formatDate(day.date) }}</span>
                      </div>
                      <div class="day-value">{{ day.value }}</div>
                      <div class="day-change" :class="day.change > 0 ? 'positive' : 'negative'">
                        {{ day.change > 0 ? '+' : '' }}{{ day.change }}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Secondary Metric (if exists) -->
            <div v-if="experiment.secondary_metric_of_interest" class="analytics-section">
              <div class="section-header">
                <h3 class="section-title">Secondary Metric: {{ formatMetricName(experiment.secondary_metric_of_interest) }}</h3>
                <div class="section-subtitle">Additional tracking data</div>
              </div>
              
              <div class="metric-analytics">
                <div class="metric-overview">
                  <div class="metric-stat">
                    <div class="stat-label">Current Value</div>
                    <div class="stat-value">{{ getCurrentValue(experiment.secondary_metric_of_interest) }}</div>
                  </div>
                  <div class="metric-stat">
                    <div class="stat-label">Baseline</div>
                    <div class="stat-value">{{ getBaselineValue(experiment.secondary_metric_of_interest) }}</div>
                  </div>
                  <div class="metric-stat">
                    <div class="stat-label">Change</div>
                    <div class="stat-value" :class="getImprovementClass(getImprovement(experiment.secondary_metric_of_interest))">
                      {{ getImprovement(experiment.secondary_metric_of_interest) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Insights Section -->
            <div class="insights-section">
              <div class="section-header">
                <h3 class="section-title">Key Insights</h3>
                <div class="section-subtitle">AI-powered analysis</div>
              </div>
              
              <div class="insights-list">
                <div class="insight-item">
                  <div class="insight-icon">📈</div>
                  <div class="insight-content">
                    <div class="insight-title">Best Performance Day</div>
                    <div class="insight-description">Day 6 showed the lowest heart rate at 71 bpm</div>
                  </div>
                </div>
                <div class="insight-item">
                  <div class="insight-icon">📊</div>
                  <div class="insight-content">
                    <div class="insight-title">Trend Analysis</div>
                    <div class="insight-description">Consistent improvement trend over 7 days</div>
                  </div>
                </div>
                <div class="insight-item">
                  <div class="insight-icon">🔗</div>
                  <div class="insight-content">
                    <div class="insight-title">Correlation</div>
                    <div class="insight-description">Sleep quality shows positive correlation (+0.3)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed } from 'vue';
import { X } from 'lucide-vue-next';
import { 
  Activity, Heart, Zap, Brain, Eye, Clock, Calendar, Timer, Watch,
  BarChart3, LineChart, PieChart, TrendingUp, TrendingDown, Target,
  Book, BookOpen, FileText, Home, Coffee, Moon, Sun, Lightbulb,
  Dumbbell, Mountain, Smartphone, Laptop, Headphones, Wifi, Battery,
  Apple, Cloud, CloudRain, Snowflake, Leaf, Flower, Briefcase,
  Building, Calculator, Pill, Users, User, MessageCircle,
  Phone, Mail, Bell, Car, Plane, Train, FlaskConical, Smile,
  Frown, ThumbsUp, ThumbsDown, Star, Flag, Award, Gift, Key, Lock, Shield
} from 'lucide-vue-next';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  experiment: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['close']);

// Computed properties
const experimentStatus = computed(() => {
  if (!props.experiment.start_date || !props.experiment.end_date) return 'not-started';
  
  const now = new Date();
  const start = new Date(props.experiment.start_date);
  const end = new Date(props.experiment.end_date);
  
  if (now < start) return 'not-started';
  if (now > end) return 'completed';
  return 'ongoing';
});

const statusLabel = computed(() => {
  const statusMap = {
    'not-started': 'Not Started',
    'ongoing': 'In Progress',
    'completed': 'Completed'
  };
  return statusMap[experimentStatus.value] || 'Unknown';
});

const progressPercentage = computed(() => {
  if (experimentStatus.value === 'not-started') return '0.00';
  if (experimentStatus.value === 'completed') return '100.00';
  
  const now = new Date();
  const start = new Date(props.experiment.start_date);
  const end = new Date(props.experiment.end_date);
  
  const total = end.getTime() - start.getTime();
  const elapsed = now.getTime() - start.getTime();
  
  const percentage = Math.min(Math.max((elapsed / total) * 100, 0), 100);
  return percentage.toFixed(2);
});

// Methods
function closeModal() {
  emit('close');
}

function formatMetricName(metricName) {
  const metricNames = {
    'average_heart_rate': 'Average Heart Rate',
    'average_hrv': 'Average HRV',
    'awake_time': 'Awake Time',
    'average_breath': 'Average Breath',
    'total_sleep_duration': 'Total Sleep',
    'deep_sleep_duration': 'Deep Sleep',
    'rem_sleep_duration': 'REM Sleep',
    'steps': 'Steps',
    'heart_rate': 'Heart Rate',
    'sleep': 'Sleep',
    'vo2_max': 'VO2 Max',
    'stress': 'Stress',
    'recovery': 'Recovery',
    'strain': 'Strain',
    'hrv': 'HRV',
    'respiratory_rate': 'Respiratory Rate'
  };
  return metricNames[metricName] || metricName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatPeriod(period) {
  const periodMap = {
    '1-week': '1 Week',
    '2-weeks': '2 Weeks',
    '1-month': '1 Month',
    'custom': 'Custom'
  };
  return periodMap[period] || period;
}

function formatBenchmark(benchmark) {
  const benchmarkMap = {
    'avg-7-days': 'Last 7 Days',
    'avg-30-days': 'Last 30 Days',
    'avg-90-days': 'Last 90 Days',
    'personal-best': 'Personal Best',
    'baseline': 'Baseline'
  };
  return benchmarkMap[benchmark] || benchmark;
}

function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function getIconComponent(iconName) {
  const iconMap = {
    'activity': Activity, 'heart': Heart, 'zap': Zap, 'brain': Brain, 'eye': Eye,
    'clock': Clock, 'calendar': Calendar, 'timer': Timer, 'watch': Watch,
    'bar-chart': BarChart3, 'line-chart': LineChart, 'pie-chart': PieChart,
    'trending-up': TrendingUp, 'trending-down': TrendingDown, 'target': Target,
    'book': Book, 'book-open': BookOpen, 'file-text': FileText, 'home': Home,
    'coffee': Coffee, 'moon': Moon, 'sun': Sun, 'lightbulb': Lightbulb,
    'dumbbell': Dumbbell, 'mountain': Mountain, 'smartphone': Smartphone,
    'laptop': Laptop, 'headphones': Headphones, 'wifi': Wifi, 'battery': Battery,
    'apple': Apple, 'cloud': Cloud, 'cloud-rain': CloudRain, 'snowflake': Snowflake,
    'leaf': Leaf, 'flower': Flower, 'briefcase': Briefcase, 'building': Building,
    'calculator': Calculator, 'pill': Pill, 'users': Users, 'user': User,
    'message-circle': MessageCircle, 'phone': Phone, 'mail': Mail, 'bell': Bell,
    'car': Car, 'plane': Plane, 'train': Train, 'flask': FlaskConical,
    'smile': Smile, 'frown': Frown, 'thumbs-up': ThumbsUp, 'thumbs-down': ThumbsDown,
    'star': Star, 'flag': Flag, 'award': Award, 'gift': Gift, 'key': Key,
    'lock': Lock, 'shield': Shield
  };
  return iconMap[iconName] || Activity;
}

// Mock data functions (replace with real API calls)
function getCurrentValue(metric) {
  const mockData = {
    'heart_rate': '72 bpm',
    'average_heart_rate': '72 bpm',
    'steps': '8,432',
    'total_sleep_duration': '7.2h',
    'sleep': '7.2h',
    'stress': 'Low',
    'recovery': '85%',
    'hrv': '42 ms'
  };
  return mockData[metric] || 'N/A';
}

function getBaselineValue(metric) {
  const mockData = {
    'heart_rate': '78 bpm',
    'average_heart_rate': '78 bpm',
    'steps': '7,200',
    'total_sleep_duration': '6.8h',
    'sleep': '6.8h',
    'stress': 'Medium',
    'recovery': '72%',
    'hrv': '38 ms'
  };
  return mockData[metric] || 'N/A';
}

function getImprovement(metric) {
  const mockData = {
    'heart_rate': '-7.7%',
    'average_heart_rate': '-7.7%',
    'steps': '+17.1%',
    'total_sleep_duration': '+5.9%',
    'sleep': '+5.9%',
    'stress': '-25%',
    'recovery': '+18.1%',
    'hrv': '+10.5%'
  };
  return mockData[metric] || '0%';
}

function getImprovementClass(improvement) {
  const value = parseFloat(improvement);
  if (value > 0) return 'positive';
  if (value < 0) return 'negative';
  return 'neutral';
}

function getDailyData(metric) {
  // Mock daily data
  const baseValue = metric === 'heart_rate' ? 78 : 7200;
  const improvement = metric === 'heart_rate' ? -1 : 200;
  
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    
    const value = baseValue + (improvement * i);
    const change = i === 0 ? 0 : ((value - baseValue) / baseValue) * 100;
    
    return {
      date: date.toISOString().split('T')[0],
      value: metric === 'heart_rate' ? `${Math.round(value)} bpm` : `${Math.round(value).toLocaleString()}`,
      change: Math.round(change * 10) / 10
    };
  });
}
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 20px;
}

.modal-container {
  display: flex;
  flex-direction: column;
  max-height: 90vh; /* modal never grows beyond viewport */
  background: rgba(25, 26, 36, 0.95);
  border-radius: 16px;
  overflow: hidden; /* 🔑 ensures header + body are part of same rounded box */
}

/* Header */
.modal-header {
  flex-shrink: 0; /* header never shrinks */
  padding: 1.25rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.modal-body {
  flex: 1;                /* take up remaining space */
  overflow-y: auto;        /* only body scrolls */
  padding: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  z-index: 2;
}

.header-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.header-text {
  flex: 1;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 500;
  margin: 0 0 0.125rem 0;
  color: white;
  letter-spacing: -0.02em;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  font-weight: 400;
}

.close-button {
  position: absolute;
  top: 1.25rem;
  right: 1.25rem;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* Content */
.modal-content {
  max-height: 600px;
  margin-top: 20px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.2) transparent; /* thumb / track */
  width: 100%;
}

.modal-content::-webkit-scrollbar {
  width: 6px;
}
.modal-content::-webkit-scrollbar-thumb {
  background-color: rgba(255,255,255,0.2);
  border-radius: 3px;
}
.modal-content::-webkit-scrollbar-track {
  background: transparent;
}

/* Experiment Title Section */
.experiment-title-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.experiment-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.02em;
  line-height: 1.3;
}

.experiment-description {
  font-size: 0.9375rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  line-height: 1.5;
  font-weight: 400;
}


/* Overview Section */
.overview-section {
  margin-bottom: 2rem;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.overview-item {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 1rem;
}

.overview-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.overview-value {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-ongoing {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.status-completed {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-not-started {
  background: rgba(107, 114, 128, 0.2);
  color: #9ca3af;
  border: 1px solid rgba(107, 114, 128, 0.3);
}

/* Analytics Section */
.analytics-section {
  margin-bottom: 2rem;
}

.section-header {
  margin-bottom: 1.25rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.01em;
}

.section-subtitle {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.metric-analytics {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1.5rem;
}

.metric-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.metric-stat {
  text-align: center;
}

.stat-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.stat-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.stat-value.positive {
  color: #10b981;
}

.stat-value.negative {
  color: #ef4444;
}

/* Daily Breakdown */
.daily-breakdown {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 1.5rem;
}

.breakdown-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 1rem 0;
}

.breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.breakdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.day-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.day-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.day-date {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.8);
}

.day-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.day-change {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.day-change.positive {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.day-change.negative {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Insights Section */
.insights-section {
  margin-bottom: 1rem;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.insight-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.25rem;
}

.insight-description {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.4;
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

/* Responsive */
@media (max-width: 640px) {
  .modal-container {
    max-width: 95vw;
    margin: 1rem;
  }
  
  .modal-header {
    padding: 1.25rem 1.5rem 0.75rem 1.5rem;
  }
  
  .modal-content {
    padding: 1.25rem 1.5rem;
  }
  
  .overview-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .metric-overview {
    grid-template-columns: 1fr;
  }
}
</style>
