import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const proxyPrefix = process.env.VITE_HB_PROXY_PREFIX || "/hbapi";
const apiTarget = process.env.VITE_HB_API_TARGET || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      [proxyPrefix]: {
        target: apiTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(new RegExp(`^${proxyPrefix}`), ""),
      },
    },
  },
});
