import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';
import type { Config } from 'tailwindcss';

export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {
			colors: {
				'sage': {
					50: '#f4f7f4',
					100: '#e6ede6',
					200: '#d1e0d2',
					300: '#afc9b1',
					400: '#88aa8b',
					500: '#698c6c',
					600: '#537156',
					700: '#435b46',
					800: '#384a3a',
					900: '#2f3d31',
				},
				'mint': {
					50: '#f2f9f6',
					100: '#e6f3ed',
					200: '#bfe3d3',
					300: '#99d3b9',
					400: '#4db38f',
					500: '#009365',
					600: '#00845b',
					700: '#006e4c',
					800: '#00583d',
					900: '#004831',
				}
			}
		}
	},

	plugins: [typography, forms]
} satisfies Config;
