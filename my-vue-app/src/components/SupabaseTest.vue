<template>
  <div class="supabase-test">
    <div class="test-header">
      <h3>🔍 Supabase Connection Test</h3>
      <button @click="runTest" :disabled="isLoading" class="test-button">
        {{ isLoading ? 'Testing...' : 'Test Connection' }}
      </button>
    </div>
    
    <div v-if="testResult" class="test-results">
      <div :class="['result-status', testResult.success ? 'success' : 'error']">
        {{ testResult.success ? '✅ Connection Successful' : '❌ Connection Failed' }}
      </div>
      
      <div v-if="testResult.success" class="success-details">
        <p><strong>Query Time:</strong> {{ testResult.queryTime?.toFixed(2) }}ms</p>
        <p><strong>Records Found:</strong> {{ testResult.recordCount }}</p>
        
        <div v-if="testResult.sampleData?.length > 0" class="sample-data">
          <h4>Sample Data:</h4>
          <pre>{{ JSON.stringify(testResult.sampleData, null, 2) }}</pre>
        </div>
      </div>
      
      <div v-else class="error-details">
        <p><strong>Error:</strong> {{ testResult.error }}</p>
        <div class="fix-instructions">
          <h4>How to Fix:</h4>
          <ol>
            <li>Go to your <a href="https://***REMOVED***m/dashboard" target="_blank">Supabase Dashboard</a></li>
            <li>Select your project</li>
            <li>Go to Settings → API</li>
            <li>Copy your Project URL and anon key</li>
            <li>Update your .env file with the real values</li>
            <li>Restart your dev server</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { testSupabaseRuntime } from '../utils/supabaseRuntimeTest.js'

const isLoading = ref(false)
const testResult = ref(null)

async function runTest() {
  isLoading.value = true
  testResult.value = null
  
  try {
    const result = await testSupabaseRuntime()
    testResult.value = result
  } catch (error) {
    testResult.value = {
      success: false,
      error: error.message
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.supabase-test {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.test-header h3 {
  margin: 0;
  color: #60a5fa;
  font-size: 1.1rem;
}

.test-button {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.test-button:hover:not(:disabled) {
  background: #2563eb;
}

.test-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.test-results {
  margin-top: 1rem;
}

.result-status {
  padding: 0.75rem;
  border-radius: 6px;
  font-weight: 500;
  margin-bottom: 1rem;
}

.result-status.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.result-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.success-details p {
  margin: 0.5rem 0;
  color: #e5e7eb;
}

.sample-data {
  margin-top: 1rem;
}

.sample-data h4 {
  margin: 0 0 0.5rem 0;
  color: #d1d5db;
  font-size: 0.9rem;
}

.sample-data pre {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 0.75rem;
  font-size: 0.8rem;
  color: #e5e7eb;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.error-details p {
  color: #fca5a5;
  margin: 0.5rem 0;
}

.fix-instructions {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
}

.fix-instructions h4 {
  margin: 0 0 0.5rem 0;
  color: #60a5fa;
  font-size: 0.9rem;
}

.fix-instructions ol {
  margin: 0;
  padding-left: 1.5rem;
  color: #d1d5db;
  font-size: 0.9rem;
}

.fix-instructions li {
  margin: 0.25rem 0;
}

.fix-instructions a {
  color: #60a5fa;
  text-decoration: none;
}

.fix-instructions a:hover {
  text-decoration: underline;
}
</style>

