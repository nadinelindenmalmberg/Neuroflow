<template>
  <div class="container mt-5">
    <!-- Breadcrumb Navigation -->
    <div class="breadcrumb">
      <router-link to="/" class="breadcrumb-link">Dashboard</router-link>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-current">Integrations</span>
    </div>

    <h1>Integrations</h1>
    <hr class="subtle-line" />

    <!-- Oura Integration Card -->
    <router-link to="/oura-connect" class="integration-card">
      <div class="integration-header">
        <div class="logo-container">
          <img
            src="../assets/images/oura_logo_logo.png"
            alt="Oura Logo"
            class="integration-logo"
          />
        </div>
        <h5 class="card-title">Oura</h5>
      </div>
      <p class="card-text">
        Sync your Oura data to identify patterns in your sleep and compare
        against other metrics
      </p>
    </router-link>
  </div>
</template>

<script setup>
// Component logic will go here if needed
</script>

<style scoped>
.container {
  padding: 20px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: #9ca3af;
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  margin: 0 0.5rem;
  color: #6b7280;
}

.breadcrumb-current {
  color: #fff;
}

.subtle-line {
  border: none;
  height: 1px;
  background-color: rgba(255, 255, 255, 0.1);
  margin: 1rem 0;
}

.integration-card {
  background: linear-gradient(
    145deg,
    rgba(31, 32, 43, 0.9),
    rgba(31, 32, 43, 0.7)
  );
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  width: 280px;
  transition: all 0.2s ease;
  cursor: pointer;
  text-decoration: none;
  display: block;
}

.integration-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.integration-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.logo-container {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 0.5rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.integration-logo {
  width: 32px;
  padding: 5px;
  height: auto;
  filter: invert(1);
}

.card-title {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
  color: #fff;
}

.card-text {
  font-size: 0.8rem;
  color: #9ca3af;
  margin: 0;
}
</style>
