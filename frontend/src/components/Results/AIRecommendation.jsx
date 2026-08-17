import { Brain, Info } from "lucide-react";

export default function AIRecommendation({ recommendation }) {
  if (!recommendation) return null;

  return (
    <div>
      <div className="card-header" style={{ marginTop: 26 }}>
        <div className="card-header-icon">
          <Brain size={18} />
        </div>
        <div>
          <h3>AI Crop Care Advisor</h3>
          <div className="subtitle">Personalized guidance based on the detected condition.</div>
        </div>
      </div>

      <div className="recommendation-card">
        <p className="recommendation-text">{recommendation}</p>
        <div className="recommendation-disclaimer">
          <Info size={13} style={{ flexShrink: 0, marginTop: 1 }} />
          AI-generated guidance should be considered informational and does not replace advice from an
          agricultural expert.
        </div>
      </div>
    </div>
  );
}
