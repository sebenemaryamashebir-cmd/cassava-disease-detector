import { Leaf, AlertTriangle } from "lucide-react";
import ConfidenceScore from "./ConfidenceScore.jsx";

export default function DiagnosisCard({ predictedClass, confidence }) {
  const isHealthy = predictedClass === "Healthy";

  return (
    <div>
      <div className="diagnosis-eyebrow">AI Diagnosis</div>
      <div className="diagnosis-main">
        <div className="diagnosis-name-row">
          <div className={"diagnosis-icon-badge " + (isHealthy ? "healthy" : "warning")}>
            {isHealthy ? <Leaf size={24} /> : <AlertTriangle size={24} />}
          </div>
          <div>
            <div className="diagnosis-status-label">
              {isHealthy ? "Your cassava leaf appears healthy" : "Possible disease detected"}
            </div>
            <div className={"diagnosis-name" + (isHealthy ? "" : " warning")}>{predictedClass}</div>
          </div>
        </div>

        <ConfidenceScore confidence={confidence} />
      </div>
    </div>
  );
}
