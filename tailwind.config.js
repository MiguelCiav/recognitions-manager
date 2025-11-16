/** @type {import('tailwindcss').Config} */
module.exports = {
  // Include the Flask templates directory (one level up from the
  // frontend build root) and frontend sources.
  content: [
    "../app/templates/**/*.{html,js}",
    "./**/*.{html,js}"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}