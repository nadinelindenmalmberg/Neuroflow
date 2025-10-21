import { createApp } from "vue";
import App from "./App.vue"; // or import Dashboard from './components/Dashboard.vue'
import router from "./router";

// Import base styles
import "./assets/styles/base.css";
import "./assets/styles/components.css";

// Import Tailwind
import "./index.css";

// Performance monitoring
const startTime = performance.now();
window.addEventListener('load', () => {
  const loadTime = performance.now() - startTime;
  console.log(`🚀 App loaded in ${loadTime.toFixed(2)}ms`);
});

const app = createApp(App);
app.use(router);
app.mount("#app");