import { CheckCircle } from "lucide-react";
import PageHeader from "../Common/PageHeader.jsx";

const CAPABILITIES = [
  "Uses computer vision to classify cassava leaf diseases",
  "Uses an AI model trained for cassava disease recognition",
  "Provides confidence scores for every prediction",
  "Uses an LLM to generate personalized crop-care recommendations",
  "Designed as an agricultural decision-support tool, not a replacement for expert diagnosis",
];

const TIMELINE = ["Upload", "Analyze", "Diagnose", "Understand", "Act"];

export default function AboutPage() {
  return (
    <div>
      <PageHeader title="About CassavaCare" subtitle="A computer vision and LLM-powered crop health assistant." />

      <div className="card">
        <h3 style={{ marginBottom: 14 }}>What this application does</h3>
        <div className="about-list">
          {CAPABILITIES.map((c) => (
            <div className="about-list-item" key={c}>
              <CheckCircle size={16} />
              {c}
            </div>
          ))}
        </div>

        <h3 style={{ marginTop: 30, marginBottom: 4 }}>How it works</h3>
        <div className="timeline">
          {TIMELINE.map((step, i) => (
            <div className="timeline-step" key={step}>
              <div className="timeline-node">
                <div className="timeline-dot">{i + 1}</div>
                <div className="timeline-label">{step}</div>
              </div>
              {i < TIMELINE.length - 1 && <div className="timeline-line" />}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
