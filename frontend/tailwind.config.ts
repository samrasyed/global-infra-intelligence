import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#080B10",
        surface: "#0E131C",
        "surface-2": "#141B27",
        "surface-3": "#1A2331",
        border: "rgba(148,163,184,0.12)",
        "border-strong": "rgba(148,163,184,0.24)",
        ink: "#E7ECF4",
        "ink-muted": "#8996A9",
        "ink-faint": "#586376",
        signal: "#2FD6C0",
        "signal-dim": "#1B7A6E",
        amber: "#F0A83C",
        crimson: "#EF5B4E",
        cobalt: "#4C8DFF",
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        glass: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 20px 40px -20px rgba(0,0,0,0.6)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(148,163,184,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.06) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "36px 36px",
      },
      keyframes: {
        sweep: {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        pulse_ring: {
          "0%": { transform: "scale(0.8)", opacity: "0.7" },
          "100%": { transform: "scale(2.2)", opacity: "0" },
        },
      },
      animation: {
        sweep: "sweep 6s linear infinite",
        pulse_ring: "pulse_ring 2.4s ease-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
