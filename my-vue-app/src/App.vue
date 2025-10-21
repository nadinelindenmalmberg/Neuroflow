<script setup>
// No need to import Dashboard anymore as it's handled by the router
</script>

<template>
  <router-view></router-view>
</template>

<style>
/* Minimal global styles */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: sans-serif;
  background-color: #191a23;
  color: white;
}

/* Apply global styles */
html,
body,
#app {
  height: 100%;
  min-height: 100vh;
  background-color: #191a23;
  margin: 0;
  padding: 0;
}

/* Chart container styling for consistent sizing */
.chart-container {
  min-height: 300px;
  margin-top: 1rem;
}
</style>