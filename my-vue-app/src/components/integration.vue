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
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">Device Integrations</h1>
          <p class="hero-subtitle">
            Connect your health devices to automatically sync data and gain deeper insights
          </p>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <main class="main-content">
      <div class="integrations-container">
        <div class="section-header">
          <h2 class="section-title">Available Integrations</h2>
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
    </main>

    <!-- Metric Selection Modal -->
    <MetricSelectionModal
      :is-visible="showMetricSelection"
      :device-name="selectedDevice?.name || ''"
      :available-metrics="selectedDevice?.availableMetrics || []"
      :selected-metrics="selectedDevice?.selectedMetrics || []"
      @close="closeMetricSelection"
      @save="saveMetricSelection"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Watch, Zap, Shield, Apple, Activity, Heart, CheckCircle, AlertCircle, Info, X } from 'lucide-vue-next'
import DeviceIntegrationCard from './DeviceIntegrationCard.vue'
import MetricSelectionModal from './MetricSelectionModal.vue'

// Device integrations data - will be populated from API
const deviceIntegrations = ref([])
const availableMetrics = ref({})
const selectedMetrics = ref({})

// Metric selection modal state
const showMetricSelection = ref(false)
const selectedDevice = ref(null)

// Toast notification system
const toasts = ref([])

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

// Load integrations data from API
async function loadIntegrations() {
  try {
    const response = await fetch('http://localhost:5174/api/integrations/status')
    const data = await response.json()
    
    if (data.integrations) {
      deviceIntegrations.value = data.integrations.map(integration => ({
        name: integration.name,
        logo: getDeviceLogo(integration.name),
        connected: integration.connected,
        lastSync: integration.last_sync ? formatLastSync(integration.last_sync) : "Never",
        metrics: integration.available_metrics,
        syncFrequency: integration.sync_frequency === 'manual' ? 'Manual' : integration.sync_frequency,
        dataPoints: integration.data_points,
        selectedMetrics: selectedMetrics.value[integration.name.toLowerCase()] || [],
        availableMetrics: getAvailableMetricsForDevice(integration.name)
      }))
    }
  } catch (error) {
    console.error('Error loading integrations:', error)
  }
}

// Load available metrics from API
async function loadAvailableMetrics() {
  try {
    const response = await fetch('http://localhost:5174/api/dashboard/metrics/available')
    const data = await response.json()
    availableMetrics.value = data
  } catch (error) {
    console.error('Error loading available metrics:', error)
  }
}

// Load selected metrics from API
async function loadSelectedMetrics() {
  try {
    const response = await fetch('http://localhost:5174/api/dashboard/metrics/selected')
    const data = await response.json()
    selectedMetrics.value = data.selected_metrics || {}
  } catch (error) {
    console.error('Error loading selected metrics:', error)
  }
}

// Helper functions
function getDeviceLogo(deviceName) {
  const logos = {
    'Oura Ring': Zap,
    'Fitbit': Activity,
    'Garmin Connect': Watch,
    'WHOOP': Shield
  }
  return logos[deviceName] || Activity
}

function formatLastSync(lastSync) {
  const date = new Date(lastSync)
  const now = new Date()
  const diffMs = now - date
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffDays > 0) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  } else if (diffHours > 0) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  } else {
    return 'Just now'
  }
}

function getAvailableMetricsForDevice(deviceName) {
  // Map device names to the keys used in availableMetrics API
  const deviceKeyMap = {
    'Oura Ring': 'oura',
    'Garmin Connect': 'garmin', 
    'WHOOP': 'whoop'
  }
  const deviceKey = deviceKeyMap[deviceName] || deviceName.toLowerCase().replace(' ', '_')
  return availableMetrics.value[deviceKey] || []
}

// Helper function to format metric names for display
function formatMetricName(metricName) {
  const exceptions = {
    hrv: "HRV",
    vo2: "VO2",
    rem: "REM"
  };
  
  // Replace underscores with spaces and capitalize words
  let formatted = metricName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  
  // Apply exceptions
  Object.entries(exceptions).forEach(([key, value]) => {
    const regex = new RegExp(`\\b${key}\\b`, 'gi');
    formatted = formatted.replace(regex, value);
  });
  
  return formatted;
}

