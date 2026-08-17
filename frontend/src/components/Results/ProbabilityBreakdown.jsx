import { Star } from "lucide-react";

export default function ProbabilityBreakdown({ probabilities }) {
  const sorted = Object.entries(probabilities || {}).sort((a, b) => b[1] - a[1]);
  if (sorted.length === 0) return null;

  return (
    <div className="prob-section">
      <div className="prob-section-title">Prediction Breakdown</div>
      <div className="prob-section-subtitle">Probability assigned to each detected class</div>

      <div className="prob-bars">
        {sorted.map(([label, pct], i) => (
          <div className="prob-row" key={label}>
            <div className="prob-row-top">
              <span className={"label" + (i === 0 ? " top-pick" : "")}>
                {i === 0 && <Star size={12} fill="currentColor" />}
                {label}
              </span>
              <span className="pct">{pct}%</span>
            </div>
            <div className="prob-track">
              <div
                className={"prob-fill" + (i === 0 ? " top" : "")}
                style={{ "--target-width": `${pct}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
