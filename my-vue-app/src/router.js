import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "./components/Dashboard.vue";
import Experiments from "./components/Experiments.vue";
import Explorer from "./components/Explorer.vue";
import Integration from "./components/integration.vue";
import OuraConnect from "./components/OuraConnect.vue";
import Upload from "./components/Upload.vue";

const routes = [
  {
    path: "/",
    redirect: "/experiments"
  },
  {
    path: "/experiments",
    name: "Experiments",
    component: Experiments,
  },
  {
    path: "/dashboard",
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
