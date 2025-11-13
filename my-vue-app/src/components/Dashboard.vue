<template>
  <div class="min-h-screen bg-background">
    <!-- Toast Notifications -->
    <div class="toast-container">
      <div 
        v-for="toast in toasts" 
        :key="toast.id" 
        class="toast"
        :class="toast.type"
        @click="removeToast(toast.id)"
      >
        <div class="toast-icon">
          <CheckCircle v-if="toast.type === 'success'" class="w-5 h-5" />
          <AlertCircle v-else-if="toast.type === 'error'" class="w-5 h-5" />
          <Info v-else class="w-5 h-5" />
        </div>
        <div class="toast-content">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button class="toast-close" @click.stop="removeToast(toast.id)">
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-overlay"></div>
      <div class="health-pattern"></div>
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">Health Metrics Dashboard</h1>
          <p class="hero-subtitle">
            Track your health metrics, interventions, and experiments in one place
          </p>
          <div class="hero-actions">
            <button class="hero-button primary" @click="showNewGraphForm = true">
              <Plus class="button-icon" size="16" />
              Add Graph
            </button>
            <button class="hero-button secondary" @click="showAddDataForm = true">
              <Calendar class="button-icon" size="16" />
              Add Data
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Stats -->
    <section class="quick-stats-section">
      <div class="quick-stats-grid">
        <QuickStatsCard
          label="Health Score"
          value="85/100"
          :icon="Heart"
          icon-class="destructive"
        />
        <QuickStatsCard
          label="Active Graphs"
          :value="graphs.length || '...'"
          :icon="Activity"
          icon-class="primary"
        />
        <QuickStatsCard
          label="Data Points"
          :value="totalDataPoints || '...'"
          :icon="TrendingUp"
          icon-class="success"
        />
        <QuickStatsCard
          label="Experiments"
          value="2"
          :icon="Brain"
          icon-class="accent"
        />
      </div>
    </section>

    <!-- Main Content -->
    <main class="main-content">
      <Tabs :tabs="tabs" :default-value="currentTab" @tab-change="handleTabChange">
        <template #default="{ activeTab }">
          <TabContent value="metrics">
            <div class="tab-section">
              <div class="section-header">
                <h2 class="section-title">Health Metrics</h2>
                <button class="add-button" @click="showAddDataForm = true">
                  <Plus class="button-icon" size="16" />
                  Add Metric
                </button>
              </div>
              

              <!-- Integrated Metrics Section -->
              <div class="metrics-section">
                <h3 class="subsection-title">Live Data from Connected Devices</h3>
                <div class="integrated-metrics-grid">
                  <IntegratedMetricCard
                    v-for="(metric, index) in integratedMetrics"
                    :key="index"
                    :title="metric.title"
                    :value="metric.value"
                    :unit="metric.unit"
                    :trend="metric.trend"
                    :trend-value="metric.trendValue"
                    :last-updated="metric.lastUpdated"
                    :source="metric.source"
                    :source-icon="metric.sourceIcon"
                    :category="metric.category"
                  />
                </div>
              </div>
            </div>
          </TabContent>

          <TabContent value="graphs">
            <div class="tab-section">
              <div class="section-header">
                <h2 class="section-title">Your Graphs</h2>
                <div class="header-actions">
                  <button class="add-button" @click="showNewGraphForm = true">
                    <Plus class="button-icon" size="16" />
                    Add Graph
                  </button>
                  <button class="add-button" @click="showAddDataForm = true">
                    <Plus class="button-icon" size="16" />
                    Add Data
                  </button>
                </div>
              </div>
              <div class="graphs-container">
                <p v-if="graphs.length === 0" class="empty-state">
                  No graphs found. Create your first graph to get started!
                </p>
                <div
                  v-for="(graph, index) in graphs"
                  :key="graph.id"
                  class="graph-card"
                >
                  <div class="graph-header">
                    <h3>{{ graph.title }}</h3>
                    <div class="graph-actions">
                      <button
                        :id="'ai-analyze-btn-' + index"
                        class="icon-button-wand"
                        @click="() => aiAnalyze(graph.graph_id, index)"
                      >
                        <img
                          src="../assets/magic-wand--filled 1.svg"
                          alt="Analyze"
                          class="w-6 h-6"
                        />
                      </button>
                      <button
                        class="icon-button"
                        @click="() => openGraphEditor(graph.graph_id)"
                      >
                        <img
                          src="../assets/edit.svg"
                          alt="Edit Icon"
                          class="w-6 h-6"
                        />
                      </button>
                      <button
                        class="icon-button"
                        @click="() => deleteGraph(graph.graph_id)"
                      >
                        <img
                          src="../assets/delete.svg"
                          alt="Delete Icon"
                          class="w-6 h-6"
                        />
                      </button>
                    </div>
                  </div>
                  <div :id="'user-graph-' + index" class="chart-container"></div>
                </div>
              </div>
            </div>
          </TabContent>


          <TabContent value="integrations">
            <div class="tab-section">
              <div class="section-header">
                <h2 class="section-title">Device Integrations</h2>
                <p class="section-description">
                  Connect your devices to automatically sync health data and track comprehensive metrics
                </p>
              </div>

              <div class="integrations-grid">
                <DeviceIntegrationCard
                  v-for="(device, index) in deviceIntegrations"
                  :key="index"
                  :name="device.name"
                  :logo="device.logo"
                  :connected="device.connected"
                  :last-sync="device.lastSync"
                  :metrics="device.metrics"
                  :sync-frequency="device.syncFrequency"
                  :data-points="device.dataPoints"
                  :selected-metrics="device.selectedMetrics"
                  :available-metrics="device.availableMetrics"
                  :syncing="device.syncing || false"
                  @connect="handleDeviceConnect(device)"
                  @disconnect="handleDeviceDisconnect(device)"
                  @selectMetrics="handleSelectMetrics(device)"
                  @syncNow="handleSyncNow(device)"
                />
              </div>

              <!-- Additional Integration Options -->
              <div class="additional-integrations">
                <h3 class="subsection-title">More Integrations Coming Soon</h3>
                <div class="coming-soon-grid">
                  <div class="coming-soon-card">
                    <div class="coming-soon-icon">
                      <Apple class="icon" />
                    </div>
                    <h4 class="coming-soon-title">Apple Health</h4>
                    <p class="coming-soon-description">Sync with Apple HealthKit for comprehensive health tracking</p>
                  </div>
                  <div class="coming-soon-card">
                    <div class="coming-soon-icon">
                      <Heart class="icon" />
                    </div>
                    <h4 class="coming-soon-title">Polar</h4>
                    <p class="coming-soon-description">Sync heart rate and training data from Polar devices</p>
                  </div>
                </div>
              </div>
            </div>
          </TabContent>

          <TabContent value="experiments">
            <div class="tab-section">
              <!-- Quick Stats -->
              <div class="quick-stats">
                <div class="stat-card">
                  <div class="stat-icon">
                    <FlaskConical :size="24" color="#3b82f6" />
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ experiments?.length || 0 }}</div>
                    <div class="stat-label">Total Experiments</div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon">
                    <TrendingUp :size="24" color="#10b981" />
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ ongoingExperiments?.length || 0 }}</div>
                    <div class="stat-label">Ongoing</div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon">
                    <CheckCircle :size="24" color="#f59e0b" />
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ completedExperiments?.length || 0 }}</div>
                    <div class="stat-label">Completed</div>
                  </div>
                </div>
              </div>

              <!-- Experiments Section -->
              <div class="experiments-section">
                <div class="section-header">
                  <h2 class="section-title">Your Experiments</h2>
                  <div class="section-actions">
                    <button class="filter-button" @click="showFilters = !showFilters">
                      <Filter :size="16" />
                      Filter
                    </button>
                    <button class="add-button" @click="openAddExperimentModal">
                      <Plus class="button-icon" size="16" />
                      New Experiment
                    </button>
                  </div>
                </div>

                <!-- Loading State -->
                <div v-if="experimentsLoading" class="loading-state">
                  <div class="loading-spinner"></div>
                  <p class="loading-text">Loading experiments...</p>
                </div>

                <!-- Error State -->
                <div v-else-if="experimentsError" class="error-state">
                  <div class="error-icon">⚠️</div>
                  <h3 class="error-title">Failed to load experiments</h3>
                  <p class="error-description">{{ experimentsError }}</p>
                  <button class="error-action" @click="loadExperiments()">
                    Try Again
                  </button>
                </div>

                <!-- Empty State -->
                <div v-else-if="!experiments || experiments.length === 0" class="empty-state">
                  <div class="empty-icon">
                    <FlaskConical :size="64" color="rgba(255, 255, 255, 0.4)" />
                  </div>
                  <h3 class="empty-title">No experiments yet</h3>
                  <p class="empty-description">Create your first experiment to start tracking your health improvements</p>
                  <button class="empty-action" @click="openAddExperimentModal">
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
          </TabContent>
        </template>
      </Tabs>
    </main>

        <!-- New Graph Form Modal -->
        <NewGraphForm
          :isVisible="showNewGraphForm"
          @close="showNewGraphForm = false"
          @graphCreated="handleGraphCreated"
        />

        <!-- AI Analysis Modal -->
        <transition name="modal-fade">
          <div v-if="showModal" class="modal-overlay">
            <div class="modal-wrapper">
              <div class="modal-container">
                <div class="modal-header">
                  <h1 class="modal-title">AI Analysis</h1>
                  <button
                    class="close-button"
                    type="button"
                    @click="closeAnalysis"
                  >
                    &times;
                  </button>
                </div>
                <div class="modal-body">
                  <div
                    id="ai-analysis-content"
                    class="analysis-content"
                    v-html="analysisContent"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </transition>


        <!-- Add Data Form Modal -->
        <AddDataForm
          v-if="showAddDataForm"
          :is-visible="showAddDataForm"
          :graphs="graphs"
          @close="showAddDataForm = false"
          @data-added="handleDataAdded"
        />

        <!-- Graph Editor Modal -->
        <transition name="modal-fade">
          <GraphEditor
            v-if="showGraphEditor"
            :graph-id="selectedGraphId"
            @close="showGraphEditor = false"
            @updated="handleGraphUpdated"
          />
        </transition>

        <!-- Metric Selection Modal -->
        <MetricSelectionModal
          :is-visible="showMetricSelection"
          :device-name="selectedDevice?.name || ''"
          :available-metrics="selectedDevice?.availableMetrics || []"
          :selected-metrics="selectedDevice?.selectedMetrics || []"
          @close="closeMetricSelection"
          @save="handleMetricSelectionSave"
        />

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

        <!-- Experiment Analytics Modal -->
        <ExperimentAnalyticsModal
          :isVisible="showAnalyticsModal"
          :experiment="viewingExperiment"
          @close="showAnalyticsModal = false"
        />
      </div>
   
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed, onUpdated } from "vue";
import { useRouter, useRoute } from "vue-router";
import ApexCharts from "apexcharts";
import { marked } from "marked";
import { FlaskConical, BarChart3, Activity, GitBranch, Upload, Plus, Calendar, Heart, TrendingUp, Brain, Watch, Zap, Shield, CheckCircle, AlertCircle, Info, X, Apple, Filter } from "lucide-vue-next";
import NewGraphForm from "./NewGraphForm.vue";
import AddDataForm from "./AddDataForm.vue";
import GraphEditor from "./GraphEditor.vue";
import MetricCard from "./MetricCard.vue";
import QuickStatsCard from "./QuickStatsCard.vue";
import Tabs from "./Tabs.vue";
import TabContent from "./TabContent.vue";
import DeviceIntegrationCard from "./DeviceIntegrationCard.vue";
import IntegratedMetricCard from "./IntegratedMetricCard.vue";
import MetricSelectionModal from "./MetricSelectionModal.vue";
import AddExperimentModal from "./AddExperimentModal.vue";
import ExperimentCompletionModal from "./ExperimentCompletionModal.vue";
import ExperimentCard from "./ExperimentCard.vue";
import ExperimentAnalyticsModal from "./ExperimentAnalyticsModal.vue";
import { getApiUrl } from "../config";
import { useExperiments } from "../composables/useExperiments.js";
import { metricsApi, dashboardApi, integrationsApi, graphsApi } from "../services/api.js";

