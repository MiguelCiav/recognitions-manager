/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Flask templates
    "../app/templates/**/*.html",
    // Frontend entry points
    "./index.html",
    "./main.js"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
