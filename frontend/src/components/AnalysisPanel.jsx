// frontend/src/components/AnalysisPanel.jsx
import React, { useState } from "react";
import InsightTabs from "./InsightTabs";
import FinancialCharts from "./FinancialCharts";

const AnalysisPanel = ({ data }) => {
  const [activeTab, setActiveTab] = useState("thesis");
  const [showRaw, setShowRaw] = useState(false);

  if (!data) {
    return (
      <div className="p-4 bg-surface rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Analysis</h2>
        <p className="text-textMuted">
          No analysis available. Search a stock to view insights.
        </p>
      </div>
    );
  }

  const { query, symbol, chat, financial, research, news } = data;

  return (
    <div className="p-4 bg-surface rounded-lg space-y-4">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold">Analysis</h2>
        <p className="text-xs text-textMuted">
          Query: <b>{query}</b> | Symbol: <b>{symbol}</b>
        </p>
      </div>

      {/* Tabs */}
      <InsightTabs activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* TAB CONTENT */}
      {activeTab === "thesis" && (
        <div className="text-sm whitespace-pre-line">
          {chat?.answer || "Thesis not available"}
        </div>
      )}

      {activeTab === "data" && (
        <div>
          <h3 className="text-sm font-semibold mb-2">
            Revenue & Profit (Last 5 Years)
          </h3>
          {activeTab === 'data' && (
            <FinancialCharts financial={data?.financial} />
            )}
          /
        </div>
      )}

      {activeTab === "risk" && (
        <div className="text-sm whitespace-pre-line">
          {research?.risk || "Risk analysis not available"}
        </div>
      )}

      {/* RAW JSON TOGGLE (IMPORTANT) */}
      <div className="pt-3 border-t border-textMuted/20">
        <button
          onClick={() => setShowRaw(!showRaw)}
          className="text-xs text-primary underline"
        >
          {showRaw ? "Hide Raw API Response" : "Show Raw API Response"}
        </button>

        {showRaw && (
          <pre className="mt-2 text-xs max-h-64 overflow-auto bg-background p-2 rounded">
            {JSON.stringify(data, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};

export default AnalysisPanel;
