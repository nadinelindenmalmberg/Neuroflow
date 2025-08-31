<template>
  <div class="integration-layout">
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
        <router-link to="/explorer" class="nav-link">
          <Activity class="nav-icon" size="20" />
          <span>Explorer</span>
        </router-link>
        <router-link to="/integrations" class="nav-link">
          <GitBranch class="nav-icon" size="20" />
          <span>Integrations</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Breadcrumb Navigation -->
      <div class="breadcrumb">
        <router-link to="/integrations" class="breadcrumb-link">
          <ArrowLeft class="breadcrumb-icon" size="16" />
          Integrations
        </router-link>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-current">Oura</span>
      </div>

      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <div class="integration-info">
            <div class="integration-icon">
              <img src="../assets/images/oura_logo_logo.png" alt="Oura" class="logo" />
            </div>
            <div class="integration-details">
              <h1>Oura</h1>
              <p>Sync your Oura data to identify patterns in your sleep and compare against other metrics</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <button 
          class="tab-button" 
          :class="{ active: activeTab === 'configuration' }"
          @click="activeTab = 'configuration'"
        >
          Configuration
        </button>
        <button 
          class="tab-button" 
          :class="{ active: activeTab === 'logs' }"
          @click="activeTab = 'logs'"
        >
          Logs
        </button>
      </div>

      <!-- Tab Content -->
      <div v-if="activeTab === 'configuration'" class="tab-panel">
        <div class="config-card">
          <!-- API Configuration Section -->
          <div class="section">
            <h3 class="section-title">API Configuration</h3>
            
            <div class="form-group">
              <label for="token" class="form-label">API Token</label>
              <div class="token-input-wrapper">
                <input
                  type="text"
                  class="form-control"
                  id="token"
                  v-model="formData.token"
                  :type="showToken ? 'text' : 'password'"
                  placeholder="Enter your Oura API token"
                  @blur="handleTokenBlur"
                  required
                />
                <button 
                  type="button" 
                  class="token-toggle-btn"
                  @click="toggleTokenVisibility"
                  v-if="formData.token"
                >
                  <Eye v-if="!showToken" size="16" />
                  <EyeOff v-else size="16" />
                </button>
              </div>
            </div>

            <div class="form-group">
              <label for="sync_frequency" class="form-label">Sync Frequency</label>
              <select
                id="sync_frequency"
                v-model="formData.sync_frequency"
                class="form-control"
                @change="updateSyncFrequency"
              >
                <option value="manual">Manual only</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>

            <div class="form-group">
              <div class="checkbox-group">
                <input
                  type="checkbox"
                  id="sync_enabled"
                  v-model="formData.sync_enabled"
                  class="checkbox"
                  @change="updateSyncSchedule"
                />
                <label for="sync_enabled" class="checkbox-label">
                  Enable automatic sync
                </label>
              </div>
              <div class="form-help-text">
                When enabled, your data will be automatically synced based on the frequency above
              </div>
            </div>
          </div>

          <!-- Manual Sync Section -->
          <div class="section">
            <h3 class="section-title">Manual Sync</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label for="start_date" class="form-label">Start Date</label>
                <input
                  type="date"
                  class="form-control"
                  id="start_date"
                  v-model="formData.start_date"
                  required
                />
              </div>
              <div class="form-group">
                <label for="end_date" class="form-label">End Date</label>
                <input
                  type="date"
                  class="form-control"
                  id="end_date"
                  v-model="formData.end_date"
                  required
                />
              </div>
            </div>

                          <div class="sync-actions">
                <button
                  type="button"
                  class="button-primary"
                  @click="handleSubmit"
                  :disabled="isLoading || !formData.token"
                >
                  <RefreshCw v-if="isLoading" class="spinner" size="16" />
                  {{ isLoading ? "Syncing..." : "Sync Data" }}
                </button>
              </div>
          </div>
        </div>
      </div>

      <!-- Logs Tab -->
      <div v-if="activeTab === 'logs'" class="tab-panel">
        <div class="logs-card">
          <div class="logs-header">
            <h2>Sync History</h2>
            <button @click="refreshLogs" class="btn btn-secondary" :disabled="isLoadingLogs">
              <RefreshCw v-if="isLoadingLogs" class="icon" size="16" />
              <RefreshCw v-else class="icon" size="16" />
              Refresh
            </button>
          </div>

          <div class="logs-table">
            <div v-if="syncHistory.length === 0" class="empty-state">
              <p>No sync history available yet.</p>
            </div>

            <div v-else class="table">
              <div 
                v-for="sync in syncHistory" 
                :key="sync.id" 
                class="table-row"
                :class="{ expanded: expandedRows.includes(sync.id) }"
              >
                <div class="row-content" @click="toggleRow(sync.id)">
                  <div class="row-main">
                    <div class="sync-info">
                      <div class="sync-type">{{ sync.sync_type }}</div>
                      <div class="sync-status" :class="getStatusClass(sync.status)">
                        {{ sync.status }}
                      </div>
                      <div class="sync-dates">
                        {{ sync.start_date }} to {{ sync.end_date }}
                      </div>
                    </div>
                    <div class="row-actions">
                      <div class="sync-date">{{ formatDate(sync.started_at) }}</div>
                      <ChevronDown v-if="!expandedRows.includes(sync.id)" class="expand-icon" size="16" />
                      <ChevronUp v-else class="expand-icon" size="16" />
                    </div>
                  </div>
                </div>

                <div v-if="expandedRows.includes(sync.id)" class="row-details">
                  <div class="detail-grid">
                    <div class="detail-item">
                      <span class="detail-label">Records Imported:</span>
                      <span class="detail-value">{{ sync.records_imported || 0 }}</span>
                    </div>
                    <div class="detail-item" v-if="sync.duration_seconds">
                      <span class="detail-label">Duration:</span>
                      <span class="detail-value">{{ formatDuration(sync.duration_seconds) }}</span>
                    </div>
                    <div class="detail-item" v-if="sync.error_message">
                      <span class="detail-label">Error:</span>
                      <span class="detail-value error">{{ sync.error_message }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notifications -->
    <div class="toast-container">
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        <div class="toast-content">
          <span class="toast-message">{{ toast.message }}</span>
          <button class="toast-close" @click="removeToast(toast.id)">
            <X size="14" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getApiUrl } from "../config";
