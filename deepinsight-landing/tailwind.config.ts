import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: "1.25rem",
        sm: "1.5rem",
        lg: "2rem",
      },
      screens: {
        "2xl": "1280px",
      },
    },
    extend: {
      colors: {
        navy: {
          50: "#F0F4FA",
          100: "#E1EAF6",
          200: "#C8D9EE",
          300: "#A1BEE1",
          400: "#749DD0",
          500: "#527DBF",
          600: "#3E62A2",
          700: "#324E83",
          800: "#2B426D",
          900: "#26385B",
          950: "#0A0B1A", // Darkest background
        },
        brand: {
          50: "#EEF2FF",
          100: "#E0E7FF",
          200: "#C7D2FE",
          300: "#A5B4FC",
          400: "#818CF8",
          500: "#6366F1", // Primary indigo
          600: "#4F46E5",
          700: "#4338CA",
          800: "#3730A3",
          900: "#312E81",
          950: "#1E1B4B",
        },
        ink: "#0A0B1A",
      },
      fontFamily: {
        display: ["var(--font-inter)", "system-ui", "sans-serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-1": ["clamp(2.75rem, 5vw + 1rem, 4.5rem)", { lineHeight: "1.05", letterSpacing: "-0.02em" }],
        "display-2": ["clamp(2.25rem, 3.5vw + 1rem, 3.5rem)", { lineHeight: "1.08", letterSpacing: "-0.015em" }],
        "display-3": ["clamp(1.75rem, 2vw + 1rem, 2.5rem)", { lineHeight: "1.15", letterSpacing: "-0.01em" }],
      },
      boxShadow: {
        soft: "0 4px 20px -2px rgba(10, 11, 26, 0.05)",
        glow: "0 10px 40px -10px rgba(79, 70, 229, 0.5)",
        lift: "0 20px 40px -10px rgba(10, 11, 26, 0.08), 0 1px 3px rgba(10, 11, 26, 0.05)",
        ring: "0 0 0 1px rgba(99, 102, 241, 0.4)",
      },
      backgroundImage: {
        "brand-gradient": "linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%)",
        "brand-gradient-light": "linear-gradient(135deg, #818CF8 0%, #93C5FD 100%)",
      },
      keyframes: {
        "fade-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        drift: {
          "0%": { transform: "translateY(0) translateX(0)", opacity: "0" },
          "20%": { opacity: "0.6" },
          "100%": { transform: "translateY(-120px) translateX(20px)", opacity: "0" },
        },
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.7s cubic-bezier(0.16, 1, 0.3, 1) both",
        drift: "drift 7s ease-in infinite",
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
