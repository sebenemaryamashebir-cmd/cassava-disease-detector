import { ScanEye } from "lucide-react";

// Designed so a future `result.gradcam_url` (or similar) can be wired in
// without restructuring this component: pass it as the `gradcamUrl` prop
// and swap the placeholder branch below for the two-image comparison.
export default function ExplainabilityCard({ gradcamUrl, originalImageUrl }) {
  return (
    <div>
      <div className="card-header" style={{ marginTop: 26 }}>
        <div className="card-header-icon">
          <ScanEye size={18} />
        </div>
        <div>
          <h3>Understanding the Prediction</h3>
          <div className="subtitle">Visual explanation of what influenced the AI's decision.</div>
        </div>
      </div>

      {gradcamUrl ? (
        <div className="detect-grid" style={{ marginTop: 14 }}>
          <div>
            <div className="prob-section-title" style={{ marginBottom: 8 }}>
              Original
            </div>
            <img src={originalImageUrl} alt="Original leaf" style={{ width: "100%", borderRadius: 12 }} />
          </div>
          <div>
            <div className="prob-section-title" style={{ marginBottom: 8 }}>
              Heatmap
            </div>
            <img src={gradcamUrl} alt="Model attention heatmap" style={{ width: "100%", borderRadius: 12 }} />
          </div>
          <p style={{ gridColumn: "1 / -1", fontSize: 13, color: "var(--ink-600)" }}>
            Highlighted regions indicate areas of the leaf that influenced the model's prediction.
          </p>
        </div>
      ) : (
        <div className="explain-placeholder">
          <ScanEye size={26} />
          <p>Visual explanation will appear here when explainability is enabled.</p>
        </div>
      )}
    </div>
  );
}
