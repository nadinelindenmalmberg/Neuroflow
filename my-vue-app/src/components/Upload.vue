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
          <router-link to="/upload" class="nav-link router-link-active">
            <Upload class="nav-icon" size="20" />
            <span>Upload</span>
          </router-link>
        </nav>
      </aside>

      <!-- Main Content Area -->
      <main class="main-content">
        <!-- Page Title -->
        <div class="page-header">
          <h1 class="page-title">Upload</h1>
        </div>

        <!-- Upload Form -->
        <div class="upload-form">
          <div class="form-group">
            <label for="notes" class="form-label">Notes</label>
            <textarea
              id="notes"
              v-model="notes"
              class="notes-textarea"
              placeholder="Paste your notes here...&#10;&#10;Examples:&#10;Sleep: 7.5 hours&#10;Mood: 8/10&#10;Workout: 45 min cardio"
              rows="12"
            ></textarea>
          </div>

          <div class="form-actions">
            <button 
              @click="processNotes" 
              :disabled="!notes.trim() || isProcessing"
              class="button primary"
            >
              <span v-if="isProcessing">Processing...</span>
              <span v-else>Process</span>
            </button>
          </div>
        </div>

        <!-- Processing Status -->
        <div v-if="isProcessing" class="processing-status">
          <div class="spinner"></div>
          <p>AI is analyzing your notes...</p>
        </div>

        <!-- Clarification Questions -->
        <div v-if="clarificationQuestions.length > 0" class="clarification-section">
          <h3>Clarification Needed</h3>
          <p class="clarification-description">
            Please clarify the following:
          </p>
          
          <div class="questions-list">
            <div 
              v-for="(question, index) in clarificationQuestions" 
              :key="index" 
              class="question-item"
            >
              <label class="question-label">{{ question }}</label>
              <input 
                v-model="clarificationAnswers[index]" 
                type="text" 
                class="clarification-input"
                :placeholder="`Answer for: ${question}`"
              />
            </div>
          </div>

          <div class="clarification-actions">
            <button @click="submitClarifications" class="button primary">
              Submit Clarifications
            </button>
            <button @click="clearClarifications" class="button secondary">
              Cancel
            </button>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <!-- Structured Data Preview -->
        <div v-if="structuredData.length > 0" class="data-preview">
          <h3>Preview ({{ structuredData.length }} metrics)</h3>
          <p class="preview-description">
            Review and confirm:
          </p>
          
          <div class="data-table">
            <div class="table-header">
              <div class="header-cell">Metric</div>
              <div class="header-cell">Value</div>
              <div class="header-cell">Unit</div>
              <div class="header-cell">Date</div>
            </div>
            
            <div 
              v-for="(item, index) in structuredData" 
              :key="index" 
              class="table-row"
            >
              <div class="table-cell">{{ item.metric_name }}</div>
              <div class="table-cell">{{ item.value }}</div>
              <div class="table-cell">{{ item.unit }}</div>
              <div class="table-cell">{{ item.date }}</div>
            </div>
          </div>

          <div class="preview-actions">
            <button @click="saveToDatabase" class="button primary">
              Save
            </button>
            <button @click="clearData" class="button secondary">
              Clear
            </button>
          </div>
        </div>

        <!-- Toast Notifications -->
        <div class="toast-container">
          <div 
            v-for="toast in toasts" 
            :key="toast.id" 
            :class="['toast', `toast-${toast.type}`]"
            @click="removeToast(toast.id)"
          >
            {{ toast.message }}
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getApiUrl } from '../config.js'
import { FlaskConical, BarChart3, Activity, GitBranch, Upload } from "lucide-vue-next"
import neuroflowLogo from "../assets/images/ChatGPT_Image_Apr_5__2025__01_36_36_PM-removebg-preview 1.svg"

const notes = ref('')
const isProcessing = ref(false)
const errorMessage = ref('')
const structuredData = ref([])
const clarificationQuestions = ref([])
const clarificationAnswers = ref([])
const toasts = ref([])

const processNotes = async () => {
  if (!notes.value.trim()) return

  isProcessing.value = true
  errorMessage.value = ''
  
  // Check if this is a large dataset
  const notesLength = notes.value.trim().length
  const isLargeDataset = notesLength > 3000
  
  if (isLargeDataset) {
    addToast('info', `Processing large dataset (${notesLength} characters). This may take a few moments...`)
  }

  try {
    const response = await fetch(getApiUrl('upload/process-notes'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        notes: notes.value.trim()
      }),
    })

    if (response.ok) {
      const result = await response.json()
      console.log('Processing result:', result)
      
      if (result.needs_clarification) {
        // Show clarification questions
        clarificationQuestions.value = result.questions
        clarificationAnswers.value = new Array(result.questions.length).fill('')
        errorMessage.value = ''
      } else if (result.success && result.structured_data) {
        structuredData.value = result.structured_data
        
        // Show success message with chunk info if available
        if (result.chunks_processed) {
          addToast('success', `Successfully processed ${result.count} data points from ${result.chunks_processed} chunks!`)
        } else {
          addToast('success', `Successfully processed ${result.count} data points!`)
        }
        
        errorMessage.value = ''
      } else {
        errorMessage.value = result.error || 'Failed to process notes'
      }
    } else {
      const error = await response.json()
      errorMessage.value = error.message || 'Failed to process notes'
    }
  } catch (error) {
    console.error('Error processing notes:', error)
    errorMessage.value = 'Failed to process notes. Please try again.'
  } finally {
    isProcessing.value = false
  }
}

