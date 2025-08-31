<template>
  <div class="explorer-layout">
    <!-- Main Navigation Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <img :src="neuroflowLogo" alt="Neuroflow" class="sidebar-logo" />
        <span class="sidebar-title">Neuroflow</span>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/experiments" class="nav-link">
          <FlaskConical class="nav-icon" size="20" />
          <span>Experiments</span>
        </router-link>
        <router-link to="/dashboard" class="nav-link">
          <BarChart3 class="nav-icon" size="20" />
          <span>Dashboard</span>
        </router-link>
        <router-link to="/explorer" class="nav-link router-link-active">
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
    <main class="explorer-main">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">Explorer</h1>
          <div class="header-actions">
            <!-- Explorer-specific actions can go here if needed -->
          </div>
        </div>
      </div>

      <!-- Graph Container -->
      <div class="explorer-graph" :data-graph-id="tempGraphId">
        <h3 class="graph-title">{{ graphName }}</h3>
        <div id="explorer-chart" class="chart-container"></div>
        <div class="button-container">
          <button class="button-secondary" @click="cancelExploration">
            Cancel Exploration
          </button>
          <button
            class="button-primary"
            @click="addToDashboard"
            :disabled="selectedMetrics.length === 0"
          >
            + Add to dashboard
          </button>
        </div>
      </div>
    </main>

    <!-- Metrics Sidebar -->
    <aside class="metrics-sidebar">
      <div>
        <h2 class="sidebar-title">Metrics</h2>
        <div class="metrics-list">
          <div
            v-for="metric in metrics"
            :key="metric"
            class="metric-item"
            @click="toggleMetric(metric)"
          >
            <span class="metric-name">{{ metric }}</span>
            <img
              v-if="selectedMetrics.includes(metric)"
              :src="checkmarkIcon"
              alt="Selected"
              class="checkmark"
            />
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRouter } from "vue-router";
import ApexCharts from "apexcharts";
import { FlaskConical, BarChart3, Activity, GitBranch, Upload } from "lucide-vue-next";
import checkmarkIcon from "../assets/images/checkmark.svg";
import neuroflowLogo from "../assets/images/ChatGPT_Image_Apr_5__2025__01_36_36_PM-removebg-preview 1.svg";
import { getApiUrl } from "../config";

const router = useRouter();

// Props and state
const metrics = ref([]);
const selectedMetrics = ref([]);
const tempGraphId = ref(null);
const graphName = ref("Temporary explorer graph");
const chart = ref(null);
const currentSeries = ref([]);

// Chart options
const chartOptions = {
  chart: {
    type: "area",
    foreColor: "#ffffff",
    animations: { enabled: true },
    background: "transparent",
    toolbar: {
      show: false,
    },
    height: 350,
    width: "100%",
    redrawOnWindowResize: true,
  },
  series: [],
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
  },
  legend: {
    show: false,
    position: "bottom",
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

// Initialize explorer and fetch available metrics
async function initializeExplorer() {
  try {
    // Create temporary graph
    const response = await fetch(getApiUrl("explorer/init"), {
      method: "POST",
    });
    const data = await response.json();
    tempGraphId.value = data.temp_graph_id;
    metrics.value = data.metrics;

    // Initialize chart
    const chartElement = document.querySelector("#explorer-chart");
    if (chartElement) {
      // Wait for next tick to ensure DOM is fully rendered
      await nextTick();
      
      chart.value = new ApexCharts(chartElement, {
        ...chartOptions,
        chart: {
          ...chartOptions.chart,
          width: "100%",
        },
      });
      chart.value.render();

      // Update chart size when window resizes
      window.addEventListener("resize", () => {
        if (chart.value && chart.value.updateOptions) {
          chart.value.updateOptions({
            chart: {
              ...chartOptions.chart,
              width: "100%",
            },
          });
        }
      });
    }
  } catch (error) {
    console.error("Error initializing explorer:", error);
  }
}

// Toggle metric selection
async function toggleMetric(metric) {
  try {
    if (selectedMetrics.value.includes(metric)) {
      // Remove metric
      selectedMetrics.value = selectedMetrics.value.filter((m) => m !== metric);
      currentSeries.value = currentSeries.value.filter(
        (s) => s.name !== metric
      );
    } else {
      // Add metric
      const response = await fetch(
        getApiUrl(`metric-data/${encodeURIComponent(metric)}`)
      );
      const data = await response.json();

      if (data.data) {
        selectedMetrics.value.push(metric);
        currentSeries.value.push({
          name: metric,
          data: data.data
        });
      }
    }

    // Update chart
    if (chart.value && chart.value.updateSeries) {
      chart.value.updateSeries(currentSeries.value);
    }
  } catch (error) {
    console.error("Error toggling metric:", error);
  }
}

// Add current exploration to dashboard
async function addToDashboard() {
  try {
    const response = await fetch(getApiUrl("explorer/save"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        temp_graph_id: tempGraphId.value,
        metrics: selectedMetrics.value,
      }),
    });

    if (response.ok) {
      router.push("/experiments");
    }
  } catch (error) {
    console.error("Error adding to dashboard:", error);
  }
}

// Cancel exploration
async function cancelExploration() {
  try {
    await fetch(getApiUrl("explorer/cancel"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        temp_graph_id: tempGraphId.value,
      }),
    });
    router.push("/experiments");
  } catch (error) {
    console.error("Error canceling exploration:", error);
  }
}

// Lifecycle hooks
onMounted(() => {
  initializeExplorer();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", () => {});
  if (chart.value) {
    chart.value.destroy();
  }
});
</script>

<style scoped>
.explorer-layout {
  display: flex;
  min-height: 100vh;
  background-color: #191a23;
  color: white;
}

/* Main Navigation Sidebar */
.sidebar {
  width: 15rem;
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

/* Metrics Sidebar */
.metrics-sidebar {
  width: 16rem;
  background-color: #16161d;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  height: 100vh;
  overflow-y: auto;
  flex-shrink: 0;
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 40;
}

.metrics-sidebar .sidebar-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
  color: white;
}

.metrics-list {
  display: flex;
  flex-direction: column;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.metric-item:hover {
  color: white;
}

.metric-item:hover .checkmark {
  opacity: 1;
  filter: invert(80%);
}

.metric-name {
  font-size: 0.9rem;
}

.checkmark {
  width: 16px;
  height: 16px;
  filter: invert(60%);
  opacity: 0.8;
}

/* Main Content Area */
.explorer-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  min-width: 0;
  margin-left: 15rem; /* Offset for main navigation sidebar */
  margin-right: 16rem; /* Offset for metrics sidebar */
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
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

.explorer-graph {
  background-color: #1f202b;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  width: 100%;
  overflow: hidden;
}

.graph-title {
  font-size: 0.9rem;
  font-weight: 400;
  margin-bottom: 1rem;
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.7);
}

.chart-container {
  width: 100%;
  height: 350px;
  margin: 1rem 0;
  overflow: hidden;
}

.button-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.button-primary {
  padding: 0.625rem 1.25rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.button-primary:hover {
  background-color: #2563eb;
}

.button-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-secondary {
  padding: 0.625rem 1.25rem;
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: white;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.button-secondary:hover {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.25);
}
</style>