// Device connection handlers
async function handleDeviceConnect(device) {
  console.log("Connecting to device:", device.name)
  
  if (device.name === 'Fitbit') {
    try {
      // Get Fitbit OAuth URL
      const response = await fetch('http://localhost:5174/api/integrations/fitbit/auth-url')
      const data = await response.json()
      
      if (response.ok && data.auth_url) {
        console.log("Redirecting to Fitbit OAuth:", data.auth_url)
        // Open Fitbit OAuth in new window
        window.open(data.auth_url, 'fitbit-oauth', 'width=600,height=700,scrollbars=yes,resizable=yes')
        
        // Show instructions to user
        alert("✅ Fitbit OAuth window opened! Complete the authorization and return here. The page will refresh automatically.")
        
        // Refresh integrations after a delay to check for new connection
        setTimeout(async () => {
          await loadDeviceIntegrations()
        }, 3000)
      } else {
        throw new Error(data.error || 'Failed to get Fitbit auth URL')
      }
    } catch (error) {
      console.error('Fitbit connection error:', error)
      alert(`❌ Failed to connect to Fitbit: ${error.message}`)
    }
  } else {
    // For other devices, use placeholder behavior
    device.connected = true
    device.lastSync = "Just now"
  }
}

async function handleDeviceDisconnect(device) {
  console.log("Disconnecting from device:", device.name)
  
  if (device.name === 'Fitbit') {
    try {
      const response = await fetch('http://localhost:5174/api/integrations/fitbit/disconnect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Fitbit disconnected:', result)
        alert(`✅ ${device.name} disconnected successfully!`)
        
        // Reload integrations to get updated status
        await loadIntegrations()
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Disconnect failed')
      }
    } catch (error) {
      console.error('Fitbit disconnect error:', error)
      alert(`❌ Failed to disconnect from Fitbit: ${error.message}`)
    }
  } else {
    // For other devices, use placeholder behavior
    device.connected = false
    device.lastSync = "Disconnected"
  }
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
      await loadIntegrations()
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

// Metric selection handlers
function handleSelectMetrics(device) {
  selectedDevice.value = device
  showMetricSelection.value = true
}

function closeMetricSelection() {
  showMetricSelection.value = false
  selectedDevice.value = null
}

async function saveMetricSelection(selectedMetricsList) {
  if (selectedDevice.value) {
    try {
      const response = await fetch('http://localhost:5174/api/dashboard/metrics/selected', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_name: selectedDevice.value.name,
          selected_metrics: selectedMetricsList
        })
      })
      
      if (response.ok) {
        selectedDevice.value.selectedMetrics = selectedMetricsList.map(metric => metric.name)
        console.log(`Saved ${selectedMetricsList.length} metrics for ${selectedDevice.value.name}`)
        // Reload selected metrics
        await loadSelectedMetrics()
      }
    } catch (error) {
      console.error('Error saving metrics:', error)
    }
  }
}

// Load data on component mount
onMounted(async () => {
  await loadAvailableMetrics()
  await loadSelectedMetrics()
  await loadIntegrations()
})
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 4rem 1rem;
  overflow: hidden;
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

/* Main Content */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1rem;
}

.integrations-container {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  color: white;
  margin: 0 0 1rem 0;
}

.section-description {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  max-width: 600px;
  margin: 0 auto;
}

/* Integrations Grid */
.integrations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 4rem;
}

/* Additional Integrations */
.additional-integrations {
  margin-top: 4rem;
}

.subsection-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 2rem 0;
  text-align: center;
}

.coming-soon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.coming-soon-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  opacity: 0.6;
}

.coming-soon-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.02) 0%, transparent 50%);
  pointer-events: none;
}

.coming-soon-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
  opacity: 0.8;
}

.coming-soon-icon {
  width: 4rem;
  height: 4rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.coming-soon-icon .icon {
  width: 2rem;
  height: 2rem;
  color: rgba(255, 255, 255, 0.6);
}

.coming-soon-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.75rem 0;
}

.coming-soon-description {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.5;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .section-description {
    font-size: 1rem;
  }
  
  .integrations-grid {
    grid-template-columns: 1fr;
  }
  
  .coming-soon-grid {
    grid-template-columns: 1fr;
  }
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

/* Mobile responsive */
@media (max-width: 640px) {
  .toast-container {
    top: 0.5rem;
    right: 0.5rem;
    left: 0.5rem;
    max-width: none;
  }
  
  .toast {
    padding: 0.875rem;
  }
  
  .toast-title {
    font-size: 0.8125rem;
  }
  
  .toast-message {
    font-size: 0.75rem;
  }
}
</style>