const router = useRouter();
const route = useRoute();

/**
 * Reactive state (replacing data())
 */
const graphs = ref([]);
const showModal = ref(false);
const analysisContent = ref("");
const showNewGraphForm = ref(false);
const showAddDataForm = ref(false);
const showGraphEditor = ref(false);
const selectedGraphId = ref(null);

// Device integrations data (fetched from API)
const deviceIntegrations = ref([]);
const showMetricSelection = ref(false);
const selectedDevice = ref(null);

// Experiments data and functionality
const {
  experiments,
  isLoading: experimentsLoading,
  error: experimentsError,
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

// Experiments local state
const showAddExperiment = ref(false);
const availableMetrics = ref([]);
const editingExperiment = ref(null);
const showDeleteConfirmation = ref(false);
const experimentToDelete = ref(null);
const showCompletionModal = ref(false);
const completingExperiment = ref(null);
const showAnalyticsModal = ref(false);
const viewingExperiment = ref(null);
const showFilters = ref(false);
const filterStatus = ref('all'); // 'all', 'ongoing', 'completed', 'not-started'

// Tabs configuration
const tabs = ref([
  { label: "Metrics", value: "metrics", route: "/dashboard/overview" },
  { label: "Graphs", value: "graphs", route: "/dashboard/overview" },
  { label: "Integrations", value: "integrations", route: "/dashboard/integrations" },
  { label: "Experiments", value: "experiments", route: "/dashboard/experiments" }
]);

// Recent metrics data - now fetched dynamically from the database
const recentMetrics = ref([]);
const recentMetricsLoading = ref(false);
const recentMetricsError = ref(null);

// Integrated metrics from connected devices (fetched from API)
const integratedMetrics = ref([]);

// Total datapoints from all integrations
const totalIntegrationDatapoints = ref(0);

// Toast notification system
const toasts = ref([]);

// Toast functions
function addToast(title, message, type = 'info') {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, title, message, type })
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    removeToast(id)
  }, 5000)
}

