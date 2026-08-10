/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./render.py", "./src.css", "../index.html"],
  theme: {
    extend: {},
  },
  corePlugins: { preflight: true },
};
