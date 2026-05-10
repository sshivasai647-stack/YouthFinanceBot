/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6C63FF',
          50:  '#F0EFFF',
          100: '#E1DEFF',
          200: '#C3BDFF',
          300: '#A59CFF',
          400: '#877BFF',
          500: '#6C63FF',
          600: '#4D43FF',
          700: '#2E22FF',
          800: '#1200F5',
          900: '#0E00C2',
        },
        success: '#22c55e',
        warning: '#f59e0b',
        danger:  '#ef4444',
      },
    },
  },
  plugins: [],
}