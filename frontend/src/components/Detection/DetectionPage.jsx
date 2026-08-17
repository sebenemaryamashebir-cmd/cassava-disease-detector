import { ScanLine, AlertCircle, CheckCircle2 } from "lucide-react";
import PageHeader from "../Common/PageHeader.jsx";
import UploadZone from "./UploadZone.jsx";
import ImagePreview from "./ImagePreview.jsx";
import AnalysisPipeline from "./AnalysisPipeline.jsx";
import EmptyResultState from "./EmptyResultState.jsx";
import DiagnosisCard from "../Results/DiagnosisCard.jsx";
import ProbabilityBreakdown from "../Results/ProbabilityBreakdown.jsx";
import AIRecommendation from "../Results/AIRecommendation.jsx";
import ExplainabilityCard from "../Results/ExplainabilityCard.jsx";
import SystemInfoCards from "../Results/SystemInfoCards.jsx";

export default function DetectionPage({
  file,
  previewUrl,
  result,
  loading,
  error,
  validationError,
  backendOnline,
  onFileSelected,
  onRemove,
  onNewPrediction,
  onAnalyze,
  onValidationError,
  onDismissValidationError,
}) {
  return (
    <div>
      <PageHeader
        title="Cassava Crop Health"
        subtitle="Detect cassava leaf diseases using computer vision and get AI-powered recommendations."
        showStatus
        backendOnline={backendOnline}
      />

      {error && (
        <div className="alert-card">
          <AlertCircle size={19} className="alert-icon" />
          <div style={{ flex: 1 }}>
            <div className="alert-title">Unable to analyze image</div>
            <div className="alert-desc">{error}</div>
            {file && (
              <button className="btn btn-ghost" onClick={onAnalyze}>
                Try Again
              </button>
            )}
          </div>
        </div>
      )}

      {validationError && (
        <div className="alert-card warning">
          <AlertCircle size={19} className="alert-icon" />
          <div style={{ flex: 1 }}>
            <div className="alert-title">Image not accepted</div>
            <div className="alert-desc">{validationError}</div>
          </div>
          <button className="btn btn-ghost" onClick={onDismissValidationError}>
            Dismiss
          </button>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div className="card-header-icon">
            <ScanLine size={18} />
          </div>
          <div>
            <h2>Diagnose a Cassava Leaf</h2>
            <div className="subtitle">
              Upload a clear image of a cassava leaf and our AI model will analyze it for common diseases.
            </div>
          </div>
        </div>

        <div className="detect-grid">
          <div>
            {!file ? (
              <UploadZone onFileSelected={onFileSelected} onValidationError={onValidationError} />
            ) : (
              <ImagePreview
                file={file}
                previewUrl={previewUrl}
                onRemove={onRemove}
                onAnalyze={onAnalyze}
                onNewPrediction={onNewPrediction}
                loading={loading}
                hasResult={!!result}
              />
            )}
            <AnalysisPipeline loading={loading} />
          </div>

          <div>
            {result && result.recommendation_error && (
              <div className="alert-card warning" style={{ marginBottom: 16 }}>
                <CheckCircle2 size={19} className="alert-icon" />
                <div>
                  <div className="alert-title">Diagnosis completed</div>
                  <div className="alert-desc">
                    {result.confidence < 50
                      ? "The AI wasn't confident enough in this diagnosis to generate a recommendation."
                      : "The disease prediction was successful, but the AI recommendation service is currently unavailable."}
                  </div>
                </div>
              </div>
            )}

            {!result ? (
              <EmptyResultState />
            ) : (
              <div>
                <DiagnosisCard predictedClass={result.predicted_class} confidence={result.confidence} />
                <ProbabilityBreakdown probabilities={result.probabilities} />
                <AIRecommendation recommendation={result.recommendation} />
                <ExplainabilityCard gradcamUrl={result.gradcam_url} originalImageUrl={previewUrl} />
              </div>
            )}
          </div>
        </div>
      </div>

      <SystemInfoCards backendOnline={backendOnline} />
    </div>
  );
}