function removeToast(id) {
  const index = toasts.value.findIndex(toast => toast.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

// Load integrated metrics from API
async function loadIntegratedMetrics() {
  try {
    // Get selected metrics from API
    const selectedResponse = await dashboardApi.getSelectedMetrics()
    const selectedData = selectedResponse.success ? selectedResponse.data : {}
    
    // Get metric values from API
    const valuesResponse = await dashboardApi.getMetricValues()
    const valuesData = valuesResponse.success ? valuesResponse.data : {}
    
    // Get integrations status to see which devices are connected
    const integrationsResponse = await integrationsApi.getStatus()
    const integrationsData = integrationsResponse.success ? integrationsResponse.data : { integrations: [] }    
    // Calculate total datapoints from all integrations
    // Check if integrations is an array or if it's nested differently
    let integrationsArray = []
    if (Array.isArray(integrationsData.integrations)) {
      integrationsArray = integrationsData.integrations
    } else if (Array.isArray(integrationsData)) {
      integrationsArray = integrationsData
    }

    const totalDatapoints = integrationsArray.reduce((total, integration) => {
      const datapoints = integration.data_points || integration.datapoints || 0
      return total + datapoints
    }, 0)
    console.log('🔍 Total datapoints from all integrations:', totalDatapoints)
    
    // Store the total in reactive variable for use in UI
    totalIntegrationDatapoints.value = totalDatapoints

    // Get available metrics from API
    const availableResponse = await dashboardApi.getAvailableMetrics()
    const availableData = availableResponse.success ? availableResponse.data : {}
    
    const metrics = []
    
    // Process each connected device's selected metrics
    integrationsData.integrations.forEach(integration => {
      if (integration.connected && selectedData.selected_metrics[integration.name.toLowerCase()]) {
        const deviceMetrics = selectedData.selected_metrics[integration.name.toLowerCase()]
        const deviceValues = valuesData.metric_values[integration.name.toLowerCase()] || {}
        
        deviceMetrics.forEach(metricObj => {
          // Create metric object based on the selected metric using API data
          const metric = createMetricFromName(metricObj.id || metricObj, integration.name, availableData, deviceValues)
          if (metric) {
            metrics.push(metric)
          }
        })
      }
    })
    
    integratedMetrics.value = metrics
  } catch (error) {
    console.error("Error loading integrated metrics:", error);
    integratedMetrics.value = []
  }
}

// Load recent metrics from the database
async function loadRecentMetrics() {
  try {
    recentMetricsLoading.value = true;
    recentMetricsError.value = null;
    
    // Fetch recent metrics from the API
    const result = await dashboardApi.getRecentMetrics();
    
    if (result.success) {
      // Update the recent metrics with data from the database
      recentMetrics.value = result.data.recent_metrics || [];
      console.log('Loaded recent metrics:', recentMetrics.value, 'entries');
    } else {
      throw new Error(result.error || 'Failed to load recent metrics');
    }
  } catch (error) {
    console.error("Error loading recent metrics:", error);
    recentMetricsError.value = error.message;
    
    // Fallback to empty array if API fails
    recentMetrics.value = [];
  } finally {
    recentMetricsLoading.value = false;
  }
}

// Helper function to create metric objects from metric names using API data
function createMetricFromName(metricName, source, availableMetrics = {}, deviceValues = {}) {
  const sourceIcon = source === 'Oura Ring' ? Zap : source === 'Garmin Connect' ? Watch : Shield
  
  // Find the metric definition from available metrics
  // Map device names to API keys
  const deviceKeyMap = {
    'Oura Ring': 'oura',
    'Garmin Connect': 'garmin', 
    'WHOOP': 'whoop'
  }
  const deviceKey = deviceKeyMap[source] || source.toLowerCase().replace(' ', '_')
  
  const metricDef = availableMetrics[deviceKey]?.find(m => m.id === metricName)
  
  // Get real values from deviceValues
  const metricValue = deviceValues[metricName] || {}
  const value = metricValue.value || 0
  const unit = metricValue.unit || getMetricUnit(metricName)
  const lastUpdated = metricValue.date ? formatDate(metricValue.date) : "No data"
  
  return {
    title: metricDef?.name || formatMetricName(metricName),
    value: value,
    unit: unit,
    trend: "stable",
    lastUpdated: lastUpdated,
    source: source,
    sourceIcon: sourceIcon,
    category: metricDef?.category || 'vital',
    metricId: metricName
  }
}

// Helper function to format dates
function formatDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return "Today"
  } else if (diffDays === 1) {
    return "Yesterday"
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else {
    return date.toLocaleDateString()
  }
}

// Function to format metric names
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
  }
  
  return metricNames[metricName] || metricName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}


