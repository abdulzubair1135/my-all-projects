/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mineral: {
          light: '#F4F2E9',
          surface: '#FAFAF7',
          border: '#E2E0D8',
          sage: '#78866B',
          deep: '#56664C',
          dark: '#292D28',
          muted: '#5A6258'
        }
      }
    },
  },
  plugins: [],
}
