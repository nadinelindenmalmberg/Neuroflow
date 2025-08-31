<template>
  <div class="icon-picker-overlay" @click="closeModal">
    <div class="icon-picker-modal" @click.stop>
      <div class="icon-picker-header">
        <h3>Choose Icon & Color</h3>
        <button class="close-button" @click="closeModal">
          <X :size="20" />
        </button>
      </div>
      
      <!-- Icon Grid with Colors -->
      <div class="content-section">
        <!-- Color Palette -->
        <div class="color-row">
          <button
            v-for="color in colors"
            :key="color"
            class="color-circle"
            :class="{ active: selectedColor === color }"
            :style="{ backgroundColor: color }"
            @click="selectedColor = color"
          >
            <Check v-if="selectedColor === color" :size="12" color="white" />
          </button>
        </div>

        <!-- Icon Grid -->
        <div class="icon-grid">
          <button
            v-for="iconName in allIcons"
            :key="iconName"
            class="icon-option"
            :class="{ active: selectedIcon === iconName }"
            @click="selectedIcon = iconName"
          >
            <component 
              :is="getIconComponent(iconName)" 
              :size="16" 
              :color="selectedColor"
            />
          </button>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-section">
        <button class="cancel-button" @click="closeModal">Cancel</button>
        <button class="confirm-button" @click="confirmSelection" :disabled="!selectedIcon">
          Confirm
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  X, Check,
  // Activity & Health
  Activity, Heart, Zap, Brain, Eye,
  // Time & Calendar
  Clock, Calendar, Timer, Watch,
  // Charts & Analytics
  BarChart3, LineChart, PieChart, TrendingUp, TrendingDown, Target,
  // Books & Learning
  Book, BookOpen, FileText,
  // Home & Living
  Home, Coffee, Moon, Sun, Lightbulb,
  // Sports & Fitness
  Dumbbell, Mountain,
  // Technology
  Smartphone, Laptop, Headphones, Wifi, Battery,
  // Food & Drink
  Apple,
  // Weather & Nature
  Cloud, CloudRain, Snowflake, Leaf, Flower,
  // Work & Business
  Briefcase, Building, Calculator,
  // Health & Medical
  Pill, Plus,
  // Social & Communication
  Users, User, MessageCircle, Phone, Mail, Bell,
  // Transportation
  Car, Plane, Train,
  // Science & Lab
  FlaskConical,
  // Emotions & Mood
  Smile, Frown, ThumbsUp, ThumbsDown,
  // General
  Star, Flag, Award, Gift, Key, Lock, Shield
} from 'lucide-vue-next';

const props = defineProps({
  initialIcon: String,
  initialColor: String
});

const emit = defineEmits(['close', 'select']);

// Color palette
const colors = ref([
  '#6b7280', // Gray
  '#3b82f6', // Blue  
  '#06b6d4', // Cyan
  '#10b981', // Green
  '#f59e0b', // Yellow
  '#f97316', // Orange
  '#ef4444', // Red
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#84cc16'  // Lime
]);

// Icon mapping
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

const selectedIcon = ref(props.initialIcon || 'activity');
const selectedColor = ref(props.initialColor || '#3b82f6');

const allIcons = Object.keys(iconMap);

function getIconComponent(iconName) {
  return iconMap[iconName] || Activity;
}

function closeModal() {
  emit('close');
}

function confirmSelection() {
  if (selectedIcon.value) {
    emit('select', {
      icon: selectedIcon.value,
      color: selectedColor.value
    });
  }
}
</script>

<style scoped>
.icon-picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.icon-picker-modal {
  background: #1f1f2e;
  border-radius: 8px;
  width: 420px;
  max-width: 90vw;
  max-height: 70vh;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.icon-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.icon-picker-header h3 {
  margin: 0;
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
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

.content-section {
  padding: 1rem 1.25rem;
}

.color-row {
  display: flex;
  gap: 0.375rem;
  margin-bottom: 1rem;
  justify-content: center;
}

.color-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.color-circle.active {
  border-color: rgba(255, 255, 255, 0.8);
  transform: scale(1.1);
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  max-height: 220px;
  overflow-y: auto;
}

.icon-option {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.icon-option:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-option.active {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.4);
}

.actions-section {
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.cancel-button,
.confirm-button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
}

.cancel-button:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.confirm-button {
  background: #3b82f6;
  border: 1px solid #3b82f6;
  color: white;
}

.confirm-button:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
}

.confirm-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 