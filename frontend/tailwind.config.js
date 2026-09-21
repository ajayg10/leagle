/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    colors: {
      'leagle': {
        'bg': '#050709',
        'navy': '#0F141A',
        'accent': '#C5A059',  // Gold/Tan color
        'gold': '#C5A059',
      }
    },
    extend: {
      backgroundColor: {
        'leagle-glass': 'rgba(10, 15, 20, 0.9)',
      },
      borderColor: {
        'leagle-border': 'rgba(197, 160, 89, 0.15)',
      },
      textColor: {
        'leagle-accent': '#C5A059',
        'leagle-gold': '#C5A059',
      }
    },
  },
  plugins: [],
}