// Helper function to get metric units (fallback)
function getMetricUnit(metricName) {
  // This could be enhanced to get units from API data as well
  const unitMap = {
    'average_heart_rate': 'bpm',
    'average_hrv': 'ms',
    'average_breath': 'breaths/min',
    'awake_time': 'min',
    'deep_sleep_duration': 'min',
    'rem_sleep_duration': 'min',
    'total_sleep_duration': 'min',
    'hrv': 'ms',
    'heart_rate': 'bpm',
    'temperature': '°C',
    'steps': '',
    'vo2_max': 'ml/kg/min'
  }
  return unitMap[metricName] || ''
}


// Helper functions


// Computed properties
const totalDataPoints = computed(() => {
  // Get total data points from all data points in the database
  return totalIntegrationDatapoints || 0;
});

/**
 * Function to load graphs and render charts
 */
async function loadGraphs() {
  try {
    const response = await fetch(getApiUrl("graphs"));
    const data = await response.json();
    
    // Ensure data is an array
    if (Array.isArray(data)) {
      graphs.value = data;
    } else {
      console.error("Graphs API returned non-array data:", data);
      graphs.value = [];
    }
    
    nextTick(() => {
      renderCharts();
    });
  } catch (error) {
    console.error("Error loading graphs:", error);
    graphs.value = []; // Set to empty array on error
  }
}

// Performance tracking
const renderStartTime = performance.now();
let firstRenderComplete = false;

/**
 * Lifecycle hook (replacing mounted())
 * Fetch data from Flask API on component mount
 * Load critical data first, then lazy-load non-critical data
 */
onMounted(async () => {
  const mountStart = performance.now();
  
  // Load critical data first (parallel)
  await Promise.all([
    loadGraphs(),
    loadDeviceIntegrations(),
    loadExperiments(),
    loadAvailableMetrics()
  ]);
  
  const criticalLoadTime = performance.now() - mountStart;
  console.log(`📊 Critical data loaded in ${criticalLoadTime.toFixed(2)}ms`);
  
  // Lazy-load non-critical data after initial render
  nextTick(() => {
    setTimeout(async () => {
      const lazyStart = performance.now();
      await Promise.all([
        loadIntegratedMetrics(),
        loadRecentMetrics()
      ]);
      const lazyLoadTime = performance.now() - lazyStart;
      console.log(`🔄 Lazy data loaded in ${lazyLoadTime.toFixed(2)}ms`);
    }, 100); // Small delay to let UI render first
  });
});

// Track when first data render completes
onUpdated(() => {
  if (!firstRenderComplete && graphs.value.length > 0) {
    const renderTime = performance.now() - renderStartTime;
    console.log(`🎨 First data render completed in ${renderTime.toFixed(2)}ms`);
    firstRenderComplete = true;
  }
});

/**
 * Watch for route changes to reload graphs when navigating back to dashboard
 */
watch(() => route.path, (newPath) => {
  if (newPath === '/dashboard') {
    loadGraphs();
  }
});

/**
 * Replacing "methods": Now just plain JS functions
 */

