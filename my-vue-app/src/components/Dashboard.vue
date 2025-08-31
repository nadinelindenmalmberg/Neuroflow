<template>
  <div>
    <div class="dashboard-layout">
      <!-- Sidebar -->
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
            <h1 class="page-title">Dashboard</h1>
            <div class="header-actions">
              <button class="button" @click="showNewGraphForm = true">
                + Add graph
              </button>
              <button class="button" @click="showAddDataForm = true">
                + Add datapoint
              </button>
            </div>
          </div>
        </div>

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

        <!-- Graphs Container -->
        <div class="graph-grid">
          <p v-if="graphs.length === 0">No user-created graphs found.</p>
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

        <!-- Add Data Form Modal -->
        <AddDataForm
          v-if="showAddDataForm"
          :is-visible="showAddDataForm"
          :graphs="graphs"
          @close="showAddDataForm = false"
          @data-added="handleDataAdded"
        />
      </main>
    </div>

    <!-- Graph Editor Modal -->
    <transition name="modal-fade">
      <GraphEditor
        v-if="showGraphEditor"
        :graph-id="selectedGraphId"
        @close="showGraphEditor = false"
        @updated="handleGraphUpdated"
      />
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import ApexCharts from "apexcharts";
import { marked } from "marked";
import { FlaskConical, BarChart3, Activity, GitBranch, Upload } from "lucide-vue-next";
import NewGraphForm from "./NewGraphForm.vue";
import AddDataForm from "./AddDataForm.vue";
import GraphEditor from "./GraphEditor.vue";
import { getApiUrl } from "../config";
import neuroflowLogo from "../assets/images/ChatGPT_Image_Apr_5__2025__01_36_36_PM-removebg-preview 1.svg";

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

/**
 * Function to load graphs and render charts
 */
async function loadGraphs() {
  try {
    const response = await fetch(getApiUrl("graphs"));
    const data = await response.json();
    graphs.value = data;
    nextTick(() => {
      renderCharts();
    });
  } catch (error) {
    console.error("Error loading graphs:", error);
  }
}

/**
 * Lifecycle hook (replacing mounted())
 * Fetch data from Flask API on component mount
 */
onMounted(() => {
  loadGraphs();
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

  graphs.value.forEach((graph, index) => {
    // Create a new options object by merging the base options with graph-specific data
    const options = {
      ...baseOptions,
      series: graph.figure || [],
    };

    const chartEl = document.querySelector(`#user-graph-${index}`);
    if (chartEl) {
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
    .catch((err) => console.error(err));
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

// Function to fetch graphs from the API
function fetchGraphs() {
  fetch(getApiUrl("graphs"))
    .then((res) => res.json())
    .then((data) => {
      graphs.value = data;
      nextTick(() => {
        renderCharts();
      });
    })
    .catch((err) => console.error("Error fetching graphs:", err));
}

function openGraphEditor(graphId) {
  console.log("Opening editor for graph:", graphId);
  router.push(`/edit-graph/${graphId}`);
}

function handleGraphUpdated() {
  // Refresh the graphs list
  fetch(getApiUrl("graphs"))
    .then((res) => res.json())
    .then((data) => {
      graphs.value = data;
      nextTick(() => {
        renderCharts();
      });
    })
    .catch((err) => console.error("Error fetching graphs:", err));
}
</script>

<style scoped>
.dashboard-layout {
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

/* Graph grid */
.graph-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1200px) {
  .graph-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Graph card */
.graph-card {
  background: #191a24;
  backdrop-filter: blur(16px);
  border: 1.25px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  margin: 12px auto;
  max-width: 700px;
  min-width: 0;
  overflow: hidden;
  position: relative;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.graph-header h3 {
  font-size: 0.9rem;
  font-weight: 400;
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
}

.graph-actions {
  display: flex;
  gap: 0.25rem;
}

.chart-container {
  flex: 1;
  min-height: 300px;
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

.icon-button,
.icon-button-wand {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  padding: 0.25rem;
  transition: all 0.2s ease;
  cursor: pointer;
  background: transparent;
  border: none;
  outline: none;
}

.icon-button img,
.icon-button-wand img {
  width: 1.125rem;
  height: 1.125rem;
  filter: invert(60%);
  background: transparent;
  border: none;
  outline: none;
  transition: filter 0.2s ease;
}

.icon-button:hover img,
.icon-button-wand:hover img {
  filter: invert(100%);
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
  background-color: #1f202b;
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  border-radius: 0.75rem;
  border: 1.5px solid rgba(255, 255, 255, 0.1);
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
  font-weight: bold;
  margin: 0;
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
}

.analysis-content h1,
.analysis-content h2,
.analysis-content h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
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

.hidden {
  display: none;
}

/* Add these new transition CSS rules at the end of the style section */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Ensure modals appear above everything */
:deep(.modal-overlay),
:deep(.fixed) {
  z-index: 9999;
}
</style>
