import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],

  test: {
    environment: 'jsdom',
    globals: true,

    environmentOptions: {
      jsdom: {
        url: 'http://localhost:5173/',
      },
    },

    setupFiles: [
      './src/test/setup.js',
    ],
  },
})
