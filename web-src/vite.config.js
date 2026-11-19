import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";

// Build the UI into the package's ui/web/ dir (git-ignored; packaged as a
// wheel artifact). base './' so the loopback server serves it from root.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: resolve(import.meta.dirname, "../src/gmail_cleanup/ui/web"),
    emptyOutDir: true,
  },
});
