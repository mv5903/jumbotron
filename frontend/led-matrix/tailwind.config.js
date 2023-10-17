/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      gridTemplateColumns: {
        '64': 'repeat(64, minmax(0, 1fr))'
      }
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
}