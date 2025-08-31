<template>
  <div class="experiments-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <img :src="neuroflowLogo" alt="Neuroflow" class="sidebar-logo" />
        <span class="sidebar-title">Neuroflow</span>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/experiments" class="nav-link router-link-active">
          <FlaskConical class="nav-icon" size="20" />
          <span>Experiments</span>
        </router-link>
        <router-link to="/dashboard" class="nav-link">
          <BarChart3 class="nav-icon" size="20" />
          <span>Dashboard</span>
        </router-link>
        <router-link to="/explorer" class="nav-link">
          <Activity class="nav-icon" size="20" />
          <span>Explorer</span>
        </router-link>
        <router-link to="/integrations" class="nav-link">
          <GitBranch class="nav-icon" size="20" />
          <span>Integrations</span>
        </router-link>
        <router-link to="/upload" class="nav-link">
          <Upload class="nav-icon" size="20" />
          <span>Upload</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">Experiments</h1>
          <div class="header-actions">
            <button class="button" @click="showAddExperiment = true">
              + Add experiment
            </button>
          </div>
        </div>
      </div>

      <!-- Experiments Grid -->
      <div class="experiments-grid">
        <!-- Empty State -->
        <div v-if="experiments.length === 0" class="empty-state">
          <div class="empty-icon">
            <FlaskConical class="empty-icon-img" size="48" />
          </div>
          <h3 class="empty-title">No experiments created</h3>
        </div>

        <!-- Experiments Rows -->
        <div v-else class="experiments-rows">
          <div
            v-for="experiment in experiments"
            :key="experiment.id"
            class="experiment-container"
          >
            <div class="experiment-row" @click="toggleExpanded(experiment.id)">
              <div class="experiment-row-content">
                                                    <div class="experiment-main">
                    <div class="experiment-header">
                      <div class="experiment-icon">
                        <component 
                          :is="getIconComponent(experiment.icon || 'activity')" 
                          :size="20" 
                          :color="experiment.icon_color || '#3b82f6'"
                        />
                      </div>
                      <h3 class="experiment-title">{{ experiment.title }}</h3>
                    </div>
                  </div>
                  <div class="experiment-actions">
                    <div class="experiment-meta">
                      <span class="experiment-period">{{ experiment.period }}</span>
                      <span class="experiment-metric">{{ experiment.metric_of_interest }}</span>
                    </div>
                    <span 
                      class="status-label" 
                      :class="`status-${getExperimentStatus(experiment).status}`"
                    >
                      {{ getExperimentStatus(experiment).label }}
                    </span>
                    <button class="complete-button" @click.stop="completeExperiment(experiment)">
                      <Check class="complete-icon" :size="16" />
                    </button>
                    <button class="edit-button" @click.stop="editExperiment(experiment)">
                      <Edit class="edit-icon" :size="16" />
                    </button>
                    <button class="delete-button" @click.stop="deleteExperiment(experiment)">
                      <X class="delete-icon" :size="16" />
                    </button>
                    <button class="expand-button">
                      <ChevronRight 
                        v-if="!expandedExperiments.has(experiment.id)" 
                        class="chevron-icon" 
                        :size="20" 
                      />
                      <ChevronDown 
                        v-else 
                        class="chevron-icon" 
                        :size="20" 
                      />
                    </button>
                  </div>
              </div>
            </div>
            
            <!-- Expandable Details -->
            <div 
              v-if="expandedExperiments.has(experiment.id)" 
              class="experiment-details"
            >
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Start Date:</span>
                  <span class="detail-value">
                    {{ experiment.start_date ? formatDate(experiment.start_date) : 'Not set' }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">End Date:</span>
                  <span class="detail-value">
                    {{ experiment.end_date ? formatDate(experiment.end_date) : 'Not set' }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Improvement:</span>
                  <span class="detail-value" :class="getImprovementClass(experiment.id)">
                    {{ getImprovementText(experiment.id) }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Benchmark:</span>
                  <span class="detail-value">
                    {{ getBenchmarkText(experiment.id) }}
                  </span>
                </div>
              </div>
              
              <!-- Data Table Section -->
              <div class="data-table-section">
                <h4 class="table-title">Daily Data</h4>
                <div class="table-container">
                  <div class="table-scroll-container">
                    <table class="experiment-data-table">
                      <!-- Date Headers Row -->
                      <thead>
                        <tr class="date-headers">
                          <th class="table-header date-header"></th>
                          <th 
                            v-for="dataPoint in experimentTableData.get(experiment.id)?.table_data || []" 
                            :key="dataPoint.date"
                            class="table-header date-header"
                          >
                            {{ formatTableDate(dataPoint.date) }}
                          </th>
                        </tr>
                        <tr class="column-headers">
                          <th class="table-header column-header">Metric</th>
                          <th 
                            v-for="dataPoint in experimentTableData.get(experiment.id)?.table_data || []" 
                            :key="dataPoint.date"
                            class="table-header column-header"
                          >
                            <div class="header-columns">
                              <span class="header-value">Value</span>
                              <span class="header-benchmark">BM</span>
                              <span class="header-deviation">Δ</span>
                            </div>
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr class="data-row">
                          <td class="table-cell metric-name">
                            {{ experiment.metric_of_interest }}
                          </td>
                          <td 
                            v-for="dataPoint in experimentTableData.get(experiment.id)?.table_data || []" 
                            :key="dataPoint.date"
                            class="table-cell data-cell"
                          >
                            <div class="data-columns">
                              <span class="data-value" :class="{ 'no-data': !dataPoint.has_data }">
                                {{ dataPoint.has_data ? dataPoint.value?.toFixed(1) : '—' }}
                              </span>
                              <span class="data-benchmark">
                                {{ dataPoint.benchmark?.toFixed(1) || '—' }}
                              </span>
                              <span 
                                class="data-deviation" 
                                :class="{ 
                                  'positive': dataPoint.deviation > 0, 
                                  'negative': dataPoint.deviation < 0,
                                  'no-data': !dataPoint.has_data || dataPoint.deviation === null
                                }"
                              >
                                {{ dataPoint.deviation !== null ? (dataPoint.deviation > 0 ? '+' : '') + dataPoint.deviation.toFixed(1) : '—' }}
                              </span>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div v-if="tableLoading.get(experiment.id)" class="table-loading">
                  Loading data...
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add Experiment Modal -->
    <AddExperimentModal
      :is-visible="showAddExperiment"
      :available-metrics="availableMetrics"
      :editing-experiment="editingExperiment"
      @close="showAddExperiment = false; editingExperiment = null"
      @experiment-created="handleExperimentCreated"
      @experiment-updated="handleExperimentUpdated"
    />

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="modal-overlay">
      <div class="confirmation-modal">
        <div class="confirmation-header">
          <h3>Delete Experiment</h3>
        </div>
        <div class="confirmation-body">
          <p>Are you sure you want to delete <strong>"{{ experimentToDelete?.title }}"</strong>?</p>
          <p class="warning-text">This action cannot be undone.</p>
        </div>
        <div class="confirmation-actions">
          <button class="button-secondary" @click="cancelDelete">Cancel</button>
          <button class="button-danger" @click="confirmDelete">Delete</button>
        </div>
      </div>
    </div>

    <!-- Experiment Completion Modal -->
    <ExperimentCompletionModal
      :isVisible="showCompletionModal"
      :experiment="completingExperiment"
      @close="handleCompletionModalClose"
      @complete="handleExperimentCompleted"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute } from 'vue-router';
import { 
  FlaskConical, BarChart3, Activity, GitBranch, Upload, Filter, Edit, X, ChevronDown, ChevronRight, Check,
  // Common experiment icons
  Heart, Zap, Brain, Eye, Clock, Calendar, Timer, Watch,
  LineChart, PieChart, TrendingUp, TrendingDown, Target, Book, BookOpen,
  FileText, Home, Coffee, Moon, Sun, Lightbulb, Dumbbell, Mountain,
  Smartphone, Laptop, Headphones, Wifi, Battery, Apple,
  Cloud, CloudRain, Snowflake, Leaf, Flower, Briefcase,
  Building, Calculator, Pill, Plus, Users,
  User, MessageCircle, Phone, Mail, Bell, Car, Plane, Train,
  Smile, Frown, ThumbsUp, ThumbsDown, Star, Flag, Award, Gift, Key, Lock, Shield
} from "lucide-vue-next";
import AddExperimentModal from "./AddExperimentModal.vue";
import ExperimentCompletionModal from "./ExperimentCompletionModal.vue";
import neuroflowLogo from "../assets/images/ChatGPT_Image_Apr_5__2025__01_36_36_PM-removebg-preview 1.svg";

// Reactive state
const experiments = ref([]);
const showAddExperiment = ref(false);
const availableMetrics = ref([]);
const editingExperiment = ref(null);
const isLoading = ref(false);
const metricsLoaded = ref(false);
const showDeleteConfirmation = ref(false);
const experimentToDelete = ref(null);
const expandedExperiments = ref(new Set());
const experimentStats = ref(new Map());
const experimentTableData = ref(new Map()); // Store table data per experiment
const tableLoading = ref(new Map()); // Loading states per experiment
const showCompletionModal = ref(false);
const completingExperiment = ref(null);

// Empty experiments array - no placeholders
experiments.value = [];

// Fetch experiments and metrics from the API
onMounted(async () => {
  console.log('Experiments component mounted');
  await loadExperiments();
  await loadMetrics();
});

// Also reload when component becomes visible (route navigation)
const route = useRoute();
watch(() => route.path, async (newPath) => {
  if (newPath === '/experiments') {
    console.log('Navigated to experiments, reloading data');
    await loadExperiments();
  }
});

// Load experiments from API
async function loadExperiments() {
  if (isLoading.value) {
    console.log('Already loading experiments, skipping...');
    return;
  }
  
  try {
    isLoading.value = true;
    console.log('Loading experiments...');
    const experimentsResponse = await fetch('http://localhost:5174/api/experiments');
    const experimentsData = await experimentsResponse.json();
    experiments.value = experimentsData;
    console.log('Loaded experiments:', experimentsData);
  } catch (error) {
    console.error('Error fetching experiments:', error);
  } finally {
    isLoading.value = false;
  }
}

// Load metrics from API
async function loadMetrics() {
  if (metricsLoaded.value) {
    console.log('Metrics already loaded, skipping...');
    return;
  }
  
  try {
    console.log('Loading metrics...');
    const metricsResponse = await fetch('http://localhost:5174/api/metrics', {
      method: 'GET'
    });
    const metricsData = await metricsResponse.json();
    availableMetrics.value = metricsData.metrics || [];
    metricsLoaded.value = true;
    console.log('Loaded metrics:', availableMetrics.value.length, 'metrics');
  } catch (error) {
    console.error('Error fetching metrics:', error);
    // Fallback to some common metrics
    availableMetrics.value = [
      'average_heart_rate',
      'average_hrv',
      'total_sleep_duration',
      'deep_sleep_duration',
      'rem_sleep_duration',
      'awake_time',
      'average_breath'
    ];
    metricsLoaded.value = true;
  }
}

// Handle experiment creation
function handleExperimentCreated(experiment) {
  experiments.value.push(experiment);
  showAddExperiment.value = false;
}

// Handle experiment editing
function editExperiment(experiment) {
  editingExperiment.value = experiment;
  showAddExperiment.value = true;
}

// Handle experiment completion
function completeExperiment(experiment) {
  // Make sure all other modals are closed
  showAddExperiment.value = false;
  editingExperiment.value = null;
  showDeleteConfirmation.value = false;
  experimentToDelete.value = null;
  
  completingExperiment.value = experiment;
  showCompletionModal.value = true;
}

// Handle completion modal close
function handleCompletionModalClose() {
  showCompletionModal.value = false;
  completingExperiment.value = null;
}

// Handle experiment completed
async function handleExperimentCompleted(result) {
  console.log('Experiment completed:', result);
  
  // Refresh the experiments list to reflect the updated status
  await loadExperiments();
  
  // Close the modal
  handleCompletionModalClose();
}

// Handle experiment updates
async function handleExperimentUpdated(updatedExperiment) {
  const index = experiments.value.findIndex(exp => exp.id === updatedExperiment.id);
  if (index !== -1) {
    experiments.value[index] = updatedExperiment;
  }
  showAddExperiment.value = false;
  editingExperiment.value = null;
  
  // Refresh the full list to ensure we have latest data
  await loadExperiments();
}

// Handle experiment deletion
function deleteExperiment(experiment) {
  console.log('Delete function called for experiment:', experiment);
  experimentToDelete.value = experiment;
  showDeleteConfirmation.value = true;
}

// Confirm deletion
async function confirmDelete() {
  const experiment = experimentToDelete.value;
  if (!experiment) return;
  
  try {
    console.log('Sending DELETE request to:', `http://localhost:5174/api/experiments/${experiment.id}`);
    
    const response = await fetch(`http://localhost:5174/api/experiments/${experiment.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);
    
    if (response.ok) {
      console.log('Experiment deleted successfully, reloading experiments list');
      // Reload the experiments list to ensure we have fresh data
      await loadExperiments();
    } else {
      const errorText = await response.text();
      console.error('Response not ok:', errorText);
      throw new Error(`Failed to delete experiment: ${response.status}`);
    }
  } catch (error) {
    console.error('Error deleting experiment:', error);
    alert(`Failed to delete experiment: ${error.message}`);
  } finally {
    showDeleteConfirmation.value = false;
    experimentToDelete.value = null;
  }
}

// Cancel deletion
function cancelDelete() {
  showDeleteConfirmation.value = false;
  experimentToDelete.value = null;
}

// Toggle experiment expansion
function toggleExpanded(experimentId) {
  if (expandedExperiments.value.has(experimentId)) {
    expandedExperiments.value.delete(experimentId);
  } else {
    expandedExperiments.value.add(experimentId);
    // Fetch experiment stats when expanded
    fetchExperimentStats(experimentId);
    // Fetch table data when expanded
    fetchExperimentTableData(experimentId);
  }
}

// Fetch experiment table data
async function fetchExperimentTableData(experimentId) {
  // Check if we already have the data
  if (experimentTableData.value.has(experimentId)) {
    return;
  }
  
  try {
    tableLoading.value.set(experimentId, true);
    
    const response = await fetch(`http://localhost:5174/api/experiments/${experimentId}/table-data`);
    
    if (response.ok) {
      const data = await response.json();
      experimentTableData.value.set(experimentId, data);
    } else {
      console.error('Failed to fetch table data for experiment:', experimentId);
      experimentTableData.value.set(experimentId, { error: 'Failed to load data' });
    }
  } catch (error) {
    console.error('Error fetching experiment table data:', error);
    experimentTableData.value.set(experimentId, { error: 'Failed to load data' });
  } finally {
    tableLoading.value.set(experimentId, false);
  }
}

// Format date for display
function formatDate(dateString) {
  if (!dateString) return 'Not set';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
}

// Format date for table headers
function formatTableDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric' });
}

// Get improvement text
function getImprovementText(experimentId) {
  const stats = experimentStats.value.get(experimentId);
  if (!stats) return 'Loading...';
  if (stats.loading) return 'Loading...';
  if (stats.error) return 'N/A';
  
  if (stats.improvement_percentage !== null && stats.improvement_percentage !== undefined) {
    const sign = stats.improvement_percentage >= 0 ? '+' : '';
    return `${sign}${stats.improvement_percentage.toFixed(1)}%`;
  }
  
  // If no improvement data, show what we have
  if (stats.current_value !== null && stats.benchmark_value !== null) {
    return `${stats.current_value.toFixed(1)} vs ${stats.benchmark_value.toFixed(1)}`;
  }
  
  return 'N/A';
}

// Get benchmark text
function getBenchmarkText(experimentId) {
  const stats = experimentStats.value.get(experimentId);
  if (!stats) return 'Loading...';
  if (stats.loading) return 'Loading...';
  if (stats.error) return 'N/A';
  
  if (stats.benchmark_value !== null && stats.benchmark_value !== undefined) {
    const count = stats.data_points_count || 0;
    const pointText = count === 1 ? 'point' : 'points';
    return `${stats.benchmark_value.toFixed(1)} avg (${count} ${pointText})`;
  }
  
  // Show the period even if no data
  if (stats.benchmark_period) {
    return `No data for period`;
  }
  
  return 'N/A';
}

// Get experiment status
function getExperimentStatus(experiment) {
  if (!experiment.start_date || !experiment.end_date) {
    return { status: 'not-started', label: 'Not Started' };
  }
  
  const today = new Date().toISOString().split('T')[0];
  const startDate = experiment.start_date;
  const endDate = experiment.end_date;
  
  if (today < startDate) {
    return { status: 'not-started', label: 'Not Started' };
  } else if (today >= startDate && today <= endDate) {
    return { status: 'ongoing', label: 'Ongoing' };
  } else {
    return { status: 'completed', label: 'Completed' };
  }
}

// Get icon component for experiment
function getIconComponent(iconName) {
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

// Get CSS class for improvement text color
function getImprovementClass(experimentId) {
  const stats = experimentStats.value.get(experimentId);
  if (!stats || stats.loading || stats.error) return '';
  
  if (stats.improvement_percentage !== null && stats.improvement_percentage !== undefined) {
    if (stats.improvement_percentage > 0) return 'improvement-positive';
    if (stats.improvement_percentage < 0) return 'improvement-negative';
  }
  
  return '';
}

// Fetch experiment stats from API
async function fetchExperimentStats(experimentId) {
  try {
    experimentStats.value.set(experimentId, { loading: true });
    
    const response = await fetch(`http://localhost:5174/api/experiments/${experimentId}/stats`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.status}`);
    }
    
    const statsData = await response.json();
    experimentStats.value.set(experimentId, statsData);
    
    console.log(`Loaded stats for experiment ${experimentId}:`, statsData);
  } catch (error) {
    console.error('Error fetching experiment stats:', error);
    experimentStats.value.set(experimentId, { 
      error: error.message,
      benchmark_value: null,
      current_value: null,
      improvement_percentage: null,
      data_points_count: 0
    });
  }
}
</script>

<style scoped>
.experiments-layout {
  display: block;
  min-height: 100vh;
  background-color: #191a23;
  color: white;
}

/* Sidebar */
.sidebar {
  width: 15rem; /* Always expanded width */
  background-color: #16161d;
  border-right: 1px solid #2a2b38;
  display: flex;
  flex-direction: column;
  padding: 1rem 0.75rem;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  height: 100vh;
  overflow: hidden;
  z-index: 40;
  box-shadow: 4px 0 16px rgba(0, 0, 0, 0.3);
}

.sidebar-header {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.sidebar-logo {
  width: 30px;
  height: 30px;
  flex-shrink: 0;
}

.sidebar-title {
  margin-left: 0.75rem;
  opacity: 1;
  transform: translateX(0);
  font-size: 1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1.5rem;
  width: 100%;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.25rem;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: all 0.15s ease;
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
}

.nav-link span {
  opacity: 1;
  transform: translateX(0);
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 0.625rem;
  opacity: 0.7;
  color: currentColor;
  flex-shrink: 0;
}

.nav-link:hover .nav-icon,
.nav-link.router-link-active .nav-icon {
  opacity: 1;
}

/* Main content */
.main-content {
  flex: 1;
  padding: 1.25rem;
  overflow-y: auto;
  margin-left: 15rem; /* Match expanded sidebar width */
}

/* Page Header */
.page-header {
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 1.125rem;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.025em;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* Buttons */
.button {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  box-sizing: border-box;
}

.button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Experiments Grid */
.experiments-grid {
  min-height: 400px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120px 20px;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  background-color: rgba(255, 255, 255, 0.05);
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.empty-icon-img {
  width: 32px;
  height: 32px;
  color: rgba(255, 255, 255, 0.6);
}

.empty-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
}

/* Experiments Rows */
.experiments-rows {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.experiment-container {
  background: #191a24;
  backdrop-filter: blur(16px);
  border: 1.25px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.2s ease;
}

.experiment-container:hover {
  border-color: rgba(255, 255, 255, 0.2);
  background: #1f202b;
}

.experiment-row {
  padding: 1.5rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.experiment-row-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.experiment-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.experiment-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.experiment-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.experiment-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.experiment-title {
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
}

.experiment-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

/* Linear-style status labels */
.status-label {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: lowercase;
  letter-spacing: 0.025em;
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

.experiment-period,
.experiment-metric {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  padding: 0.25rem 0.75rem;
  background: transparent;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.complete-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.complete-button:hover {
  background: rgba(34, 197, 94, 0.1);
  color: rgba(34, 197, 94, 0.9);
}

.edit-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.edit-icon {
  color: currentColor;
}

.delete-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-button:hover {
  background: rgba(239, 68, 68, 0.1);
  color: rgba(239, 68, 68, 0.9);
}

.delete-icon {
  color: currentColor;
}

.expand-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.expand-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.chevron-icon {
  color: currentColor;
  transition: transform 0.2s ease;
}

/* Experiment Details */
.experiment-details {
  padding: 0 1.5rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  padding-top: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.improvement-positive {
  color: #10b981 !important;
}

.improvement-negative {
  color: #ef4444 !important;
}

/* Data Table Section */
.data-table-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  margin-left: -1.5rem;
  margin-right: -1.5rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.table-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
}

.table-container {
  overflow-x: auto;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: #16161d;
}

.table-scroll-container {
  min-width: 800px; /* Ensure a minimum width for scrolling */
}

.experiment-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.9);
}

.table-header {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.date-header {
  width: 100px; /* Fixed width for date headers */
  min-width: 100px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.column-header {
  width: 150px; /* Fixed width for column headers */
  min-width: 150px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.header-columns {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0;
  text-align: center;
  width: 100%;
}

.header-value,
.header-benchmark,
.header-deviation {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.data-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 0.75rem 1rem;
  text-align: left;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-cell:last-child {
  border-right: none;
}

.data-cell {
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  padding: 0.75rem 1rem;
}

.metric-name {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.data-columns {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0;
  text-align: center;
  width: 100%;
}

.data-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.data-value.no-data {
  color: rgba(255, 255, 255, 0.5);
}

.data-benchmark {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
}

.data-deviation {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.data-deviation.positive {
  color: #10b981;
}

.data-deviation.negative {
  color: #ef4444;
}

.data-deviation.no-data {
  color: rgba(255, 255, 255, 0.5);
}

.table-loading {
  padding: 0.75rem 1rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

/* Delete Confirmation Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.confirmation-modal {
  background: #191a24;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  width: 100%;
  max-width: 400px;
  margin: 1rem;
  overflow: hidden;
}

.confirmation-header {
  padding: 1.5rem 1.5rem 0;
}

.confirmation-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
}

.confirmation-body {
  padding: 1rem 1.5rem;
}

.confirmation-body p {
  margin: 0 0 0.5rem 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

.warning-text {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.5rem !important;
}

.confirmation-actions {
  padding: 0 1.5rem 1.5rem;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.button-secondary {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.button-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.button-danger {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #dc2626;
  border: 1px solid #dc2626;
  color: white;
}

.button-danger:hover {
  background: #b91c1c;
  border-color: #b91c1c;
}

/* Responsive Design */
@media (max-width: 768px) {
  .experiments-cards {
    grid-template-columns: 1fr;
  }
  
  .confirmation-modal {
    margin: 1rem;
  }
  
  .confirmation-actions {
    flex-direction: column;
  }
  
  .confirmation-actions button {
    width: 100%;
  }
  
  .experiment-actions {
    gap: 0.25rem;
  }
  
  .experiment-actions button {
    width: 28px;
    height: 28px;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .experiment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .experiment-meta {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
</style> 