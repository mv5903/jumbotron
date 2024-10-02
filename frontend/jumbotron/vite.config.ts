import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  define: {
    "global": {},
  },
  resolve: {
      alias: {
          process: "process/browser",
          buffer: "buffer",
          crypto: "crypto-browserify",
          stream: "stream-browserify",
          assert: "assert",
          http: "stream-http",
          https: "https-browserify",
          os: "os-browserify",
          url: "url",
          util: "util",
      },
  },
})