// 1) Render ApexCharts
function renderCharts() {
  // Define the base options that should be consistent across all graphs
  const baseOptions = {
    chart: {
      type: "area",
      foreColor: "#ffffff",
      animations: { enabled: true },
      background: "transparent",
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: true,
      },
    },
    xaxis: {
      type: "datetime",
      labels: {
        style: {
          colors: "#999",
        },
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: "#999",
        },
        formatter: (val) => {
          return val !== null && val !== undefined ? Math.round(val).toLocaleString() : "";
        },
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shadeIntensity: 1,
        inverseColors: false,
        opacityFrom: 0.6,
        opacityTo: 0.1,
        stops: [20, 100],
      },
    },
    colors: [
      "#FF4560",
      "#00E396",
      "#008FFB",
      "#FEB019",
      "#775DD0",
      "#FF66C3",
      "#26A69A",
      "#546E7A",
      "#D4526E",
      "#F86624",
    ],
    dataLabels: { enabled: false },
    stroke: { curve: "smooth", width: 2 },  
    grid: {
      show: true,
      borderColor: "rgba(255,255,255,0.05)",
      strokeDashArray: 3,
    },
    tooltip: {
      shared: true,
      intersect: false,
      theme: "dark",
      followCursor: true,
      y: {
        formatter: (val) =>
          val !== null && val !== undefined ? val.toFixed(0) : "",
      },
      style: {
        fontSize: "12px",
      },
    },
          legend: {
        show: true,
        position: "bottom",
        horizontalAlign: "center",
        labels: { 
          colors: "rgba(255, 255, 255, 0.6)",
          useSeriesColors: false
        },
        itemMargin: {
          horizontal: 10,
          vertical: 5,
        },
      },
  };

  // Ensure graphs.value is an array
  if (!Array.isArray(graphs.value)) {
    console.error("Graphs data is not an array:", graphs.value);
    return;
  }

  graphs.value.forEach((graph, index) => {
    // Transform the data format for ApexCharts
    const series = (graph.figure || []).map(figure => ({
      name: formatMetricName(figure.name),
      data: figure.data.map(point => ({
        x: new Date(point.x).getTime(), // Convert date string to timestamp
        y: point.y
      }))
    }));

    // Create a new options object by merging the base options with graph-specific data
    const options = {
      ...baseOptions,
      series: series,
    };

    const chartEl = document.querySelector(`#user-graph-${index}`);
    
    if (chartEl) {
      // Clear any existing chart content
      chartEl.innerHTML = '';
      
      const chart = new ApexCharts(chartEl, options);
      chart.render();
    }
  });
}

// 2) AI Analyze
function aiAnalyze(graphId, index) {
  const buttonEl = document.getElementById(`ai-analyze-btn-${index}`);
  if (buttonEl) {
    buttonEl.disabled = true;
    buttonEl.classList.add("opacity-50", "cursor-not-allowed");
  }

  showModal.value = true;
  analysisContent.value = `
    <div class="flex items-center justify-center space-x-2 animate-pulse">
      <div class="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <span>Loading AI Analysis...</span>
    </div>
  `;

  fetch(getApiUrl(`ai-analyze/${graphId}`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`Server error: ${res.status} ${res.statusText}`);
      }
      return res.json();
    })
    .then((data) => {
      analysisContent.value = marked.parse(data.ai_analysis);
    })
    .catch((err) => {
      analysisContent.value = "Error loading analysis.";
    })
    .finally(() => {
      if (buttonEl) {
        buttonEl.disabled = false;
        buttonEl.classList.remove("opacity-50", "cursor-not-allowed");
      }
    });
}

// 3) Close Modal
function closeAnalysis() {
  showModal.value = false;
}

// 4) Delete Graph
function deleteGraph(graphId) {
  if (!confirm("Are you sure you want to delete this graph?")) {
    return;
  }
  fetch(getApiUrl(`graphs/${graphId}`), {
    method: "DELETE",
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error("Delete failed");
      }
      graphs.value = graphs.value.filter((g) => g.graph_id !== graphId);
    })
    .catch((err) => console.error("Error fetching graphs:", err));
}

// 5) Handle Graph Creation
function handleGraphCreated(newGraph) {
  // Format the graph for display
  const formattedGraph = {
    title: newGraph.title,
    graph_id: newGraph.graph_id,
    description: newGraph.description,
    figure: [
      {
        name: "Empty",
        data: [],
      },
    ],
  };

  // Add the new graph to the graphs array
  graphs.value.push(formattedGraph);

  // Render the chart for the new graph
  nextTick(() => {
    const index = graphs.value.length - 1;
    const chartEl = document.querySelector(`#user-graph-${index}`);
    if (chartEl) {
      const options = {
        chart: {
          type: "area",
          foreColor: "#ffffff",
          animations: { enabled: true },
          background: "transparent",
          toolbar: {
            show: false,
          },
          zoom: {
            enabled: true,
          },
        },
        series: formattedGraph.figure || [],
        xaxis: {
          type: "datetime",
          labels: { style: { colors: "#999" } },
          axisBorder: { show: false },
          axisTicks: { show: false },
        },
        yaxis: {
          labels: { 
            style: { colors: "#999" },
            formatter: (val) => {
              return val !== null && val !== undefined ? Math.round(val).toLocaleString() : "";
            },
          },
        },
        fill: {
          type: "gradient",
          gradient: {
            shadeIntensity: 1,
            inverseColors: false,
            opacityFrom: 0.6,
            opacityTo: 0.1,
            stops: [20, 100],
          },
        },
        colors: ["#FF4560", "#00E396", "#008FFB"],
        dataLabels: { enabled: false },
        stroke: { curve: "smooth", width: 2 },
        grid: {
          show: true,
          borderColor: "rgba(255,255,255,0.05)",
          strokeDashArray: 3,
        },
        tooltip: {
          shared: true,
          intersect: false,
          theme: "dark",
          followCursor: true,
          y: {
            formatter: (val) =>
              val !== null && val !== undefined ? val.toFixed(0) : "",
          },
        },
        legend: {
          show: true,
          position: "right",
          offsetX: 0,
          offsetY: 0,
          labels: { 
            colors: "rgba(255, 255, 255, 0.6)",
            useSeriesColors: false
          },
          itemMargin: {
            horizontal: 5,
            vertical: 8,
          },
          fontSize: "12px",
          width: 200,
        },
      };

      const chart = new ApexCharts(chartEl, options);
      chart.render();
    }
  });
}

function handleDataAdded(data) {
  // Refresh the graphs data to show the new data points
  fetchGraphs();
}

