/**
 * Composable for managing experiments state and operations
 * Provides reactive state management, error handling, and loading states
 */

import { ref, computed } from 'vue'
import { experimentsApi, validators, errorHandler } from '../services/api.js'

// Global state
const experiments = ref([])
const isLoading = ref(false)
const error = ref(null)

export function useExperiments() {
  // Computed properties
  const ongoingExperiments = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return experiments.value
      .filter(exp => {
        if (!exp.start_date || !exp.end_date) return false
        return today >= exp.start_date && today <= exp.end_date
      })
      .sort((a, b) => {
        // Sort by start_date descending (latest first)
        return new Date(b.start_date) - new Date(a.start_date)
      })
  })

  const completedExperiments = computed(() => {
    return experiments.value.filter(exp => {
      if (!exp.start_date || !exp.end_date) return false
      const today = new Date().toISOString().split('T')[0]
      return today > exp.end_date
    })
  })

  const notStartedExperiments = computed(() => {
    return experiments.value.filter(exp => !exp.start_date || !exp.end_date)
  })

  // Actions
  async function loadExperiments(useBatchLoading = true) {
    if (isLoading.value) return

    try {
      isLoading.value = true
      error.value = null

      const result = useBatchLoading 
        ? await experimentsApi.getAllWithStats()
        : await experimentsApi.getAll()

      if (result.success) {
        // Validate data before setting
        if (Array.isArray(result.data)) {
          experiments.value = result.data
          errorHandler.showSuccess(`Loaded ${result.data.length} experiments`)
        } else {
          throw new Error('Invalid data format received from API')
        }
      } else {
        throw new Error(result.error || 'Failed to load experiments')
      }
    } catch (err) {
      error.value = err.message
      errorHandler.showError('Failed to load experiments', err)
      experiments.value = [] // Reset on error
    } finally {
      isLoading.value = false
    }
  }

  async function createExperiment(experimentData) {
    try {
      // Validate data before sending
      validators.experiment(experimentData)
      
      const result = await experimentsApi.create(experimentData)
      
      if (result.success) {
        // Add to local state
        experiments.value.unshift(result.data)
        errorHandler.showSuccess('Experiment created successfully')
        return { success: true, data: result.data }
      } else {
        throw new Error(result.error || 'Failed to create experiment')
      }
    } catch (err) {
      errorHandler.showError('Failed to create experiment', err)
      return { success: false, error: err.message }
    }
  }

  async function updateExperiment(id, experimentData) {
    try {
      // Validate data before sending
      validators.experiment(experimentData)
      
      const result = await experimentsApi.update(id, experimentData)
      
      if (result.success) {
        // Update local state
        const index = experiments.value.findIndex(exp => exp.id === id)
        if (index !== -1) {
          experiments.value[index] = result.data
        }
        errorHandler.showSuccess('Experiment updated successfully')
        return { success: true, data: result.data }
      } else {
        throw new Error(result.error || 'Failed to update experiment')
      }
    } catch (err) {
      errorHandler.showError('Failed to update experiment', err)
      return { success: false, error: err.message }
    }
  }

  async function deleteExperiment(id) {
    try {
      const result = await experimentsApi.delete(id)
      
      if (result.success) {
        // Remove from local state
        experiments.value = experiments.value.filter(exp => exp.id !== id)
        errorHandler.showSuccess('Experiment deleted successfully')
        return { success: true }
      } else {
        throw new Error(result.error || 'Failed to delete experiment')
      }
    } catch (err) {
      errorHandler.showError('Failed to delete experiment', err)
      return { success: false, error: err.message }
    }
  }

  async function completeExperiment(id, completionData) {
    try {
      const result = await experimentsApi.complete(id, completionData)
      
      if (result.success) {
        // Refresh experiments to get updated data
        await loadExperiments()
        errorHandler.showSuccess('Experiment completed successfully')
        return { success: true, data: result.data }
      } else {
        throw new Error(result.error || 'Failed to complete experiment')
      }
    } catch (err) {
      errorHandler.showError('Failed to complete experiment', err)
      return { success: false, error: err.message }
    }
  }

  function getExperimentById(id) {
    return experiments.value.find(exp => exp.id === id)
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    experiments: computed(() => experiments.value),
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    
    // Computed
    ongoingExperiments,
    completedExperiments,
    notStartedExperiments,
    
    // Actions
    loadExperiments,
    createExperiment,
    updateExperiment,
    deleteExperiment,
    completeExperiment,
    getExperimentById,
    clearError
  }
}

