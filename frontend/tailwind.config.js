/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        academic: {
          bg: "#F7F3EC",
          secondary: "#EFE9DF",
          card: "#FCFAF6",
          border: "#D8D1C5",
          primary: "#2B2926",
          muted: "#6F6A63",
          accent: "#8A6A4A",
          burgundy: "#7A1C28",
          burgundylight: "#F3E7E8",
          gold: "#C89B3C",
          goldlight: "#FAF4E7",
        }
      },
      fontFamily: {
        serif: ["Merriweather", "Georgia", "serif"],
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      }
    },
  },
  plugins: [],
}
