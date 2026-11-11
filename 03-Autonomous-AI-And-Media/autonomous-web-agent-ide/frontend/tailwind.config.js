/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ide: {
          bg: '#0d1117',
          sidebar: '#161b22',
          panel: '#1e242e',
          border: '#30363d',
          accent: '#58a6ff',
          hover: '#21262d',
          text: '#c9d1d9',
          muted: '#8b949e',
          success: '#2ea043',
          warning: '#d29922',
          error: '#f85149'
        }
      },
      fontFamily: {
        mono: ['"Fira Code"', 'Consolas', 'Monaco', '"Courier New"', 'monospace'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
      }
    },
  },
  plugins: [],
}