import { 
  FlaskConical, 
  BarChart3, 
  Activity, 
  GitBranch, 
  ArrowLeft, 
  RefreshCw, 
  ChevronDown, 
  ChevronUp,
  Eye,
  EyeOff,
  X
} from "lucide-vue-next";
import neuroflowLogo from "../assets/images/ChatGPT_Image_Apr_5__2025__01_36_36_PM-removebg-preview 1.svg";

const router = useRouter();
const activeTab = ref('configuration');
const formData = ref({
  token: "",
  start_date: "",
  end_date: "",
  sync_frequency: "manual",
  sync_enabled: false
});

const isLoading = ref(false);
const isLoadingLogs = ref(false);
const syncHistory = ref([]);
const hasToken = ref(false);
const expandedRows = ref([]);
const showToken = ref(false);
const toasts = ref([]);
const actualToken = ref(""); // Store the actual token separately

onMounted(async () => {
  await loadSyncStatus();
  await loadSyncHistory();
});

const loadSyncStatus = async () => {
  try {
    const response = await fetch(getApiUrl("integrations/oura/status"));
    if (response.ok) {
      const data = await response.json();
      hasToken.value = data.has_token;
      
      // Pre-fill the token field if it exists (will be masked)
      if (data.has_token && data.token) {
        formData.value.token = data.token;
        showToken.value = false; // Ensure token is masked by default
      }
      
      // Load sync frequency if available
      if (data.sync_frequency) {
        formData.value.sync_frequency = data.sync_frequency;
      }
    }
  } catch (error) {
    console.error("Error loading sync status:", error);
  }
  
  // Load sync schedule
  try {
    const scheduleResponse = await fetch(getApiUrl("integrations/oura/schedule"));
    if (scheduleResponse.ok) {
      const scheduleData = await scheduleResponse.json();
      formData.value.sync_enabled = scheduleData.sync_enabled || false;
    }
  } catch (error) {
    console.error("Error loading sync schedule:", error);
  }
};

const loadSyncHistory = async () => {
  isLoadingLogs.value = true;
  try {
    const response = await fetch(getApiUrl('integrations/oura/history'));
    if (response.ok) {
      const data = await response.json();
      syncHistory.value = data.sync_history || [];
    }
  } catch (error) {
    console.error('Error loading sync history:', error);
  } finally {
    isLoadingLogs.value = false;
  }
};

const refreshLogs = () => {
  loadSyncHistory();
};