const saveToDatabase = async () => {
  if (!structuredData.value.length) {
    errorMessage.value = 'No data to save'
    return
  }

  try {
    const response = await fetch(getApiUrl('upload/save-data'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        structured_data: structuredData.value
      }),
    })

    if (response.ok) {
      const result = await response.json()
      console.log('Save result:', result)
      
      // Show success message
      addToast('success', result.message || 'Data saved successfully!')
      
      // Clear the form
      clearData()
    } else {
      const error = await response.json()
      errorMessage.value = error.error || 'Failed to save data'
      addToast('error', error.error || 'Failed to save data')
    }
  } catch (error) {
    console.error('Error saving data:', error)
    errorMessage.value = 'Failed to save data. Please try again.'
    addToast('error', 'Failed to save data. Please try again.')
  }
}

const clearData = () => {
  notes.value = ''
  structuredData.value = []
  errorMessage.value = ''
  clarificationQuestions.value = []
  clarificationAnswers.value = []
}

const submitClarifications = async () => {
  isProcessing.value = true
  errorMessage.value = ''

  try {
    // Format clarifications as a string
    const clarificationsText = clarificationQuestions.value.map((question, index) => {
      return `Q: ${question}\nA: ${clarificationAnswers.value[index] || 'Not specified'}`
    }).join('\n\n')

    const response = await fetch(getApiUrl('upload/process-notes'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        notes: notes.value.trim(),
        clarifications: clarificationsText
      }),
    })

    if (response.ok) {
      const result = await response.json()
      console.log('Structuring result:', result)
      
      if (result.success && result.structured_data) {
        structuredData.value = result.structured_data
        clarificationQuestions.value = []
        clarificationAnswers.value = []
        errorMessage.value = ''
      } else {
        errorMessage.value = result.error || 'Failed to structure data'
      }
    } else {
      const error = await response.json()
      errorMessage.value = error.message || 'Failed to submit clarifications'
    }
  } catch (error) {
    console.error('Error submitting clarifications:', error)
    errorMessage.value = 'Failed to submit clarifications. Please try again.'
  } finally {
    isProcessing.value = false
  }
}

const clearClarifications = () => {
  clarificationQuestions.value = []
  clarificationAnswers.value = []
  errorMessage.value = ''
}

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
.dashboard-layout {
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
  color: rgba(255, 255, 255, 0.9);
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 1.25rem;
  overflow-y: auto;
  margin-left: 15rem; /* Match expanded sidebar width */
}

/* Page Header */
.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.875rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

/* Toast Notifications */
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toast {
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 250px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.toast:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.1), 0 4px 6px -1px rgba(0, 0, 0, 0.06);
}

.toast-success {
  background-color: #10b981;
}

.toast-error {
  background-color: #ef4444;
}

.toast-info {
  background-color: #3b82f6;
}

.upload-form {
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.notes-textarea {
  width: 100%;
  min-height: 300px;
  padding: 1rem;
  background: #111827;
  border: 1px solid #374151;
  border-radius: 0.375rem;
  color: #ffffff;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  resize: vertical;
}

.notes-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.notes-textarea::placeholder {
  color: #6b7280;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.button.primary {
  background: #3b82f6;
  color: #ffffff;
}

.button.primary:hover:not(:disabled) {
  background: #2563eb;
}

.button.primary:disabled {
  background: #6b7280;
  cursor: not-allowed;
}

.processing-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 0.5rem;
  color: #9ca3af;
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #374151;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  padding: 1rem;
  background: #dc2626;
  color: #ffffff;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.data-preview {
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.data-preview h3 {
  color: #ffffff;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.preview-description {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.data-table {
  background: #111827;
  border: 1px solid #374151;
  border-radius: 0.375rem;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  background: #374151;
  padding: 0.75rem;
  font-weight: 600;
  color: #ffffff;
  font-size: 0.875rem;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  border-bottom: 1px solid #374151;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 0.75rem;
  color: #ffffff;
  font-size: 0.875rem;
}

.table-cell:not(:last-child) {
  border-right: 1px solid #374151;
}

.preview-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.button.secondary {
  background: #6b7280;
  color: #ffffff;
}

.button.secondary:hover {
  background: #4b5563;
}

.clarification-section {
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.clarification-section h3 {
  color: #ffffff;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.clarification-description {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.questions-list {
  margin-bottom: 1.5rem;
}

.question-item {
  margin-bottom: 1rem;
}

.question-label {
  display: block;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.clarification-input {
  width: 100%;
  padding: 0.75rem;
  background: #111827;
  border: 1px solid #374151;
  border-radius: 0.375rem;
  color: #ffffff;
  font-size: 0.875rem;
}

.clarification-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.clarification-input::placeholder {
  color: #6b7280;
}

.clarification-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}
</style> 