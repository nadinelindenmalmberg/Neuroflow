<template>
  <transition name="modal-fade">
    <div v-if="isVisible" class="modal-overlay" @click="closeModal">
      <div class="modal-wrapper" @click.stop>
        <div class="modal-container">
          <!-- Header with gradient -->
          <div class="modal-header">
            <div class="header-content">
              <div class="header-icon">
                <component 
                  :is="getIconComponent(form.icon)" 
                  :size="24" 
                  :color="form.iconColor"
                />
              </div>
              <div class="header-text">
                <h2 class="modal-title">{{ editingExperiment ? 'Edit Experiment' : 'Create New Experiment' }}</h2>
                <p class="modal-subtitle">{{ editingExperiment ? 'Update your experiment details' : 'Track and analyze your health metrics' }}</p>
              </div>
            </div>
            <button class="close-button" @click="closeModal">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Progress indicator -->
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: formProgress + '%' }"></div>
            </div>
            <span class="progress-text">{{ Math.round(formProgress * 10) / 10 }}% Complete</span>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="modal-form">
            <!-- Basic Information Card -->
            <div class="form-card">
              <div class="card-header">
                <div class="card-icon">
                  <FileText :size="20" />
                </div>
                <div class="card-title">
                  <h3>Basic Information</h3>
                  <p>Give your experiment a name and description</p>
                </div>
              </div>
              <div class="card-content">
              
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">Experiment Title</span>
                  <span class="label-required">*</span>
                </label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <FileText :size="16" />
                  </div>
                  <input
                    v-model="form.title"
                    type="text"
                    class="form-input"
                    placeholder="e.g., Morning Heart Rate Optimization"
                    required
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">Description</span>
                  <span class="label-optional">(Optional)</span>
                </label>
                <div class="textarea-wrapper">
                  <div class="textarea-icon">
                    <MessageCircle :size="16" />
                  </div>
                  <textarea
                    v-model="form.description"
                    class="form-textarea"
                    placeholder="Describe what you're trying to achieve with this experiment..."
                    rows="3"
                  ></textarea>
                </div>
              </div>
              </div>
            </div>

            <!-- Visual Identity Card -->
            <div class="form-card">
              <div class="card-header">
                <div class="card-icon">
                  <Edit :size="20" />
                </div>
                <div class="card-title">
                  <h3>Visual Identity</h3>
                  <p>Choose an icon and color to represent your experiment</p>
                </div>
              </div>
              <div class="card-content">
              
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">Icon & Color</span>
                </label>
                <button 
                  type="button" 
                  class="icon-picker-button" 
                  @click="showIconPicker = true"
                >
                  <div class="icon-preview" v-if="form.icon">
                    <div class="icon-background" :style="{ backgroundColor: form.iconColor + '20' }">
                      <component 
                        :is="getIconComponent(form.icon)" 
                        :size="20" 
                        :color="form.iconColor"
                      />
                    </div>
                    <div class="icon-info">
                      <span class="icon-name">{{ form.icon.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) }}</span>
                      <div class="color-preview">
                        <div class="color-preview-circle" :style="{ backgroundColor: form.iconColor }"></div>
                        <span class="icon-color-code">{{ form.iconColor }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="icon-preview-empty" v-else>
                    <div class="empty-icon">
                      <Plus :size="20" />
                    </div>
                    <span>Choose icon & color</span>
                  </div>
                  <ChevronDown :size="16" class="chevron" />
                </button>
              </div>
              </div>
            </div>

            <!-- Metrics & Tracking Card -->
            <div class="form-card">
              <div class="card-header">
                <div class="card-icon">
                  <Target :size="20" />
                </div>
                <div class="card-title">
                  <h3>Metrics & Tracking</h3>
                  <p>Choose what you want to measure and compare</p>
                </div>
              </div>
              <div class="card-content">
              
              <!-- Step 1: Primary Metric -->
              <div class="metric-step">
                <div class="step-indicator">
                  <div class="step-number">1</div>
                  <div class="step-line"></div>
                </div>
                <div class="step-content">
                  <label class="form-label">
                    <span class="label-text">Primary Metric</span>
                    <span class="label-required">*</span>
                  </label>
                  <p class="step-description">Choose your main focus metric</p>
                  <select v-model="form.primaryMetricOfInterest" class="form-select" required>
                    <option value="">Select primary metric...</option>
                    <option v-for="metric in availableMetrics" :key="metric" :value="metric">
                      {{ formatMetricName(metric) }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Step 2: Secondary Metric -->
              <div class="metric-step">
                <div class="step-indicator">
                  <div class="step-number">2</div>
                  <div class="step-line"></div>
                </div>
                <div class="step-content">
                  <label class="form-label">
                    <span class="label-text">Secondary Metric</span>
                    <span class="label-optional">(Optional)</span>
                  </label>
                  <p class="step-description">Add an additional metric to track</p>
                  <select v-model="form.secondaryMetricOfInterest" class="form-select">
                    <option value="">Select secondary metric...</option>
                    <option v-for="metric in availableMetrics" :key="metric" :value="metric" :disabled="metric === form.primaryMetricOfInterest">
                      {{ formatMetricName(metric) }}{{ metric === form.primaryMetricOfInterest ? ' (Already selected as primary)' : '' }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Step 3: Benchmark -->
              <div class="metric-step">
                <div class="step-indicator">
                  <div class="step-number">3</div>
                </div>
                <div class="step-content">
                  <label class="form-label">
                    <span class="label-text">Benchmark Comparison</span>
                    <span class="label-required">*</span>
                  </label>
                  <p class="step-description">How do you want to compare your results?</p>
                  <select v-model="form.benchmark" class="form-select" required>
                    <option value="">Select benchmark comparison...</option>
                    <option v-for="benchmark in benchmarkOptions" :key="benchmark.value" :value="benchmark.value">
                      {{ benchmark.title }} - {{ benchmark.description }}
                    </option>
                  </select>
                </div>
              </div>
              </div>
            </div>

            <!-- Timeline & Configuration Card -->
            <div class="form-card">
              <div class="card-header">
                <div class="card-icon">
                  <Clock :size="20" />
                </div>
                <div class="card-title">
                  <h3>Timeline & Configuration</h3>
                  <p>Set the duration and context for your experiment</p>
                </div>
              </div>
              <div class="card-content">
              
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">Experiment Duration</span>
                  <span class="label-required">*</span>
                </label>
                <div class="duration-grid">
                  <button 
                    v-for="period in periodOptions" 
                    :key="period.value"
                    type="button"
                    class="duration-option"
                    :class="{ active: form.period === period.value }"
                    @click="form.period = period.value; calculateDates()"
                  >
                    <div class="duration-icon">
                      <component :is="period.icon" :size="16" />
                    </div>
                    <div class="duration-info">
                      <span class="duration-title">{{ period.title }}</span>
                      <span class="duration-desc">{{ period.description }}</span>
                    </div>
                  </button>
                </div>
              </div>

              <!-- Custom Dates (Only show for custom period) -->
              <div v-if="form.period === 'custom'" class="custom-dates">
                <div class="form-group-row">
                  <div class="form-group">
                    <label class="form-label">Start Date</label>
                    <div class="input-wrapper">
                      <div class="input-icon">
                        <Calendar :size="16" />
                      </div>
                      <input
                        v-model="form.startDate"
                        type="date"
                        class="form-input"
                        required
                      />
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="form-label">End Date</label>
                    <div class="input-wrapper">
                      <div class="input-icon">
                        <Calendar :size="16" />
                      </div>
                      <input
                        v-model="form.endDate"
                        type="date"
                        class="form-input"
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">Experiment Driver</span>
                  <span class="label-optional">(Optional)</span>
                </label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <Lightbulb :size="16" />
                  </div>
                  <input
                    v-model="form.driver"
                    type="text"
                    class="form-input"
                    placeholder="What's driving this experiment? (e.g., 'Improve sleep quality', 'Reduce stress')"
                  />
                </div>
                <p class="form-help">Describe the motivation or goal behind this experiment</p>
              </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="modal-actions">
              <button type="button" class="button-secondary" @click="closeModal">
                <X :size="16" />
                Cancel
              </button>
              <button type="submit" class="button-primary" :disabled="!isFormValid">
                <component :is="editingExperiment ? 'Edit' : 'Plus'" :size="16" />
                {{ editingExperiment ? 'Update Experiment' : 'Create Experiment' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </transition>

  <!-- Icon Picker Modal - Teleported to body -->
  <Teleport to="body">
    <IconPicker
      v-if="showIconPicker"
      :initialIcon="form.icon"
      :initialColor="form.iconColor"
      @close="showIconPicker = false"
      @select="handleIconSelect"
    />
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import { 
  X, ChevronDown, Activity, Plus, Edit,
  // All icons from IconPicker
  Heart, Zap, Brain, Eye, Clock, Calendar, Timer, Watch,
  BarChart3, LineChart, PieChart, TrendingUp, TrendingDown, Target,
  Book, BookOpen, FileText, Home, Coffee, Moon, Sun, Lightbulb,
  Dumbbell, Mountain, Smartphone, Laptop, Headphones, Wifi, Battery,
  Apple, Cloud, CloudRain, Snowflake, Leaf, Flower, Briefcase,
  Building, Calculator, Pill, Users, User, MessageCircle,
  Phone, Mail, Bell, Car, Plane, Train, FlaskConical, Smile,
  Frown, ThumbsUp, ThumbsDown, Star, Flag, Award, Gift, Key, Lock, Shield
} from 'lucide-vue-next';
import IconPicker from './IconPicker.vue';
import { experimentsApi, validators, errorHandler } from '../services/api.js';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  availableMetrics: {
    type: Array,
    default: () => []
  },
  editingExperiment: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'experiment-created', 'experiment-updated']);

// Form data
const form = ref({
  title: '',
  description: '',
  period: '1-week',
  startDate: '',
  endDate: '',
  driver: '',
  primaryMetricOfInterest: '',
  secondaryMetricOfInterest: '',
  benchmark: '',
  icon: 'activity',
  iconColor: '#3b82f6'
});

// Icon picker state
const showIconPicker = ref(false);

// Form progress calculation
const formProgress = computed(() => {
  const fields = [
    form.value.title,
    form.value.primaryMetricOfInterest,
    form.value.benchmark,
    form.value.period,
    form.value.startDate,
    form.value.endDate
  ];
  const filledFields = fields.filter(field => field && field.trim() !== '').length;
  return (filledFields / fields.length) * 100;
});

// Form validation
const isFormValid = computed(() => {
  return form.value.title && 
         form.value.primaryMetricOfInterest && 
         form.value.benchmark && 
         form.value.period &&
         form.value.startDate &&
         form.value.endDate;
});

// Benchmark options
const benchmarkOptions = [
  {
    value: 'avg-7-days',
    title: 'Last 7 Days',
    description: 'Compare to recent average',
    icon: 'TrendingUp'
  },
  {
    value: 'avg-30-days',
    title: 'Last 30 Days',
    description: 'Compare to monthly average',
    icon: 'BarChart3'
  },
  {
    value: 'avg-90-days',
    title: 'Last 90 Days',
    description: 'Compare to quarterly average',
    icon: 'LineChart'
  },
  {
    value: 'personal-best',
    title: 'Personal Best',
    description: 'Compare to your best performance',
    icon: 'Target'
  },
  {
    value: 'baseline',
    title: 'Baseline',
    description: 'Compare to starting point',
    icon: 'Flag'
  }
];

// Period options
const periodOptions = [
  {
    value: '1-week',
    title: '1 Week',
    description: 'Quick experiment',
    icon: 'Clock'
  },
  {
    value: '2-weeks',
    title: '2 Weeks',
    description: 'Short-term study',
    icon: 'Timer'
  },
  {
    value: '1-month',
    title: '1 Month',
    description: 'Comprehensive analysis',
    icon: 'Calendar'
  },
  {
    value: 'custom',
    title: 'Custom',
    description: 'Set your own dates',
    icon: 'Watch'
  }
];

// Format metric names for display
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

// Period to days mapping
const periodToDays = {
  '1-week': 7,
  '2-weeks': 14,
  '1-month': 30
};

// Calculate dates based on period
function calculateDates() {
  if (form.value.period === 'custom') {
    // Don't auto-calculate for custom period
    return;
  }
  
  const days = periodToDays[form.value.period];
  if (!days) return;
  
  // Start date is today
  const today = new Date();
  const startDate = today.toISOString().split('T')[0];
  
  // End date is start date + period days
  const endDate = new Date(today);
  endDate.setDate(today.getDate() + days);
  const endDateStr = endDate.toISOString().split('T')[0];
  
  form.value.startDate = startDate;
  form.value.endDate = endDateStr;
}

// Initialize dates on component mount
onMounted(() => {
  calculateDates();
});

// Watch for primary metric changes to clear secondary if it matches
watch(() => form.value.primaryMetricOfInterest, (newPrimary) => {
  if (newPrimary && form.value.secondaryMetricOfInterest === newPrimary) {
    form.value.secondaryMetricOfInterest = '';
  }
});

// Watch for editing experiment changes
watch(() => props.editingExperiment, (newExperiment) => {
  if (newExperiment) {
    // Populate form with experiment data
    form.value = {
      title: newExperiment.title || '',
      description: newExperiment.description || '',
      period: newExperiment.period || '1-week',
      startDate: newExperiment.start_date || '',
      endDate: newExperiment.end_date || '',
      driver: newExperiment.driver || '',
      primaryMetricOfInterest: newExperiment.primary_metric_of_interest || newExperiment.metric_of_interest || '',
      secondaryMetricOfInterest: newExperiment.secondary_metric_of_interest || '',
      benchmark: newExperiment.benchmark || '',
      icon: newExperiment.icon || 'activity',
      iconColor: newExperiment.icon_color || '#3b82f6'
    };
    // If editing and no dates, calculate them
    if (!newExperiment.start_date && !newExperiment.end_date) {
      calculateDates();
    }
  } else {
    resetForm();
  }
}, { immediate: true });

// Methods
function closeModal() {
  emit('close');
}

function resetForm() {
  form.value = {
    title: '',
    description: '',
    period: '1-week',
    startDate: '',
    endDate: '',
    driver: '',
    primaryMetricOfInterest: '',
    secondaryMetricOfInterest: '',
    benchmark: '',
    icon: 'activity',
    iconColor: '#3b82f6'
  };
  // Recalculate dates after reset
  calculateDates();
}

// Icon related functions
function handleIconSelect(selection) {
  form.value.icon = selection.icon;
  form.value.iconColor = selection.color;
  showIconPicker.value = false;
}

function getIconComponent(iconName) {
  // Same icon mapping as IconPicker
  const iconMap = {
    // Activity & Health
    'activity': Activity,
    'heart': Heart,
    'zap': Zap,
    'brain': Brain,
    'eye': Eye,
    
    // Time & Calendar
    'clock': Clock,
    'calendar': Calendar,
    'timer': Timer,
    'watch': Watch,
    
    // Charts & Analytics
    'bar-chart': BarChart3,
    'line-chart': LineChart,
    'pie-chart': PieChart,
    'trending-up': TrendingUp,
    'trending-down': TrendingDown,
    'target': Target,
    
    // Books & Learning
    'book': Book,
    'book-open': BookOpen,
    'file-text': FileText,
    
    // Home & Living
    'home': Home,
    'coffee': Coffee,
    'moon': Moon,
    'sun': Sun,
    'lightbulb': Lightbulb,
    
    // Sports & Fitness
    'dumbbell': Dumbbell,
    'mountain': Mountain,
    
    // Technology
    'smartphone': Smartphone,
    'laptop': Laptop,
    'headphones': Headphones,
    'wifi': Wifi,
    'battery': Battery,
    
    // Food & Drink
    'apple': Apple,
    
    // Weather & Nature
    'cloud': Cloud,
    'cloud-rain': CloudRain,
    'snowflake': Snowflake,
    'leaf': Leaf,
    'flower': Flower,
    
    // Work & Business
    'briefcase': Briefcase,
    'building': Building,
    'calculator': Calculator,
    
    // Health & Medical
    'pill': Pill,
    'plus': Plus,
    
    // Social & Communication
    'users': Users,
    'user': User,
    'message-circle': MessageCircle,
    'phone': Phone,
    'mail': Mail,
    'bell': Bell,
    
    // Transportation
    'car': Car,
    'plane': Plane,
    'train': Train,
    
    // Science & Lab
    'flask': FlaskConical,
    
    // Emotions & Mood
    'smile': Smile,
    'frown': Frown,
    'thumbs-up': ThumbsUp,
    'thumbs-down': ThumbsDown,
    
    // General
    'star': Star,
    'flag': Flag,
    'award': Award,
    'gift': Gift,
    'key': Key,
    'lock': Lock,
    'shield': Shield
  };
  
  return iconMap[iconName] || Activity;
}

async function handleSubmit() {
  const experimentData = {
    title: form.value.title,
    description: form.value.description,
    period: form.value.period,
    start_date: form.value.startDate,
    end_date: form.value.endDate,
    driver: form.value.driver,
    primary_metric_of_interest: form.value.primaryMetricOfInterest,
    secondary_metric_of_interest: form.value.secondaryMetricOfInterest || null,
    // Keep backward compatibility
    metric_of_interest: form.value.primaryMetricOfInterest,
    benchmark: form.value.benchmark,
    icon: form.value.icon,
    icon_color: form.value.iconColor
  };

  try {
    // Validate data before sending
    validators.experiment(experimentData);

    if (props.editingExperiment) {
      // Update existing experiment
      const result = await experimentsApi.update(props.editingExperiment.id, experimentData);
      
      if (result.success) {
        emit('experiment-updated', result.data);
        closeModal();
      } else {
        throw new Error(result.error || 'Failed to update experiment');
      }
    } else {
      // Create new experiment
      const result = await experimentsApi.create(experimentData);
      
      if (result.success) {
        emit('experiment-created', result.data);
        closeModal();
      } else {
        throw new Error(result.error || 'Failed to create experiment');
      }
    }
  } catch (error) {
    console.error('Error saving experiment:', error);
    errorHandler.showError('Failed to save experiment', error);
  }
}
</script>

<style scoped>
/* Clean Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1500;
}

.modal-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 20px;
}

.modal-container {
  background: rgba(25, 26, 36, 0.95);
  backdrop-filter: blur(16px);
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  position: relative;
}

/* Clean Header */
.modal-header {
  padding: 1.25rem 2rem 0.75rem 2rem;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
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
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  font-weight: 400;
}

.close-button {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
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

/* Progress Indicator */
.progress-container {
  padding: 0.75rem 2rem;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

/* Form Sections */
.modal-form {
  padding: 1.5rem 2rem;
  max-height: 70vh;
  overflow-y: auto;
}

/* Form Cards */
.form-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin-bottom: 1.5rem;
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.form-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1.25rem 1.5rem 0.875rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2));
  border-radius: 12px;
  color: #60a5fa;
  flex-shrink: 0;
}

.card-title h3 {
  font-size: 1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.02em;
}

.card-title p {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  line-height: 1.5;
  font-weight: 400;
}

.card-content {
  padding: 1.25rem 1.5rem;
}

/* Form Sections (Legacy - keeping for compatibility) */
.form-section {
  margin-bottom: 2.5rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title::before {
  content: '';
  width: 3px;
  height: 16px;
  background: #3b82f6;
  border-radius: 2px;
}

.section-description {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.5;
}

/* Enhanced Form Groups */
.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.5rem;
  letter-spacing: -0.01em;
}

.label-text {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.label-required {
  color: #ff6b6b;
  font-weight: 500;
  font-size: 0.875em;
}

.label-optional {
  color: rgba(255, 255, 255, 0.4);
  font-weight: 400;
  font-size: 0.875em;
}

/* Input Wrappers */
.input-wrapper,
.textarea-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 2.5rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.875rem;
  font-weight: 400;
  transition: all 0.15s ease;
  backdrop-filter: blur(8px);
  letter-spacing: -0.01em;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.form-input:hover,
.form-select:hover,
.form-textarea:hover {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input-icon,
.textarea-icon {
  position: absolute;
  left: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.4);
  pointer-events: none;
  z-index: 1;
}

.textarea-icon {
  top: 0.875rem;
  transform: none;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  padding-top: 0.875rem;
}

.form-help {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 0.5rem;
  margin-bottom: 0;
  line-height: 1.4;
}

/* Apple/Linear-Inspired Stepped Design */
.metric-step {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 1.75rem;
  position: relative;
  transition: all 0.2s ease;
}

.metric-step:last-child {
  margin-bottom: 0;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  width: 32px;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.step-line {
  width: 1px;
  height: 32px;
  background: rgba(255, 255, 255, 0.08);
  margin-top: 0.75rem;
  border-radius: 0.5px;
}

.metric-step:last-child .step-line {
  display: none;
}

.step-content {
  flex: 1;
  padding-top: 0.125rem;
}

.step-description {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0.375rem 0 1rem 0;
  line-height: 1.5;
  font-weight: 400;
}

/* Metrics Grid (Legacy) */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.metric-card:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.15);
}

.metric-card.primary {
  border-color: rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.05);
}

.metric-card.secondary {
  border-color: rgba(139, 92, 246, 0.3);
  background: rgba(139, 92, 246, 0.05);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
}

.metric-info {
  flex: 1;
}

.metric-description {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

/* Benchmark Grid */
.benchmark-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.benchmark-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.benchmark-option:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

.benchmark-option.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.2);
}

