import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: front na :5173, backend FastAPI na :8000 (proxy). Produkcja: FastAPI serwuje dist/.
const backend = "http://localhost:8000";
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": backend, "/d": backend, "/szablon.csv": backend, "/szablon.xlsx": backend },
  },
});