const toggleRow = (id) => {
  const index = expandedRows.value.indexOf(id);
  if (index > -1) {
    expandedRows.value.splice(index, 1);
  } else {
    expandedRows.value.push(id);
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "Unknown";
  return new Date(dateString).toLocaleDateString();
};

const formatDuration = (seconds) => {
  if (!seconds) return "Unknown";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
};

const getStatusClass = (status) => {
  switch (status) {
    case 'success':
      return 'status-success';
    case 'failed':
      return 'status-failed';
    case 'in_progress':
      return 'status-progress';
    default:
      return 'status-unknown';
  }
};



const handleTokenBlur = async () => {
  if (formData.value.token && formData.value.token.trim()) {
    try {
      addToast('Saving token...', 'info');
      
      // Store the actual token and mask the display
      const tokenToSend = formData.value.token.trim();
      actualToken.value = tokenToSend; // Store actual token
      
      const response = await fetch(getApiUrl("integrations/oura/save-token"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json; charset=utf-8",
        },
        body: JSON.stringify({
          token: tokenToSend,
          remember_token: true,
        }),
      });

      if (response.ok) {
        addToast('Token saved successfully', 'success');
        hasToken.value = true;
        
        // Mask the display token
        formData.value.token = '********************************';
        showToken.value = false;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save token');
      }
    } catch (error) {
      console.error("Error saving token:", error);
      addToast('Failed to save token: ' + error.message, 'error');
    }
  } else if (formData.value.token === '') {
    addToast('Token is required', 'error');
  }
};

const updateSyncFrequency = async () => {
  try {
    const response = await fetch(getApiUrl("integrations/oura/settings"), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sync_frequency: formData.value.sync_frequency,
      }),
    });

    if (response.ok) {
      addToast('Sync frequency updated', 'success');
    } else {
      addToast('Failed to update sync frequency', 'error');
    }
  } catch (error) {
    console.error("Error updating sync frequency:", error);
    addToast('Failed to update sync frequency', 'error');
  }
};

const updateSyncSchedule = async () => {
  try {
    const response = await fetch(getApiUrl("integrations/oura/schedule"), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sync_enabled: formData.value.sync_enabled,
        sync_frequency: formData.value.sync_frequency,
      }),
    });

    if (response.ok) {
      const message = formData.value.sync_enabled 
        ? 'Automatic sync enabled' 
        : 'Automatic sync disabled';
      addToast(message, 'success');
    } else {
      addToast('Failed to update sync schedule', 'error');
    }
  } catch (error) {
    console.error("Error updating sync schedule:", error);
    addToast('Failed to update sync schedule', 'error');
  }
};

const handleSubmit = async () => {
  isLoading.value = true;

  try {
    // Update sync frequency
    const frequencyResponse = await fetch(getApiUrl("integrations/oura/settings"), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sync_frequency: formData.value.sync_frequency,
      }),
    });

    if (!frequencyResponse.ok) {
      console.warn("Failed to update sync frequency");
    }

    // Sync data - use actual token if available
    const syncResponse = await fetch(getApiUrl("integrations/oura/sync-now"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        start_date: formData.value.start_date,
        end_date: formData.value.end_date,
        token: actualToken.value || formData.value.token, // Use actual token if available
      }),
    });

    if (!syncResponse.ok) {
      const errorData = await syncResponse.json();
      throw new Error(errorData.error || "Failed to sync data");
    }

    const result = await syncResponse.json();
    addToast(`${result.message} (${result.records_imported} records imported)`, 'success');
    
    await loadSyncStatus();
    await loadSyncHistory();
  } catch (error) {
    console.error("Error syncing data:", error);
    addToast(error.message || "Failed to sync data. Please try again.", 'error');
  } finally {
    isLoading.value = false;
  }
};

const toggleTokenVisibility = () => {
  showToken.value = !showToken.value;
};

const addToast = (message, type = 'info') => {
  const id = Date.now();
  toasts.value.push({ id, message, type });
  setTimeout(() => removeToast(id), 5000); // Auto-remove after 5 seconds
};

const removeToast = (id) => {
  const index = toasts.value.findIndex(toast => toast.id === id);
  if (index > -1) {
    toasts.value.splice(index, 1);
  }
};
</script>

<style scoped>
.integration-layout {
  display: flex;
  min-height: 100vh;
  background-color: #191a23;
  color: white;
}

/* Sidebar */
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

/* Main Content */
.main-content {
  flex: 1;
  padding: 1.25rem;
  overflow-y: auto;
  margin-left: 15rem;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  font-size: 0.875rem;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: color 0.15s ease;
}

.breadcrumb-link:hover {
  color: rgba(255, 255, 255, 0.9);
}

.breadcrumb-icon {
  margin-right: 0.5rem;
}

.breadcrumb-separator {
  margin: 0 0.5rem;
  color: rgba(255, 255, 255, 0.3);
}

.breadcrumb-current {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
}

.integration-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.integration-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo {
  width: 32px;
  height: 32px;
  filter: invert(1);
}