.benchmark-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
}

.benchmark-info {
  flex: 1;
}

.benchmark-title {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
}

.benchmark-desc {
  display: block;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Duration Grid */
.duration-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
}

.duration-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.duration-option:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

.duration-option.active {
  background: rgba(139, 92, 246, 0.1);
  border-color: #8b5cf6;
  box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.2);
}

.duration-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
}

.duration-info {
  flex: 1;
}

.duration-title {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
}

.duration-desc {
  display: block;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Custom Dates */
.custom-dates {
  margin-top: 1rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.form-group-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Enhanced Icon Picker */
.icon-picker-button {
  width: 100%;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.icon-picker-button:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

.icon-preview {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: white;
}

.icon-background {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.icon-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.icon-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
}

.color-preview {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-preview-circle {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.icon-color-code {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.icon-preview-empty {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

.empty-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed rgba(255, 255, 255, 0.2);
}

.chevron {
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.2s ease;
}

.icon-picker-button:hover .chevron {
  color: rgba(255, 255, 255, 0.8);
  transform: translateY(1px);
}

/* Enhanced Actions */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.button-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.button-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.button-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.button-primary:hover {
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
}

.button-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

/* Simple Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Responsive Design */
@media (max-width: 640px) {
  .modal-container {
    max-width: 95vw;
    margin: 1rem;
    border-radius: 16px;
  }
  
  .modal-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }
  
  .modal-form {
    padding: 1.5rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .benchmark-grid {
    grid-template-columns: 1fr;
  }
  
  .duration-grid {
    grid-template-columns: 1fr;
  }
  
  .form-group-row {
    grid-template-columns: 1fr;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .button-primary,
  .button-secondary {
    width: 100%;
    justify-content: center;
  }
}
</style> 