import React from 'react';

const RiskIndicator = ({ level = 'medium' }) => {
	const color = level === 'low' ? 'text-green-500' : level === 'high' ? 'text-red-500' : 'text-yellow-500';
	return (
		<span className={`inline-flex items-center gap-2 ${color}`}>
			<span className="w-2 h-2 rounded-full bg-current block" />
			<span className="text-sm capitalize">{level}</span>
		</span>
	);
};

export default RiskIndicator;
