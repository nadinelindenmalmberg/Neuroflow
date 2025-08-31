<template>
  <div class="sync-history">
    <div class="history-header">
      <h3>Sync History</h3>
      <div class="history-stats" v-if="historyStats">
        <span class="stat-item">
          <span class="stat-label">Total:</span>
          <span class="stat-value">{{ historyStats.total_syncs }}</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">Successful:</span>
          <span class="stat-value success">{{ historyStats.successful_syncs }}</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">Failed:</span>
          <span class="stat-value error">{{ historyStats.failed_syncs }}</span>
        </span>
      </div>
    </div>

    <div class="history-list" v-if="syncHistory.length > 0">
      <div 
        v-for="sync in syncHistory" 
        :key="sync.id" 
        class="history-item"
        :class="getStatusClass(sync.status)"
      >
        <div class="sync-header">
          <div class="sync-info">
            <span class="sync-type">{{ sync.sync_type }}</span>
            <span class="sync-date">{{ formatDate(sync.started_at) }}</span>
          </div>
          <div class="sync-status">
            <span class="status-badge" :class="getStatusClass(sync.status)">
              {{ sync.status }}
            </span>
          </div>
        </div>
        
        <div class="sync-details">
          <div class="detail-row">
            <span class="detail-label">Date Range:</span>
            <span class="detail-value">{{ sync.start_date }} to {{ sync.end_date }}</span>
          </div>
          
          <div class="detail-row" v-if="sync.records_imported !== null">
            <span class="detail-label">Records Imported:</span>
            <span class="detail-value">{{ sync.records_imported }}</span>
          </div>
          
          <div class="detail-row" v-if="sync.duration_seconds !== null">
            <span class="detail-label">Duration:</span>
            <span class="detail-value">{{ formatDuration(sync.duration_seconds) }}</span>
          </div>
          
          <div class="detail-row" v-if="sync.error_message">
            <span class="detail-label">Error:</span>
            <span class="detail-value error">{{ sync.error_message }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-history">
      <p>No sync history available yet.</p>
    </div>

    <div class="history-actions">
      <button 
        @click="refreshHistory" 
        class="btn btn-secondary"
        :disabled="isLoading"
      >
        <span v-if="isLoading">Loading...</span>
        <span v-else>Refresh History</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getApiUrl } from '../config';

const syncHistory = ref([]);
const historyStats = ref(null);
const isLoading = ref(false);

onMounted(() => {
  loadSyncHistory();
});

const loadSyncHistory = async () => {
  isLoading.value = true;
  try {
    const response = await fetch(getApiUrl('integrations/oura/history'));
    if (response.ok) {
      const data = await response.json();
      syncHistory.value = data.sync_history || [];
      historyStats.value = {
        total_syncs: data.total_syncs || 0,
        successful_syncs: data.successful_syncs || 0,
        failed_syncs: data.failed_syncs || 0
      };
    }
  } catch (error) {
    console.error('Error loading sync history:', error);
  } finally {
    isLoading.value = false;
  }
};

const refreshHistory = () => {
  loadSyncHistory();
};

// Expose the refreshHistory function to parent components
defineExpose({
  refreshHistory
});

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown';
  return new Date(dateString).toLocaleString();
};

const formatDuration = (seconds) => {
  if (!seconds) return 'Unknown';
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
</script>

<style scoped>
.sync-history {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.history-header h3 {
  margin: 0;
  color: #fff;
  font-size: 1.2rem;
}

.history-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 0.8rem;
  color: #ccc;
}

.stat-value {
  font-weight: 600;
  color: #fff;
}

.stat-value.success {
  color: #10b981;
}

.stat-value.error {
  color: #ef4444;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 10px;
  border-left: 4px solid transparent;
}

.history-item.status-success {
  border-left-color: #10b981;
}

.history-item.status-failed {
  border-left-color: #ef4444;
}

.history-item.status-progress {
  border-left-color: #f59e0b;
}

.sync-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.sync-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sync-type {
  font-weight: 600;
  color: #fff;
  text-transform: capitalize;
}

.sync-date {
  font-size: 0.9rem;
  color: #ccc;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.status-success {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.status-badge.status-failed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.status-badge.status-progress {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.sync-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.detail-label {
  font-size: 0.9rem;
  color: #ccc;
  font-weight: 500;
}

.detail-value {
  font-size: 0.9rem;
  color: #fff;
}

.detail-value.error {
  color: #ef4444;
}

.no-history {
  text-align: center;
  padding: 40px 20px;
  color: #ccc;
}

.history-actions {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

.btn-secondary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
</style> 