// Device integration functions
async function loadDeviceIntegrations() {
  try {
    const response = await integrationsApi.getStatus()
    const data = response.success ? response.data : { integrations: [] }
    
    if (data.integrations) {
      deviceIntegrations.value = data.integrations.map(integration => ({
        name: integration.name,
        logo: getDeviceLogo(integration.name),
        connected: integration.connected,
        lastSync: integration.last_sync ? formatLastSync(integration.last_sync) : "Never",
        metrics: integration.available_metrics,
        syncFrequency: integration.sync_frequency === 'manual' ? 'Manual' : integration.sync_frequency,
        dataPoints: integration.data_points,
        selectedMetrics: integration.selected_metrics || [],
        availableMetrics: (integration.available_metrics || []).map(metric => ({
          id: metric,
          name: formatMetricName(metric)
        }))
      }))
    }

  } catch (error) {
    console.error('Error loading device integrations:', error)
  }
}

function getDeviceLogo(deviceName) {
  const logos = {
    'Oura Ring': Zap,
    'Garmin Connect': Watch,
    'Fitbit': Heart,
    'WHOOP': Shield
  }
  return logos[deviceName] || Zap
}

function formatLastSync(lastSync) {
  if (!lastSync) return 'Never'
  
  const now = new Date()
  const syncTime = new Date(lastSync)
  const diffMs = now - syncTime
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffMins < 1) {
    return 'Just now'
  } else if (diffMins < 60) {
    return `${diffMins}m ago`
  } else if (diffHours < 24) {
    return `${diffHours}h ago`
  } else if (diffDays < 7) {
    return `${diffDays}d ago`
  } else {
    return syncTime.toLocaleDateString()
  }
}


// Device connection handlers
function handleDeviceConnect(device) {
  console.log("Connecting to device:", device.name);
  // Here you would implement the actual connection logic
  device.connected = true;
  device.lastSync = "Just now";
}

function handleDeviceDisconnect(device) {
  console.log("Disconnecting from device:", device.name);
  // Here you would implement the actual disconnection logic
  device.connected = false;
  device.lastSync = "Disconnected";
}

function handleSelectMetrics(device) {
  console.log("Selecting metrics for device:", device.name);
  selectedDevice.value = device;
  showMetricSelection.value = true;
}

function closeMetricSelection() {
  showMetricSelection.value = false;
  selectedDevice.value = null;
}

function handleMetricSelectionSave(selectedMetrics) {
  if (selectedDevice.value) {
    selectedDevice.value.selectedMetrics = selectedMetrics;
    console.log(`Updated metrics for ${selectedDevice.value.name}:`, selectedMetrics);
  }
  closeMetricSelection();
}

async function handleSyncNow(device) {
  console.log("Syncing device:", device.name)
  
  // Set syncing state
  device.syncing = true
  
  // Show sync started notification
  addToast(
    'Sync Started', 
    `Starting sync for ${device.name}...`, 
    'info'
  )
  
  try {
    let response
    let dateRange = ''
    
    if (device.name === 'Oura Ring') {
      // Calculate date range (last 7 days)
      const endDate = new Date()
      const startDate = new Date()
      startDate.setDate(endDate.getDate() - 7)
      
      dateRange = `${startDate.toISOString().split('T')[0]} to ${endDate.toISOString().split('T')[0]}`
      
      response = await fetch('http://localhost:5174/api/integrations/oura/sync-now', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: startDate.toISOString().split('T')[0],
          end_date: endDate.toISOString().split('T')[0]
        })
      })
    } else if (device.name === 'Fitbit') {
      response = await fetch('http://localhost:5174/api/integrations/fitbit/sync-now', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
    }
    
    if (response && response.ok) {
      const result = await response.json()
      console.log('Sync successful:', result)
      
      // Update last sync time
      device.lastSync = 'Just now'
      
      // Show detailed success message
      const recordsCount = result.records_imported || 0
      const syncMessage = recordsCount > 0 
        ? `Successfully imported ${recordsCount} data points${dateRange ? ` from ${dateRange}` : ''}`
        : `Sync completed successfully${dateRange ? ` for ${dateRange}` : ''} - no new data found`
      
      addToast(
        'Sync Completed', 
        syncMessage, 
        'success'
      )
      
      // Reload integrations to get updated data
      await loadDeviceIntegrations()
    } else {
      const error = await response?.json()
      throw new Error(error?.error || 'Sync failed')
    }
  } catch (error) {
    console.error('Sync error:', error)
    addToast(
      'Sync Failed', 
      `Failed to sync ${device.name}: ${error.message}`, 
      'error'
    )
  } finally {
    // Clear syncing state
    device.syncing = false
  }
}

// Experiments computed properties and functions
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

// Load available metrics for experiments
async function loadAvailableMetrics() {
  try {
    const response = await metricsApi.getAll();
    if (response.success) {
      availableMetrics.value = response.data?.metrics || response.data || [];
    } else {
      console.error('Error loading metrics:', response.error);
      availableMetrics.value = [];
    }
  } catch (error) {
    console.error('Error loading metrics:', error);
    availableMetrics.value = [];
  }
}

// Experiment handlers
function handleExperimentCreated(experiment) {
  console.log('Experiment created:', experiment);
  loadExperiments(); // Refresh the list
}

function handleExperimentUpdated(experiment) {
  console.log('Experiment updated:', experiment);
  loadExperiments(); // Refresh the list
}

function openAddExperimentModal() {
  // Close any other open modals
  showAnalyticsModal.value = false;
  showCompletionModal.value = false;
  viewingExperiment.value = null;
  completingExperiment.value = null;
  editingExperiment.value = null;
  
  showAddExperiment.value = true;
}

