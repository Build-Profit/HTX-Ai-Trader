import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const proxyPrefix = env.VITE_HB_PROXY_PREFIX || "/hbapi";
  const apiTarget = env.VITE_HB_API_TARGET || "http://localhost:8000";
  const ppTarget = env.VITE_PP_API_TARGET || "http://localhost:8000";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        [proxyPrefix]: {
          target: apiTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(new RegExp(`^${proxyPrefix}`), ""),
        },
        "/api": {
          target: ppTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
