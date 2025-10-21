<template>
  <div class="metric-card">
    <div class="metric-header">
      <h3 class="metric-title">{{ title }}</h3>
      <div class="metric-category" :class="category">
        <component :is="getCategoryIcon(category)" class="category-icon" />
      </div>
    </div>
    
    <div class="metric-content">
      <div class="metric-value">
        <span class="value">{{ value }}</span>
        <span class="unit">{{ unit }}</span>
      </div>
      
      <div class="metric-trend" :class="trend">
        <component :is="getTrendIcon(trend)" class="trend-icon" />
        <span class="trend-value">{{ trendValue }}</span>
      </div>
    </div>
    
    <div class="metric-footer">
      <span class="last-updated">Updated {{ lastUpdated }}</span>

    </div>
  </div>
</template>

<script setup>
import { Heart, Activity, Brain, Apple, TrendingUp, TrendingDown, Minus } from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  trend: {
    type: String,
    default: 'stable',
    validator: (value) => ['up', 'down', 'stable'].includes(value)
  },
  trendValue: {
    type: String,
    default: ''
  },
  lastUpdated: {
    type: String,
    required: true
  },
  category: {
    type: String,
    default: 'general',
    validator: (value) => ['fitness', 'vital', 'mental', 'general'].includes(value)
  }
})

function getCategoryIcon(category) {
  const icons = {
    fitness: Activity,
    vital: Heart,
    mental: Brain,
    general: Apple
  }
  return icons[category] || Apple
}

function getTrendIcon(trend) {
  const icons = {
    up: TrendingUp,
    down: TrendingDown,
    stable: Minus
  }
  return icons[trend] || Minus
}
</script>

<style scoped>
.metric-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, transparent 50%);
  pointer-events: none;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.metric-category {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-category.fitness {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.metric-category.vital {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.metric-category.mental {
  background: rgba(168, 85, 247, 0.2);
  color: #a855f7;
}

.metric-category.general {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.category-icon {
  width: 1rem;
  height: 1rem;
}

.metric-content {
  margin-bottom: 1rem;
}

.metric-value {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.value {
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
}

.unit {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.metric-trend.up {
  color: #22c55e;
}

.metric-trend.down {
  color: #ef4444;
}

.metric-trend.stable {
  color: rgba(255, 255, 255, 0.6);
}

.trend-icon {
  width: 0.875rem;
  height: 0.875rem;
}

.trend-value {
  font-weight: 600;
}

.metric-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 0.75rem;
}

.last-updated {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}
</style>
