<template>
  <div class="modal-overlay" v-if="isVisible">
    <div class="modal-wrapper">
      <div class="modal-container">
        <div class="modal-header">
          <h1 class="modal-title">Add Data Points</h1>
          <button class="close-button" type="button" @click="closeModal">
            &times;
          </button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="submitForm" class="space-y-6">
            <!-- Graph Selection -->
            <div>
              <label for="graph_id" class="block text-sm font-medium mb-1"
                >Select Graph</label
              >
              <select
                id="graph_id"
                v-model="selectedGraphId"
                required
                class="form-select"
              >
                <option value="" disabled selected>Select a graph</option>
                <option
                  v-for="graph in graphs"
                  :key="graph.graph_id"
                  :value="graph.graph_id"
                >
                  {{ graph.title }}
                </option>
              </select>
            </div>

            <!-- Data Points Table -->
            <div class="overflow-x-auto">
              <table>
                <thead>
                  <tr>
                    <th class="date-column">DATE</th>
                    <th class="metric-column">METRIC NAME</th>
                    <th class="value-column">VALUE</th>
                    <th class="action-column"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in dataPoints" :key="index">
                    <td>
                      <input type="date" v-model="row.date" required />
                    </td>
                    <td>
                      <input
                        type="text"
                        v-model="row.metric_name"
                        class="form-input"
                        placeholder="Enter metric name"
                        required
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        v-model="row.value"
                        class="form-input"
                        step="any"
                        placeholder="Enter value"
                        required
                      />
                    </td>
                    <td class="action-column">
                      <button
                        type="button"
                        class="remove-row-button"
                        @click="removeRow(index)"
                        :disabled="dataPoints.length === 1"
                      >
                        ×
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Form Buttons -->
            <div class="flex items-center justify-between mt-4">
              <button type="button" @click="addRow" class="add-row-button">
                <span>+</span> Add row
              </button>
              <div class="flex gap-2">
                <button
                  type="button"
                  @click="closeModal"
                  class="button-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  class="button-primary"
                  :disabled="isSubmitting"
                >
                  {{ isSubmitting ? "Submitting..." : "Submit Data Points" }}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from "vue";
import { getApiUrl } from "../config";

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false,
  },
  graphs: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["close", "dataAdded"]);

const selectedGraphId = ref("");
const isSubmitting = ref(false);
const dataPoints = ref([{ date: "", metric_name: "", value: "" }]);

function addRow() {
  dataPoints.value.push({ date: "", metric_name: "", value: "" });
}

function removeRow(index) {
  if (dataPoints.value.length > 1) {
    dataPoints.value.splice(index, 1);
  }
}

function closeModal() {
  // Reset form
  selectedGraphId.value = "";
  dataPoints.value = [{ date: "", metric_name: "", value: "" }];
  emit("close");
}

async function submitForm() {
  if (!selectedGraphId.value) {
    alert("Please select a graph");
    return;
  }

  isSubmitting.value = true;

  try {
    const response = await fetch(getApiUrl("datapoints"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        graph_id: selectedGraphId.value,
        data_points: dataPoints.value,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to add data points");
    }

    const result = await response.json();
    emit("dataAdded", {
      graphId: selectedGraphId.value,
      dataPoints: result.data_points,
    });
    closeModal();
  } catch (error) {
    console.error("Error adding data points:", error);
    alert("Failed to add data points. Please try again.");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.form-select {
  width: 100%;
  background-color: #16161d;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 0.625rem 0.75rem;
  color: #fff;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='rgba(255, 255, 255, 0.5)'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem;
}

.form-select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.form-input {
  width: 100%;
  background-color: #16161d;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 0.625rem 0.75rem;
  color: #fff;
  transition: background-color 0.2s, border-color 0.2s;
}

.form-input:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

.form-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.button {
  padding: 0.625rem 1rem;
  background-color: #16161d;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: #fff;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.button:hover {
  background-color: #1f1f1f;
  border-color: rgba(255, 255, 255, 0.2);
}

.button-primary {
  padding: 0.625rem 1.25rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: background-color 0.2s;
  cursor: pointer;
}

.button-primary:hover {
  background-color: #2563eb;
}

.button-primary:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.button-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-secondary {
  padding: 0.625rem 1.25rem;
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: white;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.button-secondary:hover {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.25);
}

/* Reuse the modal styles from your Dashboard.vue but with refinements */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
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
  padding: 1rem;
}

.modal-container {
  background-color: #1f202b;
  width: 100%;
  max-width: 800px;
  max-height: 85vh;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  overflow-y: auto;
  padding: 1.75rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  width: 2rem;
  height: 2rem;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.modal-body {
  margin-top: 0.75rem;
}

/* Add additional styles for better table and form layout */
table {
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
  margin: 1rem 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  overflow: hidden;
}

thead th {
  background-color: #16161d;
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  color: rgba(255, 255, 255, 0.7);
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

tbody td {
  padding: 0.25rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background-color: #1a1a23;
}

tbody tr:hover td {
  background-color: #1f1f29;
}

/* Make inputs look like they're part of the table cells */
.form-input {
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.625rem 0.75rem;
  color: #fff;
  transition: background-color 0.2s;
}

.form-input:hover,
.form-input:focus {
  background-color: #16161d;
}

.form-input:focus {
  outline: none;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

/* Style the date input specifically */
input[type="date"] {
  background-color: transparent;
  border: none;
  padding: 0.625rem 0.75rem;
  color: #fff;
  width: 100%;
  font-family: inherit;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(0.8);
  opacity: 0.5;
  cursor: pointer;
}

input[type="date"]::-webkit-calendar-picker-indicator:hover {
  opacity: 0.8;
}

/* Style the remove row button */
.remove-row-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  padding: 0;
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.6);
  background-color: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.remove-row-button:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
}

/* Update the table header and cell widths */
.date-column {
  width: 25%;
}

.metric-column {
  width: 40%;
}

.value-column {
  width: 25%;
}

.action-column {
  width: 10%;
  text-align: center;
}

/* Add row button styling */
.add-row-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  color: rgba(255, 255, 255, 0.8);
  background-color: #16161d;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.add-row-button:hover {
  background-color: #1f1f29;
  border-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.add-row-button span {
  font-size: 1.2em;
  line-height: 0;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-2 {
  gap: 0.5rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.block {
  display: block;
}

.text-sm {
  font-size: 0.875rem;
}

.font-medium {
  font-weight: 500;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.overflow-x-auto {
  overflow-x: auto;
}

.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.w-full {
  width: 100%;
}

.text-left {
  text-align: left;
}

.border {
  border-width: 1px;
}

.border-gray-800 {
  border-color: rgba(255, 255, 255, 0.1);
}

.divide-y > * + * {
  border-top-width: 1px;
}

.divide-gray-800 > * + * {
  border-color: rgba(255, 255, 255, 0.05);
}
</style>
