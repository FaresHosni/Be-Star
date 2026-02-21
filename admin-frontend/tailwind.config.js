/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                gold: {
                    50: '#FFF9E6',
                    100: '#FFF3CC',
                    200: '#FFE799',
                    300: '#FFDB66',
                    400: '#FFCF33',
                    500: '#D4AF37',
                    600: '#B8962F',
                    700: '#9C7D27',
                    800: '#80641F',
                    900: '#644B17',
                },
                dark: {
                    50: '#3a3a3a',
                    100: '#2a2a2a',
                    200: '#1a1a1a',
                    300: '#151515',
                    400: '#0f0f0f',
                    500: '#0a0a0a',
                    600: '#050505',
                    700: '#000000',
                }
            },
            fontFamily: {
                cairo: ['Cairo', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