function handleCompleteExperiment(experiment) {
  // Close any other open modals
  showAddExperiment.value = false;
  showAnalyticsModal.value = false;
  editingExperiment.value = null;
  viewingExperiment.value = null;
  
  completingExperiment.value = experiment;
  showCompletionModal.value = true;
}

function handleExperimentCompleted(experiment) {
  console.log('Experiment completed:', experiment);
  loadExperiments(); // Refresh the list
  showCompletionModal.value = false;
  completingExperiment.value = null;
}

function handleCompletionModalClose() {
  showCompletionModal.value = false;
  completingExperiment.value = null;
}

function viewExperiment(experiment) {
  console.log('🔍 Opening Analytics Modal - Closing other modals');
  // Close any other open modals
  showAddExperiment.value = false;
  showCompletionModal.value = false;
  editingExperiment.value = null;
  completingExperiment.value = null;
  
  // Small delay to ensure state updates
  nextTick(() => {
    viewingExperiment.value = experiment;
    showAnalyticsModal.value = true;
    console.log('🔍 Analytics Modal State:', {
      showAddExperiment: showAddExperiment.value,
      showAnalyticsModal: showAnalyticsModal.value,
      showCompletionModal: showCompletionModal.value
    });
  });
}

function editExperiment(experiment) {
  // Close any other open modals
  showAnalyticsModal.value = false;
  showCompletionModal.value = false;
  viewingExperiment.value = null;
  completingExperiment.value = null;
  
  editingExperiment.value = experiment;
  showAddExperiment.value = true;
}

function handleDeleteExperiment(experiment) {
  experimentToDelete.value = experiment;
  showDeleteConfirmation.value = true;
}

function cancelDelete() {
  showDeleteConfirmation.value = false;
  experimentToDelete.value = null;
}

async function confirmDelete() {
  if (experimentToDelete.value) {
    try {
      await deleteExperiment(experimentToDelete.value.id);
      showDeleteConfirmation.value = false;
      experimentToDelete.value = null;
      loadExperiments(); // Refresh the list
    } catch (error) {
      console.error('Error deleting experiment:', error);
    }
  }
}

// Function to fetch graphs from the API
async function fetchGraphs() {
  try {
    const response = await graphsApi.getAll();
    if (response.success) {
      graphs.value = response.data;
      nextTick(() => {
        renderCharts();
      });
    } else {
      console.error("Graphs API returned non-array data:", response);
      graphs.value = [];
    }
  } catch (err) {
    console.error("Error fetching graphs:", err);
    graphs.value = [];
  }
}

function openGraphEditor(graphId) {
  console.log("Opening editor for graph:", graphId);
  router.push(`/edit-graph/${graphId}`);
}

async function handleGraphUpdated() {
  // Refresh the graphs list
  try {
    const response = await graphsApi.getAll();
    if (response.success) {
      graphs.value = response.data;
      nextTick(() => {
        renderCharts();
      });
    } else {
      console.error("Error refreshing graphs:", response.error);
    }
  } catch (err) {
    console.error("Error refreshing graphs:", err);
  }
}

// Tab change handler
function handleTabChange(tabValue) {
  console.log("Tab changed to:", tabValue);
  
  // Navigate to the appropriate route
  const tab = tabs.value.find(t => t.value === tabValue);
  if (tab && tab.route) {
    router.push(tab.route);
  }
  
  // Re-render charts when switching to graphs tab
  if (tabValue === 'graphs') {
    nextTick(() => {
      // Small delay to ensure DOM elements are fully rendered
      setTimeout(() => {
        renderCharts();
      }, 100);
    });
  }
}

// Get active tab from current route
function getActiveTabFromRoute() {
  const route = router.currentRoute.value;
  if (route.path.includes('/integrations')) return 'integrations';
  if (route.path.includes('/experiments')) return 'experiments';
  if (route.path.includes('/overview')) return 'metrics';
  return 'metrics'; // default
}

// Reactive tab value based on current route
const currentTab = ref(getActiveTabFromRoute());

// Watch for route changes to update active tab
watch(() => router.currentRoute.value.path, (newPath) => {
  currentTab.value = getActiveTabFromRoute();
}, { immediate: true });

// Modal state watcher - ensure only one modal is open at a time
watch([showAddExperiment, showAnalyticsModal, showCompletionModal], ([add, analytics, completion]) => {
  const openModals = [add, analytics, completion].filter(Boolean).length;
  if (openModals > 1) {
    console.warn('🚨 Multiple modals detected!', { add, analytics, completion });
  }
}, { immediate: true });


</script>

<style scoped>
/* Global styles */
.bg-background {
  background-color: #191a23;
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
  background-image: 
    radial-gradient(circle at 20% 20%, rgba(34, 197, 94, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 60%, rgba(168, 85, 247, 0.1) 0%, transparent 50%),
    linear-gradient(45deg, transparent 30%, rgba(34, 197, 94, 0.05) 50%, transparent 70%);
  animation: pulse 8s ease-in-out infinite;
}

.hero-section::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 98px,
      rgba(34, 197, 94, 0.03) 100px
    ),
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 98px,
      rgba(59, 130, 246, 0.03) 100px
    );
  animation: gridMove 20s linear infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

@keyframes gridMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(100px, 100px); }
}

/* Health-themed decorative elements */
.hero-section .health-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    /* Heart rate lines */
    linear-gradient(90deg, transparent 0%, rgba(239, 68, 68, 0.1) 2%, transparent 4%),
    linear-gradient(90deg, transparent 0%, rgba(239, 68, 68, 0.1) 2%, transparent 4%),
    /* Measurement grid */
    linear-gradient(0deg, transparent 0%, rgba(34, 197, 94, 0.05) 1px, transparent 2px),
    linear-gradient(90deg, transparent 0%, rgba(34, 197, 94, 0.05) 1px, transparent 2px);
  background-size: 200px 100px, 200px 100px, 50px 50px, 50px 50px;
  background-position: 0 0, 0 50px, 0 0, 0 0;
  animation: healthPulse 6s ease-in-out infinite;
  pointer-events: none;
}

