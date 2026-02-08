import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const FinancialCharts = ({ financial }) => {

  // 🔥 REAL DATA TRANSFORMATION (NO MOCK)
  const chartData = useMemo(() => {
    const reports =
      financial?.financials?.income_statement?.annualReports;

    if (!Array.isArray(reports)) return [];

    return reports
      .slice(0, 5)
      .reverse()
      .map((r) => ({
        year: r.fiscalDateEnding.slice(0, 4),
        revenue: Number(r.totalRevenue),
        profit: Number(r.grossProfit)
      }));
  }, [financial]);

  if (chartData.length === 0) {
    return (
      <p className="text-textMuted text-sm mt-4">
        No financial data available
      </p>
    );
  }

  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold mb-2">
        Revenue & Profit (Last 5 Years)
      </h4>

      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={chartData}>
          <XAxis dataKey="year" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip />
          <Legend />

          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#3DD9D0"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="Revenue"
          />

          <Line
            type="monotone"
            dataKey="profit"
            stroke="#22c55e"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="Profit"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FinancialCharts;
