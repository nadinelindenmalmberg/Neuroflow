<template>
  <div class="experiments-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">Experiments</h1>
          <p class="hero-subtitle">Track and analyze your health experiments with data-driven insights</p>
        </div>
        <div class="hero-actions">
          <button class="hero-button" @click="showAddExperiment = true">
            <Plus :size="20" />
            New Experiment
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Quick Stats -->
      <div class="quick-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <FlaskConical :size="24" color="#3b82f6" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ experiments.length }}</div>
            <div class="stat-label">Total Experiments</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <TrendingUp :size="24" color="#10b981" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ ongoingExperiments.length }}</div>
            <div class="stat-label">Ongoing</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <CheckCircle :size="24" color="#f59e0b" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ completedExperiments.length }}</div>
            <div class="stat-label">Completed</div>
          </div>
        </div>
      </div>

      <!-- Experiments Grid -->
      <div class="experiments-section">
        <div class="section-header">
          <h2 class="section-title">Your Experiments</h2>
          <div class="section-actions">
            <button class="filter-button" @click="showFilters = !showFilters">
              <Filter :size="16" />
              Filter
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p class="loading-text">Loading experiments...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <h3 class="error-title">Failed to load experiments</h3>
          <p class="error-description">{{ error }}</p>
          <button class="error-action" @click="loadExperiments()">
            Try Again
          </button>
        </div>

        <!-- Empty State -->
        <div v-else-if="experiments.length === 0" class="empty-state">
          <div class="empty-icon">
            <FlaskConical :size="64" color="rgba(255, 255, 255, 0.4)" />
          </div>
          <h3 class="empty-title">No experiments yet</h3>
          <p class="empty-description">Create your first experiment to start tracking your health improvements</p>
          <button class="empty-action" @click="showAddExperiment = true">
            <Plus :size="20" />
            Create Experiment
          </button>
        </div>

        <!-- Experiments Grid -->
        <div v-else class="experiments-grid">
          <ExperimentCard
            v-for="experiment in filteredExperiments"
            :key="experiment.id"
            :experiment="experiment"
            :stats="experiment.stats"
            @complete="handleCompleteExperiment"
            @view="viewExperiment"
            @edit="editExperiment"
            @delete="handleDeleteExperiment"
          />
        </div>
      </div>
    </div>

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
import { ref, onMounted, watch, computed } from "vue";
import { useRoute } from 'vue-router';
import { 
  FlaskConical, Plus, Filter, TrendingUp, CheckCircle, Eye, Edit, Trash2,
  // Common experiment icons
  Heart, Zap, Brain, Clock, Calendar, Timer, Watch,
  LineChart, PieChart, TrendingDown, Target, Book, BookOpen,
  FileText, Home, Coffee, Moon, Sun, Lightbulb, Dumbbell, Mountain,
  Smartphone, Laptop, Headphones, Wifi, Battery, Apple,
  Cloud, CloudRain, Snowflake, Leaf, Flower, Briefcase,
  Building, Calculator, Pill, Users,
  User, MessageCircle, Phone, Mail, Bell, Car, Plane, Train,
  Smile, Frown, ThumbsUp, ThumbsDown, Star, Flag, Award, Gift, Key, Lock, Shield
} from "lucide-vue-next";
import AddExperimentModal from "./AddExperimentModal.vue";
import ExperimentCompletionModal from "./ExperimentCompletionModal.vue";
import ExperimentCard from "./ExperimentCard.vue";
import { useExperiments } from "../composables/useExperiments.js";
import { metricsApi } from "../services/api.js";

// Use the experiments composable for state management
const {
  experiments,
  isLoading,
  error,
  ongoingExperiments,
  completedExperiments,
  notStartedExperiments,
  loadExperiments,
  createExperiment,
  updateExperiment,
  deleteExperiment,
  completeExperiment,
  clearError
} = useExperiments();

// Local component state
const showAddExperiment = ref(false);
const availableMetrics = ref([]);
const editingExperiment = ref(null);
const metricsLoaded = ref(false);
const showDeleteConfirmation = ref(false);
const experimentToDelete = ref(null);
const showCompletionModal = ref(false);
const completingExperiment = ref(null);
const showFilters = ref(false);
const filterStatus = ref('all'); // 'all', 'ongoing', 'completed', 'not-started'