@keyframes healthPulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
}

.hero-content {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.hero-text {
  max-width: 600px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: white;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  line-height: 1.5;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
}

.hero-button.primary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.hero-button.primary:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.hero-button.secondary {
  background: transparent;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.hero-button.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.button-icon {
  width: 1rem;
  height: 1rem;
}

/* Quick Stats Section */
.quick-stats-section {
  max-width: 1200px;
  margin: -2rem auto 0;
  padding: 0 1rem;
  position: relative;
  z-index: 10;
}

.quick-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

/* Main Content */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1rem;
}

/* Tab Section */
.tab-section {
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.add-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
}

.add-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
  background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
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
  padding: 2rem;
  text-align: center;
  background: rgba(239, 68, 68, 0.05);
  border: 2px dashed rgba(239, 68, 68, 0.2);
  border-radius: 0.75rem;
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

.error-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fca5a5;
  margin: 0 0 0.5rem 0;
}

.error-description {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 1.5rem 0;
  max-width: 300px;
  line-height: 1.5;
}

.error-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #ef4444;
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.error-action:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  opacity: 0.6;
}

.empty-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 0.5rem 0;
}

.empty-description {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  max-width: 300px;
  line-height: 1.5;
}

/* Integrations Grid */
.integrations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

/* Metrics Sections */
.metrics-section {
  margin-bottom: 3rem;
}

.subsection-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Integrated Metrics Grid */
.integrated-metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Graphs Container */
.graphs-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1200px) {
  .graphs-container {
    grid-template-columns: repeat(2, 1fr);
  }
}



/* Icon Buttons */
.icon-button,
.icon-button-wand {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-button:hover,
.icon-button-wand:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.icon-button img,
.icon-button-wand img {
  width: 1rem;
  height: 1rem;
  filter: invert(80%);
}

/* Empty States */
.empty-state {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1rem;
  margin: 2rem 0;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  margin: 1rem auto;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.cta-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
}

.integrations-content,
.experiments-content {
  text-align: center;
  padding: 2rem;
}

/* Modal Styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
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
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(16px);
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow-y: auto;
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body {
  margin-top: 0.5rem;
}

.analysis-content {
  margin-top: 1rem;
  line-height: 1.6;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
}

.analysis-content h1,
.analysis-content h2,
.analysis-content h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: white;
}

.analysis-content p {
  margin-bottom: 1rem;
}

.analysis-content ul,
.analysis-content ol {
  padding-left: 1.5rem;
  margin: 1rem 0;
}

.analysis-content li {
  margin-bottom: 0.5rem;
}

.analysis-content strong {
  font-weight: 600;
  color: #fff;
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

/* Graph Grid Layout */
.graph-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  max-width: 800px; /* Limit maximum width */
  margin: 0 auto; /* Center the grid */
}

.graph-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.graph-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, transparent 50%);
  pointer-events: none;
}

.graph-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.graph-header h3 {
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
}

.graph-actions {
  display: flex;
  gap: 0.5rem;
}

.chart-container {
  min-height: 300px;
  max-width: 100%;
  width: 100%;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .quick-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .integrations-grid {
    grid-template-columns: 1fr;
  }
  
  .integrated-metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .graph-grid {
    max-width: 100%;
    padding: 0 1rem;
  }
  
  .chart-container {
    min-height: 250px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

/* Ensure modals appear above everything */
:deep(.modal-overlay),
:deep(.fixed) {
  z-index: 9999;
}

/* Toast Notification Styles */
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  animation: slideIn 0.3s ease-out;
}

.toast:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.toast.success {
  border-left: 4px solid #22c55e;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.toast.info {
  border-left: 4px solid #3b82f6;
}

.toast-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.toast.success .toast-icon {
  color: #22c55e;
}

.toast.error .toast-icon {
  color: #ef4444;
}

.toast.info .toast-icon {
  color: #3b82f6;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.toast-message {
  font-size: 0.8125rem;
  color: #6b7280;
  line-height: 1.4;
}

.toast-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
}

.toast-close:hover {
  color: #6b7280;
  background: rgba(0, 0, 0, 0.05);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Integrations Styles */
.section-description {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
  margin-top: 0.5rem;
  line-height: 1.5;
}

.integrations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.additional-integrations {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.subsection-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 1.5rem;
}

.coming-soon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.coming-soon-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.coming-soon-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.coming-soon-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  margin-bottom: 1rem;
}

.coming-soon-icon .icon {
  width: 1.5rem;
  height: 1.5rem;
  color: rgba(255, 255, 255, 0.7);
}

.coming-soon-title {
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
}

.coming-soon-description {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.4;
}

/* Experiments Styles */
.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.experiments-section {
  margin-top: 2rem;
}

.section-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.filter-button {
  display: flex;
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
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text, .error-description, .empty-description {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-title, .empty-title {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.error-action, .empty-action {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.error-action:hover, .empty-action:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.experiments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

/* Modal Styles */
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
  backdrop-filter: blur(4px);
}

.confirmation-modal {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1rem;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  backdrop-filter: blur(10px);
}

.confirmation-header h3 {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.confirmation-body p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.5rem;
}

.warning-text {
  color: #f59e0b !important;
  font-size: 0.875rem;
}

.confirmation-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  justify-content: flex-end;
}

.button-secondary {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.button-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.button-danger {
  padding: 0.75rem 1.5rem;
  background: #ef4444;
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.button-danger:hover {
  background: #dc2626;
}
</style>
