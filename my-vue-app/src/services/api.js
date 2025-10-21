/**
 * Centralized API service for all backend communication
 * Handles error handling, environment management, and request/response processing
 */

// Environment configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5174'

/**
 * Generic API request handler with error handling
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  }

  try {
    const response = await fetch(url, { ...defaultOptions, ...options })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }
    
    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error(`API Request failed for ${endpoint}:`, error)
    return { 
      success: false, 
      error: error.message,
      data: null 
    }
  }
}

/**
 * Experiments API
 */
export const experimentsApi = {
  // Get all experiments with their stats in a single request
  async getAll() {
    return await apiRequest('/api/experiments')
  },

  // Get experiments with stats (batch loading)
  async getAllWithStats() {
    return await apiRequest('/api/experiments/with-stats')
  },

  // Get single experiment
  async getById(id) {
    return await apiRequest(`/api/experiments/${id}`)
  },

  // Create experiment
  async create(experimentData) {
    return await apiRequest('/api/experiments', {
      method: 'POST',
      body: JSON.stringify(experimentData)
    })
  },

  // Update experiment
  async update(id, experimentData) {
    return await apiRequest(`/api/experiments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(experimentData)
    })
  },

  // Delete experiment
  async delete(id) {
    return await apiRequest(`/api/experiments/${id}`, {
      method: 'DELETE'
    })
  },

  // Get experiment stats
  async getStats(id) {
    return await apiRequest(`/api/experiments/${id}/stats`)
  },

  // Complete experiment
  async complete(id, completionData) {
    return await apiRequest(`/api/experiments/${id}/complete`, {
      method: 'POST',
      body: JSON.stringify(completionData)
    })
  }
}

/**
 * Metrics API
 */
export const metricsApi = {
  async getAll() {
    return await apiRequest('/api/metrics')
  }
}

/**
 * Dashboard API
 */
export const dashboardApi = {
  async getSelectedMetrics() {
    return await apiRequest('/api/dashboard/metrics/selected')
  },

  async getMetricValues() {
    return await apiRequest('/api/dashboard/metrics/values')
  },

  async getAvailableMetrics() {
    return await apiRequest('/api/dashboard/metrics/available')
  },

  async getRecentMetrics() {
    return await apiRequest('/api/dashboard/metrics/recent')
  },

  async saveSelectedMetrics(metrics) {
    return await apiRequest('/api/dashboard/metrics/selected', {
      method: 'POST',
      body: JSON.stringify({ selected_metrics: metrics })
    })
  }
}

/**
 * Integrations API
 */
export const integrationsApi = {
  async getStatus() {
    return await apiRequest('/api/integrations/status')
  }
}

/**
 * Graphs API
 */
export const graphsApi = {
  async getAll() {
    return await apiRequest('/api/graphs')
  }
}

/**
 * Data validation helpers
 */
export const validators = {
  experiment(experiment) {
    // Check for either the new primary metric or the legacy metric_of_interest
    const hasMetric = experiment.primary_metric_of_interest || experiment.metric_of_interest
    const required = ['title', 'benchmark', 'period']
    const missing = required.filter(field => !experiment[field])
    
    if (!hasMetric) {
      missing.push('primary_metric_of_interest')
    }
    
    if (missing.length > 0) {
      throw new Error(`Missing required fields: ${missing.join(', ')}`)
    }
    
    return true
  },

  experimentStats(stats) {
    if (!stats || typeof stats !== 'object') {
      throw new Error('Invalid stats data')
    }
    return true
  }
}

/**
 * Error handling utilities
 */
export const errorHandler = {
  showError(message, error = null) {
    console.error('Application Error:', message, error)
    // Simple error logging - can be enhanced with a proper notification system later
  },

  showSuccess(message) {
    console.log('Success:', message)
    // Simple success logging - can be enhanced with a proper notification system later
  }
}
