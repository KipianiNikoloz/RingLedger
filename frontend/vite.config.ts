import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 4173,
  },
  test: {
    allowOnly: false,
    dangerouslyIgnoreUnhandledErrors: false,
    environment: "jsdom",
    fileParallelism: false,
    setupFiles: "./src/vitest.setup.ts",
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    exclude: ["e2e/**", "node_modules/**", "dist/**"],
    passWithNoTests: false,
  },
});
