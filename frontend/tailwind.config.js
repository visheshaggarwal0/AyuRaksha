/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ayush: {
          forest: "#14532D",       // Deep solid emerald forest
          forestDark: "#052E16",   // Header dark green
          forestLight: "#ECFDF5",  // Light green tint for badges
          saffron: "#B45309",      // Deep solid amber
          saffronLight: "#FFFBEB", // Saffron badge tint
          crimson: "#991B1B",      // Restrictive/Prohibited red
          crimsonLight: "#FEF2F2", // Crimson badge tint
          navy: "#0F172A",         // Primary dark text (Slate 900)
          slate: "#475569",        // Secondary muted text (Slate 600)
          border: "#E2E8F0",       // Clean border line
          card: "#FFFFFF",         // Crisp card surface
          canvas: "#F8FAFC",       // Off-white neutral background
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"DM Sans"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        hindi: ['"Noto Sans Devanagari"', 'sans-serif'],
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04)',
        floating: '0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)',
        modal: '0 25px 50px -12px rgba(0, 0, 0, 0.2)',
      }
    },
  },
  plugins: [],
}
