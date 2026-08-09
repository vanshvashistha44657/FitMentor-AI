import type { Config } from "tailwindcss";

// Design tokens for FitMentor AI:
// A "training at dusk" palette — deep graphite (not pure black) grounds the UI,
// an ember-orange accent carries effort/heat (workouts, streaks, XP),
// and a cool signal-teal is reserved exclusively for AI-generated content
// (coach messages, scores, insights) so the user always knows what the
// machine said versus what they logged themselves.
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: "#0B0D0F",
          900: "#111418",
          800: "#181C22",
          700: "#232830",
          600: "#323944",
        },
        ember: {
          400: "#FF8A4C",
          500: "#FF6B2C",
          600: "#E8551B",
        },
        signal: {
          400: "#5EEAD4",
          500: "#2DD4BF",
          600: "#14B8A6",
        },
        bone: "#EDEAE3",
        mute: "#8A8F98",
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backdropBlur: {
        xs: "2px",
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0,0,0,0.35)",
        glow: "0 0 24px rgba(255,107,44,0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
