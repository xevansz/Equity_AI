/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#658594', // dragon blue
        primaryDark: '#4F6C7A', // deeper blue
        accent: '#7AA89F', // dragon teal

        secondary: '#1F1F28', // dragonblack2
        background: '#181820',// dragonblack3
        surface: '#2A2A37',   // dragonblack4

        text: '#C5C9C5',     // dragonwhite
        textMuted: '#727169',// dragonash

        success: '#87A987', //dragongreen
        warning: '#C4B28A', // dragonorange
        error: '#C4746E'    // dragonred
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}