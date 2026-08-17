import { Sparkles, ScanEye, Gauge, Lightbulb } from "lucide-react";

const FEATURES = [
  { icon: ScanEye, label: "AI Disease Detection" },
  { icon: Gauge, label: "Confidence Analysis" },
  { icon: Lightbulb, label: "Smart Recommendations" },
];

export default function EmptyResultState() {
  return (
    <div className="empty-result">
      <div className="empty-result-icon">
        <Sparkles size={28} strokeWidth={1.8} />
      </div>
      <h3>Your diagnosis will appear here</h3>
      <p>Upload a cassava leaf image to receive an AI-powered disease prediction and crop-care recommendation.</p>

      <div className="empty-feature-row">
        {FEATURES.map(({ icon: Icon, label }) => (
          <div className="empty-feature" key={label}>
            <div className="empty-feature-icon">
              <Icon size={17} />
            </div>
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}
