<template>
  <div class="quick-stats-card">
    <div class="stats-icon" :class="iconClass">
      <component :is="icon" class="icon" />
    </div>
    <div class="stats-content">
      <p class="stats-label">{{ label }}</p>
      <p class="stats-value">{{ value }}</p>
    </div>
  </div>
</template>

<script setup>
import { Heart, Activity, TrendingUp, Brain } from 'lucide-vue-next'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: [String, Object, Function],
    required: true
  },
  iconClass: {
    type: String,
    default: 'primary'
  }
})
</script>

<style scoped>
.quick-stats-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.quick-stats-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.quick-stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.stats-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stats-icon.primary {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.stats-icon.destructive {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.stats-icon.success {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.stats-icon.accent {
  background: rgba(168, 85, 247, 0.2);
  color: #a855f7;
}

.icon {
  width: 1.5rem;
  height: 1.5rem;
}

.stats-content {
  flex: 1;
}

.stats-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 0.25rem 0;
  font-weight: 500;
}

.stats-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  line-height: 1;
}
</style>
