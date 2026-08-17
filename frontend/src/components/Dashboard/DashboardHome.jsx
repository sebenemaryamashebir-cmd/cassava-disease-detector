import { ScanEye, Gauge, Lightbulb, ArrowRight, History as HistoryIcon } from "lucide-react";
import PageHeader from "../Common/PageHeader.jsx";

const FEATURES = [
  {
    icon: ScanEye,
    title: "AI Disease Detection",
    desc: "Computer vision trained on cassava leaf imagery identifies common diseases from a single photo.",
  },
  {
    icon: Gauge,
    title: "Confidence Analysis",
    desc: "Every prediction comes with a model confidence score, so you know how much to trust the result.",
  },
  {
    icon: Lightbulb,
    title: "Smart Recommendations",
    desc: "An AI advisor turns the diagnosis into plain-language, actionable crop-care guidance.",
  },
];

export default function DashboardHome({ backendOnline, recentHistory, onNavigate, onSelectHistory }) {
  return (
    <div>
      <PageHeader
        title="Welcome back"
        subtitle="Your AI-powered crop health assistant for detecting and understanding cassava leaf disease."
        showStatus
        backendOnline={backendOnline}
      />

      <div className="feature-cards-row">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <div className="feature-mini-card" key={title}>
            <div className="icon">
              <Icon size={18} />
            </div>
            <h4>{title}</h4>
            <p>{desc}</p>
          </div>
        ))}
      </div>

      <div className="cta-banner">
        <div>
          <h3>Diagnose a cassava leaf</h3>
          <p>Upload a photo and get a disease prediction with AI-generated crop-care recommendations in seconds.</p>
        </div>
        <button className="btn btn-primary" onClick={() => onNavigate("detect")}>
          Start Detection
          <ArrowRight size={16} />
        </button>
      </div>

      <div className="card" style={{ marginTop: 22 }}>
        <div className="card-header">
          <div className="card-header-icon">
            <HistoryIcon size={18} />
          </div>
          <div>
            <h3>Recent Predictions</h3>
            <div className="subtitle">Your last few diagnoses on this device.</div>
          </div>
        </div>

        {recentHistory.length === 0 ? (
          <div className="history-empty">No predictions yet — analyze a leaf to see it here.</div>
        ) : (
          <div className="history-list">
            {recentHistory.slice(0, 3).map((entry) => (
              <div
                className="history-item"
                key={entry.id}
                onClick={() => onSelectHistory?.(entry)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") onSelectHistory?.(entry);
                }}
                style={{ cursor: onSelectHistory ? "pointer" : "default" }}
              >
                {entry.imageDataUrl && <img className="history-thumb" src={entry.imageDataUrl} alt="" />}
                <div className="history-info">
                  <div className="history-disease">{entry.predictedClass}</div>
                  <div className="history-meta">
                    <span>{entry.confidence}% confidence</span>
                    <span>·</span>
                    <span>{new Date(entry.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
