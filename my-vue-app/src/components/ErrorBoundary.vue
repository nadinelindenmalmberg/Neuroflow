<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <div class="error-icon">⚠️</div>
      <h2>Something went wrong</h2>
      <p>{{ errorMessage }}</p>
      <div class="error-actions">
        <button @click="retry" class="retry-button">Try Again</button>
        <button @click="reportError" class="report-button">Report Issue</button>
      </div>
      <details v-if="errorDetails" class="error-details">
        <summary>Technical Details</summary>
        <pre>{{ errorDetails }}</pre>
      </details>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'

const hasError = ref(false)
const errorMessage = ref('')
const errorDetails = ref('')

onErrorCaptured((error, instance, info) => {
  console.error('Error caught by boundary:', error)
  console.error('Component instance:', instance)
  console.error('Error info:', info)
  
  hasError.value = true
  errorMessage.value = error.message || 'An unexpected error occurred'
  errorDetails.value = `${error.stack}\n\nComponent: ${info}`
  
  // Prevent error from propagating
  return false
})

function retry() {
  hasError.value = false
  errorMessage.value = ''
  errorDetails.value = ''
}

function reportError() {
  // In a real app, you'd send this to an error reporting service
  console.error('Error reported:', {
    message: errorMessage.value,
    details: errorDetails.value,
    timestamp: new Date().toISOString()
  })
  
  // For now, just show an alert
  alert('Error has been logged. Thank you for reporting!')
}
</script>

<style scoped>
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #dc3545;
}

.error-content {
  text-align: center;
  max-width: 500px;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-content h2 {
  color: #dc3545;
  margin-bottom: 1rem;
}

.error-content p {
  color: #6c757d;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.retry-button,
.report-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button {
  background: #007bff;
  color: white;
}

.retry-button:hover {
  background: #0056b3;
}

.report-button {
  background: #6c757d;
  color: white;
}

.report-button:hover {
  background: #545b62;
}

.error-details {
  text-align: left;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 1rem;
}

.error-details summary {
  cursor: pointer;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.error-details pre {
  background: #2d3748;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.8rem;
  line-height: 1.4;
  margin: 0;
}
</style>