// Computed properties
const filteredExperiments = computed(() => {
  if (filterStatus.value === 'ongoing') return ongoingExperiments.value;
  if (filterStatus.value === 'completed') return completedExperiments.value;
  if (filterStatus.value === 'not-started') return notStartedExperiments.value;
  
  // When showing all experiments, sort by status (ongoing first) and then by start date
  if (filterStatus.value === 'all') {
    const today = new Date().toISOString().split('T')[0];
    
    return [...experiments.value].sort((a, b) => {
      // Helper function to determine experiment status
      const getStatus = (exp) => {
        if (!exp.start_date || !exp.end_date) return 'not-started';
        if (today >= exp.start_date && today <= exp.end_date) return 'ongoing';
        if (today > exp.end_date) return 'completed';
        return 'not-started';
      };
      
      const statusA = getStatus(a);
      const statusB = getStatus(b);
      
      // Priority order: ongoing > not-started > completed
      const statusOrder = { 'ongoing': 0, 'not-started': 1, 'completed': 2 };
      
      if (statusOrder[statusA] !== statusOrder[statusB]) {
        return statusOrder[statusA] - statusOrder[statusB];
      }
      
      // Within same status, sort by start_date descending (latest first)
      return new Date(b.start_date || 0) - new Date(a.start_date || 0);
    });
  }
  
  return experiments.value;
});

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

// Note: loadExperiments is now provided by the useExperiments composable

// Load metrics from API
async function loadMetrics() {
  if (metricsLoaded.value) {
    console.log('Metrics already loaded, skipping...');
    return;
  }
  
  try {
    console.log('Loading metrics...');
    const result = await metricsApi.getAll();
    
    if (result.success) {
      availableMetrics.value = result.data.metrics || [];
      metricsLoaded.value = true;
      console.log('Loaded metrics:', availableMetrics.value.length, 'metrics');
    } else {
      throw new Error(result.error || 'Failed to load metrics');
    }
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
async function handleExperimentCreated(experimentData) {
  const result = await createExperiment(experimentData);
  if (result.success) {
    showAddExperiment.value = false;
  }
}

// Handle experiment view
function viewExperiment(experiment) {
  // For now, just expand the experiment details
  // In the future, this could open a detailed view modal
  console.log('View experiment:', experiment);
}

// Handle experiment edit
function editExperiment(experiment) {
  editingExperiment.value = experiment;
  showAddExperiment.value = true;
}

// Handle experiment completion
function handleCompleteExperiment(experiment) {
  // Make sure all other modals are closed
  showAddExperiment.value = false;
  editingExperiment.value = null;
  showDeleteConfirmation.value = false;
  experimentToDelete.value = null;
  
  completingExperiment.value = experiment;
  showCompletionModal.value = true;
}

// Handle experiment delete
function handleDeleteExperiment(experiment) {
  experimentToDelete.value = experiment;
  showDeleteConfirmation.value = true;
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
async function handleExperimentUpdated(experimentData) {
  const result = await updateExperiment(editingExperiment.value.id, experimentData);
  if (result.success) {
    showAddExperiment.value = false;
    editingExperiment.value = null;
  }
}

// Confirm deletion
async function confirmDelete() {
  const experiment = experimentToDelete.value;
  if (!experiment) return;
  
  const result = await deleteExperiment(experiment.id);
  if (result.success) {
    showDeleteConfirmation.value = false;
    experimentToDelete.value = null;
  }
}

// Cancel deletion
function cancelDelete() {
  showDeleteConfirmation.value = false;
  experimentToDelete.value = null;
}
</script>

<style scoped>
.experiments-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  color: white;
}

/* Hero Section */
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  padding: 4rem 1rem;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 40% 80%, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
  animation: pulse 4s ease-in-out infinite;
}

.hero-section::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(90deg, transparent 98%, rgba(255, 255, 255, 0.03) 100%),
    linear-gradient(0deg, transparent 98%, rgba(255, 255, 255, 0.03) 100%);
  background-size: 50px 50px;
  animation: moveGrid 20s linear infinite;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.hero-text {
  flex: 1;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  line-height: 1.6;
}

.hero-actions {
  flex-shrink: 0;
}

.hero-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border: none;
  border-radius: 1rem;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
}

.hero-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(59, 130, 246, 0.4);
}

/* Main Content */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Quick Stats */
.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0.25rem 0 0 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Experiments Section */
.experiments-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 0.75rem;
}

.filter-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  margin: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: rgba(239, 68, 68, 0.05);
  border: 2px dashed rgba(239, 68, 68, 0.2);
  border-radius: 1rem;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #fca5a5;
  margin: 0 0 0.5rem 0;
}

.error-description {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 2rem 0;
  max-width: 400px;
  line-height: 1.6;
}

.error-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #ef4444;
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.error-action:hover {
  background: #dc2626;
  transform: translateY(-2px);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.5rem 0;
}

.empty-description {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 2rem 0;
  max-width: 400px;
  line-height: 1.6;
}

.empty-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.empty-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
}

/* Experiments Grid */
.experiments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

/* Delete Confirmation Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.confirmation-modal {
  background: rgba(25, 26, 36, 0.95);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1rem;
  width: 100%;
  max-width: 400px;
  margin: 1rem;
  overflow: hidden;
}

.confirmation-header {
  padding: 1.5rem 1.5rem 0;
}

.confirmation-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: white;
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
  color: white;
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

/* Animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

@keyframes moveGrid {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .quick-stats {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .experiments-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .confirmation-actions {
    flex-direction: column;
  }
  
  .confirmation-actions button {
    width: 100%;
  }
}
</style> 