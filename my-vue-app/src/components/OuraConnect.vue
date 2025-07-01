<template>
  <div class="container mt-5">
    <h1>Configure Oura Integration</h1>
    <p>Enter your API token and date range to sync your Oura data.</p>

    <form @submit.prevent="handleSubmit" class="mt-4">
      <div class="mb-3">
        <label for="token" class="form-label">API Token</label>
        <input
          type="text"
          class="form-control"
          id="token"
          v-model="formData.token"
          required
        />
      </div>

      <div class="mb-3">
        <label for="start_date" class="form-label">Start Date</label>
        <input
          type="date"
          class="form-control"
          id="start_date"
          v-model="formData.start_date"
          required
        />
      </div>

      <div class="mb-3">
        <label for="end_date" class="form-label">End Date</label>
        <input
          type="date"
          class="form-control"
          id="end_date"
          v-model="formData.end_date"
          required
        />
      </div>

      <button type="submit" class="btn btn-primary">Sync data</button>
    </form>

    <p class="mt-3">
      <router-link to="/integrations">Back to Integrations</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { getApiUrl } from "../config";

const router = useRouter();
const formData = ref({
  token: "",
  start_date: "",
  end_date: "",
});

const handleSubmit = async () => {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await fetch(getApiUrl("oura-connect"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        token: formData.value.token,
        start_date: formData.value.start_date,
        end_date: formData.value.end_date,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to connect to Oura");
    }

    await response.json();
    router.push("/");
  } catch (error) {
    console.error("Error connecting to Oura:", error);
    errorMessage.value = "Failed to connect to Oura. Please try again.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #fff;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  background-color: #1f202b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
  color: #fff;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #2563eb;
}

a {
  color: #fff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
