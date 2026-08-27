/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        kivo: {
          light: "#1AEAA0",
          emerald: "#00CE86",
          darkgreen: "#006C59",
          navy: "#051329",
          background: "#F8FAFC",
        }
      }
    },
  },
  plugins: [],
};
