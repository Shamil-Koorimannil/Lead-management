/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#0284c7',
          600: '#0369a1',
          700: '#075985',
          900: '#0c4a6e',
        },
        qualified: {
          bg: '#ecfdf5',
          text: '#047857',
          border: '#a7f3d0',
        },
        review: {
          bg: '#fffbebf',
          text: '#b45309',
          border: '#fde68a',
        },
        disqualified: {
          bg: '#fef2f2',
          text: '#b91c1c',
          border: '#fecaca',
        }
      }
    },
  },
  plugins: [],
}
