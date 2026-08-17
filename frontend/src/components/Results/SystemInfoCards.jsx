import { Cpu, Layers, Brain } from "lucide-react";

export default function SystemInfoCards({ backendOnline }) {
  return (
    <div className="info-cards-grid">
      <div className="info-card">
        <div className="info-card-icon">
          <Cpu size={17} />
        </div>
        <h4>AI Model</h4>
        <div className="value">Cassava Disease Classifier</div>
        <div className="status-row">
          <span
            style={{
              fontSize: 12,
              fontWeight: 600,
              color: backendOnline ? "var(--leaf-600)" : "var(--danger-600)",
            }}
          >
            ● {backendOnline ? "Online" : "Offline"}
          </span>
        </div>
      </div>

      <div className="info-card">
        <div className="info-card-icon">
          <Layers size={17} />
        </div>
        <h4>Disease Classes</h4>
        <div className="value">5 classes: Healthy, Mosaic, Bacterial Blight, Brown Streak, Green Mottle</div>
      </div>

      <div className="info-card">
        <div className="info-card-icon">
          <Brain size={17} />
        </div>
        <h4>AI Advisor</h4>
        <div className="value">LLM Recommendation Engine</div>
        <div className="status-row">
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--leaf-600)" }}>● Available</span>
        </div>
      </div>
    </div>
  );
}