.integration-details h1 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
}

.integration-details p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

/* Tabs */
.tabs {
  display: flex;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 2rem;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-button:hover {
  color: rgba(255, 255, 255, 0.9);
}

.tab-button.active {
  color: white;
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

/* Tab Content */
.tab-panel {
  min-height: 400px;
}

/* Cards */
.config-card,
.logs-card {
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

.config-card h2,
.logs-card h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
}

.config-card p {
  margin: 0 0 2rem 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}



/* Form */
.config-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
}

.form-control {
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background-color: rgba(255, 255, 255, 0.05);
  color: white;
  transition: border-color 0.15s ease;
}

.form-control:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox {
  width: 1rem;
  height: 1rem;
}

.checkbox-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
}

.form-help-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.25rem;
  line-height: 1.4;
}

/* Buttons */
.form-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  color: white;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  gap: 0.5rem;
}

.btn-primary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-primary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-primary:disabled {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-secondary:disabled {
  background: rgba(255, 255, 255, 0.02);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Alerts */
.alert {
  padding: 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  margin-top: 1rem;
}

.alert-error {
  background: rgba(220, 38, 38, 0.2);
  color: #f87171;
  border: 1px solid rgba(220, 38, 38, 0.3);
}

.alert-success {
  background: rgba(5, 150, 105, 0.2);
  color: #4ade80;
  border: 1px solid rgba(5, 150, 105, 0.3);
}

/* Logs */
.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.logs-table {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
  overflow: hidden;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
}

.table {
  background: #191a24;
}

.table-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-row:last-child {
  border-bottom: none;
}

.row-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.row-content:hover {
  background: rgba(255, 255, 255, 0.05);
}

.row-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sync-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sync-type {
  font-weight: 500;
  color: white;
  text-transform: capitalize;
}

.sync-status {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.sync-status.status-success {
  background: rgba(5, 150, 105, 0.2);
  color: #4ade80;
}

.sync-status.status-failed {
  background: rgba(220, 38, 38, 0.2);
  color: #f87171;
}

.sync-status.status-progress {
  background: rgba(217, 119, 6, 0.2);
  color: #fbbf24;
}

.sync-status.status-info {
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
}

.sync-dates {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sync-date {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}

.expand-icon {
  color: rgba(255, 255, 255, 0.5);
  transition: transform 0.15s ease;
}

.row-details {
  background: rgba(255, 255, 255, 0.02);
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.detail-value {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
}

.detail-value.error {
  color: #f87171;
}

.icon {
  color: currentColor;
}

/* New styles for token input */
.token-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.token-input-wrapper .form-control {
  width: 100%;
  padding-right: 3rem; /* Make room for the toggle button */
}

.token-toggle-btn {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.15s ease;
  z-index: 10;
}

.token-toggle-btn:hover {
  color: rgba(255, 255, 255, 0.8);
}

.token-status {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  padding: 0.4rem 0.8rem;
  border-radius: 0.375rem;
  font-weight: 500;
}

.token-status.success {
  background-color: rgba(5, 150, 105, 0.1);
  color: #4ade80;
  border: 1px solid rgba(5, 150, 105, 0.2);
}

.token-status.error {
  background-color: rgba(220, 38, 38, 0.1);
  color: #f87171;
  border: 1px solid rgba(220, 38, 38, 0.2);
}

.token-status.info {
  background-color: rgba(100, 116, 139, 0.1);
  color: #94a3b8;
  border: 1px solid rgba(100, 116, 139, 0.2);
}

.section {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.sync-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.button-primary {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  color: white;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.button-primary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.button-primary:disabled {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
}

/* Toast Notifications */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast {
  background-color: rgba(22, 22, 29, 0.95);
  color: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 200px;
  max-width: 300px;
  font-size: 0.875rem;
  backdrop-filter: blur(8px);
}

.toast.info {
  border-color: rgba(59, 130, 246, 0.4);
  background-color: rgba(59, 130, 246, 0.1);
}

.toast.success {
  border-color: rgba(34, 197, 94, 0.4);
  background-color: rgba(34, 197, 94, 0.1);
}

.toast.error {
  border-color: rgba(239, 68, 68, 0.4);
  background-color: rgba(239, 68, 68, 0.1);
}

.toast.warning {
  border-color: rgba(245, 158, 11, 0.4);
  background-color: rgba(245, 158, 11, 0.1);
}

.toast-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.toast-message {
  flex-grow: 1;
  margin-right: 8px;
}

.toast-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 2px;
  border-radius: 3px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-close:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}
</style>
