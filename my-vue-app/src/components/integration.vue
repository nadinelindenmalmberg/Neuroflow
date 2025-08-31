<template>
  <div class="integration-layout">
    <!-- Main Navigation Sidebar -->
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
        <router-link to="/integrations" class="nav-link router-link-active">
          <GitBranch class="nav-icon" size="20" />
          <span>Integrations</span>
        </router-link>
        <router-link to="/upload" class="nav-link">
          <Upload class="nav-icon" size="20" />
          <span>Upload</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">Integrations</h1>
          <div class="header-actions">
            <!-- Integration-specific actions can go here if needed -->
          </div>
        </div>
      </div>

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
    </main>
  </div>
</template>

<script setup>
import { FlaskConical, BarChart3, Activity, GitBranch, Upload } from "lucide-vue-next";
import neuroflowLogo from "../assets/images/ChatGPT_Image_Apr_5__2025__01_36_36_PM-removebg-preview 1.svg";
</script>

<style scoped>
.integration-layout {
  display: flex;
  min-height: 100vh;
  background-color: #191a23;
  color: white;
}

/* Main Navigation Sidebar */
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

/* Main Content */
.main-content {
  flex: 1;
  padding: 1.25rem;
  overflow-y: auto;
  margin-left: 15rem; /* Match expanded sidebar width */
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 1.125rem;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.025em;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
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
  color: white;
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

/* Removed old container and subtle-line styles */

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
