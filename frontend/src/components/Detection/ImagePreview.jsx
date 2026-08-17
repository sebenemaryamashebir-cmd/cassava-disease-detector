import { CheckCircle, X } from "lucide-react";

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return "";
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(0)} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

export default function ImagePreview({ file, previewUrl, onRemove, onAnalyze, onNewPrediction, loading, hasResult }) {
  return (
    <div>
      <div className="image-preview">
        <img src={previewUrl} alt={`Preview of ${file.name}`} />
        <div className="image-ready-badge">
          <CheckCircle size={13} />
          Image Ready
        </div>
      </div>

      <div className="image-meta-row">
        <div>
          <span className="filename">{file.name}</span>
          {file.size != null && <span> · {formatBytes(file.size)}</span>}
        </div>
        <button className="remove-link" onClick={onRemove} disabled={loading}>
          <X size={13} />
          Remove
        </button>
      </div>

      <div className="analyze-cta">
        <button
          className="btn btn-primary btn-full"
          onClick={hasResult ? onNewPrediction : onAnalyze}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner" /> Analyzing leaf...
            </>
          ) : hasResult ? (
            "Analyze Another Leaf"
          ) : (
            "Analyze Leaf"
          )}
        </button>
      </div>
    </div>
  );
}
