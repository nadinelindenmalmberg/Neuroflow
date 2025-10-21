<template>
  <div class="integrated-metric-card">
    <div class="card-header">
      <div class="header-content">
        <h3 class="card-title">{{ title }}</h3>
        <div class="header-badges">
          <span v-if="category" class="category-badge" :class="getCategoryClass(category)">
            {{ category }}
          </span>
          <div class="source-badge">
            <component :is="sourceIcon" class="source-icon" />
            <span class="source-text">{{ source }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card-content">
      <div class="metric-display">
        <div class="value-section">
          <span class="metric-value">{{ value }}</span>
          <span v-if="unit" class="metric-unit">{{ unit }}</span>
        </div>
        
        <div v-if="trend" class="trend-section">
          <component :is="getTrendIcon(trend)" class="trend-icon" :class="getTrendClass(trend)" />
          <span v-if="trendValue" class="trend-value">{{ trendValue }}</span>
        </div>
      </div>
      
      <div v-if="lastUpdated" class="sync-info">
        <span class="sync-text">Synced {{ lastUpdated }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { TrendingUp, TrendingDown, Minus } from 'lucide-vue-next'

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
    default: ''
  },
  source: {
    type: String,
    required: true
  },
  sourceIcon: {
    type: [String, Object, Function],
    required: true
  },
  category: {
    type: String,
    default: '',
    validator: (value) => ['vital', 'fitness', 'mental', 'nutrition', ''].includes(value)
  }
})

function getTrendIcon(trend) {
  const icons = {
    up: TrendingUp,
    down: TrendingDown,
    stable: Minus
  }
  return icons[trend] || Minus
}

function getTrendClass(trend) {
  const classes = {
    up: 'trend-up',
    down: 'trend-down',
    stable: 'trend-stable'
  }
  return classes[trend] || 'trend-stable'
}

function getCategoryClass(category) {
  const classes = {
    vital: 'category-vital',
    fitness: 'category-fitness',
    mental: 'category-mental',
    nutrition: 'category-nutrition'
  }
  return classes[category] || ''
}
</script>

<style scoped>
.integrated-metric-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.integrated-metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, transparent 50%);
  pointer-events: none;
}

.integrated-metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.card-header {
  margin-bottom: 1rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  flex: 1;
}

.header-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.category-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid;
}

.category-vital {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.2);
}

.category-fitness {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.2);
}

.category-mental {
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
  border-color: rgba(168, 85, 247, 0.2);
}

.category-nutrition {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border-color: rgba(34, 197, 94, 0.2);
}

.source-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.375rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.source-icon {
  width: 1rem;
  height: 1rem;
  color: rgba(255, 255, 255, 0.6);
}

.source-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.card-content {
  space-y: 1rem;
}

.metric-display {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.75rem;
}

.value-section {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
}

.metric-unit {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.trend-section {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.trend-icon {
  width: 1rem;
  height: 1rem;
}

.trend-up {
  color: #22c55e;
}

.trend-down {
  color: #ef4444;
}

.trend-stable {
  color: rgba(255, 255, 255, 0.6);
}

.trend-value {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.sync-info {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 0.75rem;
}

.sync-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .header-badges {
    align-self: flex-end;
  }
  
  .metric-display {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
