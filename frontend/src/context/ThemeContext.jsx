// ThemeContext.jsx
import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext({
	theme: 'light',
	setTheme: () => {},
});

export function ThemeProvider({ children }) {
	const [theme, setTheme] = useState('light');

	useEffect(() => {
		const root = document.documentElement;
		if (theme === 'dark') root.classList.add('dark');
		else root.classList.remove('dark');
	}, [theme]);

	return (
		<ThemeContext.Provider value={{ theme, setTheme }}>
			{children}
		</ThemeContext.Provider>
	);
}

export default ThemeProvider;
