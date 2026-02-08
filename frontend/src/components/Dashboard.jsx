// Dashboard.jsx
import React from 'react';
import { LineChart } from 'recharts';

console.log(LineChart);

const Dashboard = ({ selectedStock }) => {
	return (
		<div className="p-4 bg-surface rounded-lg">
			<h2 className="text-lg font-semibold mb-2">Market Overview</h2>
			{selectedStock ? (
				<div>
					<p className="text-textMuted">Showing data for {selectedStock}</p>
				</div>
			) : (
				<p className="text-textMuted">Select a stock to view details.</p>
			)}
		</div>
	);
};

export default Dashboard;
