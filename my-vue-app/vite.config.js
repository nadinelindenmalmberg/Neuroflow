import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:5174",
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, options) => {
          proxy.on("error", (err, req, res) => {
            console.log("proxy error", err);
          });
          proxy.on("proxyReq", (proxyReq, req, res) => {
            console.log("Sending Request to the Target:", req.method, req.url);
          });
          proxy.on("proxyRes", (proxyRes, req, res) => {
            console.log(
              "Received Response from the Target:",
              proxyRes.statusCode
            );
          });
        },
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate large dependencies
          'apexcharts': ['apexcharts'],
          'lucide': ['lucide-vue-next'],
          'supabase': ['@supabase/supabase-js'],
          'marked': ['marked']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    minify: 'esbuild'
  }
});

