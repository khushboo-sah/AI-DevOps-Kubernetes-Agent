/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0f172a",
        panel: "#111827",
        accent: "#38bdf8",
        danger: "#f87171",
        warning: "#fbbf24",
        success: "#34d399",
      },
    },
  },
  plugins: [],
};
