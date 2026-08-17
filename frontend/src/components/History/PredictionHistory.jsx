import { History as HistoryIcon, Trash2 } from "lucide-react";
import PageHeader from "../Common/PageHeader.jsx";

export default function PredictionHistory({ history, onClear, onSelect, onDelete }) {
  const handleClearAll = () => {
    if (window.confirm("Delete all prediction history? This can't be undone.")) {
      onClear();
    }
  };

  const handleDeleteOne = (e, id) => {
    e.stopPropagation();
    if (window.confirm("Delete this prediction from your history?")) {
      onDelete?.(id);
    }
  };

  return (
    <div>
      <PageHeader
        title="Prediction History"
        subtitle="A local record of your recent leaf diagnoses, stored on this device."
      />

      <div className="card">
        <div className="card-header" style={{ justifyContent: "space-between", width: "100%" }}>
          <div style={{ display: "flex", gap: 12 }}>
            <div className="card-header-icon">
              <HistoryIcon size={18} />
            </div>
            <div>
              <h3>Recent Predictions</h3>
              <div className="subtitle">Stored locally in this browser — not synced to a server yet.</div>
            </div>
          </div>
          {history.length > 0 && (
            <button className="btn btn-ghost" onClick={handleClearAll}>
              <Trash2 size={14} />
              Clear all
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <div className="history-empty">
            No predictions yet. Head to Disease Detection and analyze a leaf to build up your history.
          </div>
        ) : (
          <div className="history-list">
            {history.map((entry) => (
              <div
                className="history-item"
                key={entry.id}
                onClick={() => onSelect?.(entry)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") onSelect?.(entry);
                }}
                style={{ cursor: onSelect ? "pointer" : "default" }}
              >
                {entry.imageDataUrl && <img className="history-thumb" src={entry.imageDataUrl} alt="" />}
                <div className="history-info">
                  <div className="history-disease">{entry.predictedClass}</div>
                  <div className="history-meta">
                    <span>{entry.fileName}</span>
                    <span>·</span>
                    <span>{entry.confidence}% confidence</span>
                    <span>·</span>
                    <span>{new Date(entry.timestamp).toLocaleString()}</span>
                  </div>
                </div>
                <button
                  className="remove-link"
                  onClick={(e) => handleDeleteOne(e, entry.id)}
                  aria-label={`Delete prediction for ${entry.fileName}`}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
