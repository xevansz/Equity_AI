import React from 'react';

const Footer = () => (
	<footer className="border-t border-textMuted/10 py-6 mt-8">
		<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-textMuted">
			© {new Date().getFullYear()} EquityAI — Built for research
		</div>
	</footer>
);

export default Footer;
