import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "./components/Dashboard.vue";
import Explorer from "./components/Explorer.vue";
import Integration from "./components/integration.vue";
import OuraConnect from "./components/OuraConnect.vue";

const routes = [
  {
    path: "/",
    name: "Dashboard",
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
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
