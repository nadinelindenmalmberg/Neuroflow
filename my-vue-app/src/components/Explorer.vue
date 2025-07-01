<template>
  <div class="explorer-layout">
    <!-- Sidebar -->
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

    <!-- Main Content Area -->
    <main class="explorer-main">
      <div class="breadcrumb">
        <router-link to="/" class="breadcrumb-link">Dashboard</router-link>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-current">Explorer</span>
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
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import ApexCharts from "apexcharts";
import checkmarkIcon from "../assets/images/checkmark.svg";
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
      show: true,
      tools: {
        download: true,
        selection: true,
        zoom: true,
        zoomin: true,
        zoomout: true,
        pan: true,
        reset: true,
      },
    },
    height: 500,
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
    theme: "dark",
    y: {
      formatter: (val) =>
        val !== null && val !== undefined ? val.toFixed(0) : "",
    },
  },
  legend: {
    position: "bottom",
    horizontalAlign: "center",
    labels: { colors: "white" },
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
    tempGraphId.value = data.graph_id;
    metrics.value = data.available_metrics;

    // Initialize chart
    const chartElement = document.querySelector("#explorer-chart");
    if (chartElement) {
      chart.value = new ApexCharts(chartElement, {
        ...chartOptions,
        chart: {
          ...chartOptions.chart,
          width: chartElement.clientWidth,
        },
      });
      chart.value.render();

      // Update chart size when window resizes
      window.addEventListener("resize", () => {
        if (chart.value) {
          chart.value.updateOptions({
            chart: {
              ...chartOptions.chart,
              width: chartElement.clientWidth,
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

      if (data.series) {
        selectedMetrics.value.push(metric);
        currentSeries.value.push(data.series);
      }
    }

    // Update chart
    if (chart.value) {
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
        metrics: selectedMetrics.value,
      }),
    });

    if (response.ok) {
      router.push("/");
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
    });
    router.push("/");
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

.metrics-sidebar {
  width: 16rem;
  background-color: #16161d;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  height: 100vh;
  overflow-y: auto;
  flex-shrink: 0;
}

.sidebar-title {
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

.explorer-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  min-width: 0;
}

.breadcrumb {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

.breadcrumb-link {
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: white;
}

.breadcrumb-separator {
  color: rgba(255, 255, 255, 0.3);
}

.breadcrumb-current {
  color: white;
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
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.chart-container {
  width: 100%;
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
