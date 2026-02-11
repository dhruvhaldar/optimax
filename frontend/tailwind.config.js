/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                glass: {
                    base: 'rgba(255, 255, 255, 0.1)',
                    border: 'rgba(255, 255, 255, 0.2)',
                    highlight: 'rgba(255, 255, 255, 0.05)',
                },
                accent: {
                    primary: '#00f2ff', // Cyan
                    secondary: '#ff00ff', // Magenta/Pink
                }
            },
            backgroundImage: {
                'deep-ocean': 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)', // Midnight Blue -> Indigo
            }
        },
    },
    plugins: [],
}
