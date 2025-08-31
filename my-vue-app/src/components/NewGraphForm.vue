<template>
  <div class="modal-overlay" v-if="isVisible" @click="closeModal">
    <div class="modal-wrapper" @click.stop>
      <div class="modal-container">
        <div class="modal-header">
          <h1 class="modal-title">Create a New Graph</h1>
          <button class="close-button" type="button" @click="closeModal">
            &times;
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitForm" class="new-graph-form">
            <div class="form-group">
              <label for="name">Graph Name:</label>
              <input
                type="text"
                id="name"
                v-model="formData.name"
                required
                class="form-input"
                placeholder="Enter graph name"
              />
            </div>

            <div class="form-group">
              <label for="description">Description:</label>
              <input
                type="text"
                id="description"
                v-model="formData.description"
                class="form-input"
                placeholder="Enter graph description (optional)"
              />
            </div>

            <div class="form-group">
              <label for="metrics">Tracked Metrics:</label>
              <select
                id="metrics"
                v-model="formData.selectedMetrics"
                multiple
                class="form-input"
                size="4"
              >
                <option 
                  v-for="metric in availableMetrics" 
                  :key="metric" 
                  :value="metric"
                >
                  {{ metric }}
                </option>
              </select>
              <small class="form-help">Hold Ctrl/Cmd to select multiple metrics</small>
            </div>

            <div class="form-actions">
              <button type="button" class="cancel-button" @click="closeModal">
                Cancel
              </button>
              <button
                type="submit"
                class="submit-button"
                :disabled="isSubmitting"
              >
                {{ isSubmitting ? "Creating..." : "Create Graph" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from "vue";
import { getApiUrl } from "../config.js";

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "graphCreated"]);

const formData = ref({
  name: "",
  description: "",
  selectedMetrics: [],
});

const availableMetrics = ref([]);
const isSubmitting = ref(false);
const error = ref("");

// Fetch available metrics when component is mounted
const fetchAvailableMetrics = async () => {
  try {
    const response = await fetch(getApiUrl("/metrics"));
    if (response.ok) {
      const data = await response.json();
      availableMetrics.value = data.metrics || [];
    }
  } catch (err) {
    console.error("Error fetching metrics:", err);
  }
};

// Fetch metrics when component is created
fetchAvailableMetrics();

function closeModal() {
  // Reset form data when closing
  formData.value = {
    name: "",
    description: "",
    selectedMetrics: [],
  };
  error.value = "";
  emit("close");
}

async function submitForm() {
  if (!formData.value.name.trim()) {
    error.value = "Graph name is required";
    return;
  }

  isSubmitting.value = true;

  try {
    const requestData = {
      name: formData.value.name,
      description: formData.value.description,
      tracked_metrics: formData.value.selectedMetrics
    };

    const response = await fetch(getApiUrl("/graphs"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to create graph");
    }

    const data = await response.json();

    // Emit an event with the new graph data
    emit("graphCreated", data.graph);

    // Close the modal and reset form
    closeModal();
  } catch (err) {
    error.value = err.message || "An error occurred";
    console.error("Error creating graph:", err);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
/* A cleaner modal implementation */
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
  max-width: 500px;
  border-radius: 0.75rem;
  border: 1.5px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
  margin: 0 auto;
  position: relative;
  z-index: 1002;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
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

/* Form styles */
.new-graph-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #e5e7eb;
  margin-bottom: 0.25rem;
}

.form-help {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.form-input {
  padding: 0.75rem;
  border-radius: 0.5rem;
  background-color: #16161d;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.9rem;
  width: 100%;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.3);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.cancel-button {
  padding: 0.6rem 1rem;
  border-radius: 0.5rem;
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-button:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.submit-button {
  padding: 0.6rem 1.25rem;
  border-radius: 0.5rem;
  background-color: #3b82f6;
  border: none;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-button:hover {
  background-color: #2563eb;
}

.submit-button:disabled {
  background-color: #64748b;
  cursor: not-allowed;
  opacity: 0.7;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}
</style>
