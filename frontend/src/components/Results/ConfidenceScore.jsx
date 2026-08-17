function getConfidenceLevel(pct) {
  if (pct >= 80) return { level: "high", label: "High confidence", desc: "Model is very sure of this result." };
  if (pct >= 50) return { level: "moderate", label: "Moderate confidence", desc: "Consider a second opinion." };
  return { level: "low", label: "Low confidence", desc: "Result is uncertain — try a clearer photo." };
}

export default function ConfidenceScore({ confidence }) {
  const pct = Math.max(0, Math.min(100, Number(confidence) || 0));
  const { level, label, desc } = getConfidenceLevel(pct);

  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;

  const ringColor =
    level === "high" ? "var(--leaf-500)" : level === "moderate" ? "var(--amber-600)" : "var(--ink-400)";

  return (
    <div className="confidence-gauge">
      <div className="confidence-ring">
        <svg width="96" height="96" viewBox="0 0 96 96">
          <circle cx="48" cy="48" r={radius} fill="none" stroke="var(--line)" strokeWidth="8" />
          <circle
            cx="48"
            cy="48"
            r={radius}
            fill="none"
            stroke={ringColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.8s ease" }}
          />
        </svg>
        <div className="confidence-ring-value">
          {pct}%
          <span>confidence</span>
        </div>
      </div>
      <div className="confidence-label-block">
        <div className={"level " + level}>{label}</div>
        <div className="desc">{desc}</div>
      </div>
    </div>
  );
}
