<template>
  <transition name="modal-fade">
    <div v-if="isVisible" class="modal-overlay" @click="closeModal">
      <div class="modal-wrapper" @click.stop>
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <h2 class="modal-title">{{ editingExperiment ? 'Edit Experiment' : 'Add Experiment' }}</h2>
            <button class="close-button" @click="closeModal">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="modal-form">
            <!-- Title -->
            <div class="form-group">
              <label class="form-label">Title</label>
              <input
                v-model="form.title"
                type="text"
                class="form-input"
                placeholder="Experiment title"
                required
              />
            </div>

            <!-- Description -->
            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea
                v-model="form.description"
                class="form-textarea"
                placeholder="Add a short summary..."
                rows="3"
              ></textarea>
            </div>

            <!-- Icon & Color -->
            <div class="form-group">
              <label class="form-label">Icon & Color</label>
              <button 
                type="button" 
                class="icon-picker-button" 
                @click="showIconPicker = true"
              >
                <div class="icon-preview" v-if="form.icon">
                  <component 
                    :is="getIconComponent(form.icon)" 
                    :size="20" 
                    :color="form.iconColor"
                  />
                </div>
                <div class="icon-preview-empty" v-else>
                  <span>Choose icon</span>
                </div>
                <ChevronDown :size="16" class="chevron" />
              </button>
            </div>

            <!-- Period -->
            <div class="form-group">
              <label class="form-label">Period</label>
              <select v-model="form.period" @change="calculateDates" class="form-select">
                <option value="1-week">1 week</option>
                <option value="2-weeks">2 weeks</option>
                <option value="1-month">1 month</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            <!-- Custom Dates (Only show for custom period) -->
            <div v-if="form.period === 'custom'" class="form-group-row">
              <div class="form-group">
                <label class="form-label">Start Date</label>
                <input
                  v-model="form.startDate"
                  type="date"
                  class="form-input"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">End Date</label>
                <input
                  v-model="form.endDate"
                  type="date"
                  class="form-input"
                  required
                />
              </div>
            </div>

            <!-- Driver -->
            <div class="form-group">
              <label class="form-label">Driver</label>
              <input
                v-model="form.driver"
                type="text"
                class="form-input"
                placeholder="What drives this experiment?"
              />
            </div>

            <!-- Metric of Interest -->
            <div class="form-group">
              <label class="form-label">Metric of Interest</label>
              <select v-model="form.metricOfInterest" class="form-select" required>
                <option value="">Select a metric</option>
                <option v-for="metric in availableMetrics" :key="metric" :value="metric">
                  {{ metric }}
                </option>
              </select>
            </div>

            <!-- Benchmark -->
            <div class="form-group">
              <label class="form-label">Benchmark</label>
              <select v-model="form.benchmark" class="form-select" required>
                <option value="">Select benchmark</option>
                <option value="avg-7-days">Average last 7 days</option>
                <option value="avg-30-days">Average last 30 days</option>
                <option value="avg-90-days">Average last 90 days</option>
                <option value="personal-best">Personal best</option>
                <option value="baseline">Baseline</option>
              </select>
            </div>

            <!-- Actions -->
            <div class="modal-actions">
              <button type="button" class="button-secondary" @click="closeModal">
                Cancel
              </button>
              <button type="submit" class="button-primary">
                {{ editingExperiment ? 'Update Experiment' : 'Create Experiment' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </transition>

  <!-- Icon Picker Modal -->
  <IconPicker
    v-if="showIconPicker"
    :initialIcon="form.icon"
    :initialColor="form.iconColor"
    @close="showIconPicker = false"
    @select="handleIconSelect"
  />
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { 
  X, ChevronDown, Activity,
  // All icons from IconPicker
  Heart, Zap, Brain, Eye, Clock, Calendar, Timer, Watch,
  BarChart3, LineChart, PieChart, TrendingUp, TrendingDown, Target,
  Book, BookOpen, FileText, Home, Coffee, Moon, Sun, Lightbulb,
  Dumbbell, Mountain, Smartphone, Laptop, Headphones, Wifi, Battery,
  Apple, Cloud, CloudRain, Snowflake, Leaf, Flower, Briefcase,
  Building, Calculator, Pill, Plus, Users, User, MessageCircle,
  Phone, Mail, Bell, Car, Plane, Train, FlaskConical, Smile,
  Frown, ThumbsUp, ThumbsDown, Star, Flag, Award, Gift, Key, Lock, Shield
} from 'lucide-vue-next';
import IconPicker from './IconPicker.vue';

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
  metricOfInterest: '',
  benchmark: '',
  icon: 'activity',
  iconColor: '#3b82f6'
});

// Icon picker state
const showIconPicker = ref(false);

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
      metricOfInterest: newExperiment.metric_of_interest || '',
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
    metricOfInterest: '',
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
    metric_of_interest: form.value.metricOfInterest,
    benchmark: form.value.benchmark,
    icon: form.value.icon,
    icon_color: form.value.iconColor
  };

  try {
    if (props.editingExperiment) {
      // Update existing experiment
      const response = await fetch(`http://localhost:5174/api/experiments/${props.editingExperiment.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(experimentData)
      });
      
      if (response.ok) {
        const result = await response.json();
        emit('experiment-updated', result.experiment);
      } else {
        throw new Error('Failed to update experiment');
      }
    } else {
      // Create new experiment
      const response = await fetch('http://localhost:5174/api/experiments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(experimentData)
      });
      
      if (response.ok) {
        const result = await response.json();
        emit('experiment-created', result.experiment);
      } else {
        throw new Error('Failed to create experiment');
      }
    }
    
    closeModal();
  } catch (error) {
    console.error('Error saving experiment:', error);
    // You might want to show an error message to the user here
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
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(2px);
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
  background-color: #1f202b;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  border-radius: 0.75rem;
  border: 1.5px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 0 1.5rem;
  margin-bottom: 1rem;
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
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.modal-form {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.5rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background-color: rgba(255, 255, 255, 0.08);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.button-secondary {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.button-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
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

.button-primary:hover {
  background-color: #2563eb;
}

/* Icon Picker Button */
.icon-picker-button {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-picker-button:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.icon-preview {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
}

.icon-preview-empty {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

.chevron {
  color: rgba(255, 255, 255, 0.5);
  transition: transform 0.2s ease;
}

.icon-picker-button:hover .chevron {
  color: rgba(255, 255, 255, 0.8);
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