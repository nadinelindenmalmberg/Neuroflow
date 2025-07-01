<template>
  <div class="min-h-screen bg-[#191a23] text-white p-6">
    <div class="max-w-6xl mx-auto">
      <div class="flex justify-between items-center mb-8">
        <input
          v-model="graphName"
          class="bg-transparent text-2xl font-bold border-b border-gray-600 focus:border-gray-400 outline-none px-2 py-1"
          :placeholder="'Graph Name'"
        />
        <button
          @click="handleBack"
          class="px-4 py-2 text-gray-400 hover:text-white"
        >
          Back
        </button>
      </div>

      <div class="bg-[#1E1F2B] rounded-lg p-6 shadow-lg">
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="border-b border-gray-700">
                <th class="py-2 px-4">Date</th>
                <th class="py-2 px-4">Metric Name</th>
                <th class="py-2 px-4">Value</th>
                <th class="py-2 px-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="point in dataPoints"
                :key="point.id"
                class="border-b border-gray-700"
              >
                <td class="py-2 px-4">
                  <input
                    v-model="point.date"
                    type="date"
                    class="bg-transparent border border-gray-600 rounded px-2 py-1"
                  />
                </td>
                <td class="py-2 px-4">
                  <input
                    v-model="point.metric_name"
                    class="bg-transparent border border-gray-600 rounded px-2 py-1"
                  />
                </td>
                <td class="py-2 px-4">
                  <input
                    v-model.number="point.value"
                    type="number"
                    step="any"
                    class="bg-transparent border border-gray-600 rounded px-2 py-1"
                  />
                </td>
                <td class="py-2 px-4">
                  <button
                    @click="deleteDataPoint(point.id)"
                    class="text-red-500 hover:text-red-400"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-end gap-4 mt-6">
          <button
            @click="handleBack"
            class="px-4 py-2 text-gray-400 hover:text-white"
          >
            Cancel
          </button>
          <button
            @click="handleSave"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getApiUrl } from "../config";

const route = useRouter();
const router = useRouter();
const graphId = ref(null);
const graphName = ref("");
const dataPoints = ref([]);

async function fetchGraphDetails() {
  console.log("Fetching graph details for ID:", graphId.value);
  try {
    const url = getApiUrl(`graphs/${graphId.value}`);
    console.log("Fetching from URL:", url);
    const response = await fetch(url);
    console.log("Response status:", response.status);
    if (!response.ok) {
      console.error("Response not OK:", response.status, response.statusText);
      throw new Error(
        `Failed to fetch graph details: ${response.status} ${response.statusText}`
      );
    }
    const data = await response.json();
    console.log("Fetched graph data:", data);
    graphName.value = data.name;
    dataPoints.value = data.data_points;
  } catch (error) {
    console.error("Error in fetchGraphDetails:", error);
  }
}

async function handleSave() {
  try {
    const response = await fetch(getApiUrl(`graphs/${graphId.value}`), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: graphName.value,
        data_points: dataPoints.value,
      }),
    });

    if (!response.ok) throw new Error("Failed to update graph");
    router.push("/"); // Navigate back to dashboard after successful save
  } catch (error) {
    console.error("Error updating graph:", error);
  }
}

function handleBack() {
  router.push("/"); // Navigate back to dashboard
}

async function deleteDataPoint(pointId) {
  try {
    const response = await fetch(getApiUrl(`datapoints/${pointId}`), {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to delete data point");
    dataPoints.value = dataPoints.value.filter((p) => p.id !== pointId);
  } catch (error) {
    console.error("Error deleting data point:", error);
  }
}

onMounted(() => {
  // Get the graph ID from the route params
  graphId.value = parseInt(route.currentRoute.value.params.id);
  console.log("GraphEditor mounted with graphId:", graphId.value);
  fetchGraphDetails();
});
</script>
