import { createRouter, createWebHistory } from "vue-router";

// Lazy load components for better initial bundle size
const Dashboard = () => import("./components/Dashboard.vue");
const Explorer = () => import("./components/Explorer.vue");
const Integration = () => import("./components/integration.vue");
const OuraConnect = () => import("./components/OuraConnect.vue");
const Upload = () => import("./components/Upload.vue");

const routes = [
  {
    path: "/",
    redirect: "/dashboard"
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
  },
  {
    path: "/dashboard/overview",
    name: "DashboardOverview",
    component: Dashboard,
  },
  {
    path: "/dashboard/integrations",
    name: "DashboardIntegrations", 
    component: Dashboard,
  },
  {
    path: "/dashboard/experiments",
    name: "DashboardExperiments",
    component: Dashboard,
  },
  {
    path: "/explorer",
    name: "Explorer",
    component: Explorer,
  },
  {
    path: "/integrations",
    name: "Integrations",
    component: Integration,
  },
  {
    path: "/oura-connect",
    name: "OuraConnect",
    component: OuraConnect,
  },
  {
    path: "/upload",
    name: "Upload",
    component: Upload,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
