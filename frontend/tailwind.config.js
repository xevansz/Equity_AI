/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3DD9D0',
        primaryDark: '#2BB8B0',
        secondary: '#1A1F2E',
        background: '#0F1419',
        surface: '#1E2532',
        text: '#E8EAED',
        textMuted: '#9CA3AF',
        accent: '#60A5FA',
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}