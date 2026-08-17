import { ArrowLeft, CheckCircle2, Trash2 } from "lucide-react";
import PageHeader from "../Common/PageHeader.jsx";
import DiagnosisCard from "../Results/DiagnosisCard.jsx";
import ProbabilityBreakdown from "../Results/ProbabilityBreakdown.jsx";
import AIRecommendation from "../Results/AIRecommendation.jsx";

export default function HistoryDetail({ entry, onBack, onDelete }) {
  const handleDelete = () => {
    if (window.confirm("Delete this prediction from your history?")) {
      onDelete?.(entry.id);
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 18, flexWrap: "wrap", gap: 10 }}>
        <button className="btn btn-ghost" onClick={onBack}>
          <ArrowLeft size={15} />
          Back to history
        </button>
        <button className="btn btn-ghost" onClick={handleDelete}>
          <Trash2 size={14} />
          Delete
        </button>
      </div>

      <PageHeader
        title={entry.fileName || "Prediction detail"}
        subtitle={`Analyzed ${new Date(entry.timestamp).toLocaleString()}`}
      />

      {entry.recommendationError && (
        <div className="alert-card warning">
          <CheckCircle2 size={19} className="alert-icon" />
          <div>
            <div className="alert-title">Diagnosis completed</div>
            <div className="alert-desc">
              {entry.confidence < 50
                ? "The AI wasn't confident enough in this diagnosis to generate a recommendation."
                : "The disease prediction was successful, but the AI recommendation service was unavailable at the time."}
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <div className="detect-grid">
          {entry.imageDataUrl && (
            <div className="image-preview" style={{ minHeight: "auto" }}>
              <img src={entry.imageDataUrl} alt={entry.fileName} />
            </div>
          )}
          <div>
            <DiagnosisCard predictedClass={entry.predictedClass} confidence={entry.confidence} />
          </div>
        </div>

        <ProbabilityBreakdown probabilities={entry.probabilities} />
        <AIRecommendation recommendation={entry.recommendation} />
      </div>
    </div>
  );
}
