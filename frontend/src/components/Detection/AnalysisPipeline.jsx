import { useEffect, useState } from "react";
import { Check } from "lucide-react";

// This is a purely cosmetic, timed sequence shown while waiting for the
// backend response — it does NOT reflect real backend telemetry, since the
// API does not expose stage-by-stage progress. It simply reassures the user
// that something is happening and roughly what kind of work is underway.
const STEPS = ["Preparing image", "Running AI model", "Generating recommendation"];
const STEP_DURATION_MS = 1400;

export default function AnalysisPipeline({ loading }) {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    if (!loading) {
      setActiveIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setActiveIndex((i) => Math.min(i + 1, STEPS.length - 1));
    }, STEP_DURATION_MS);
    return () => clearInterval(interval);
  }, [loading]);

  if (!loading) return null;

  return (
    <div className="pipeline" role="status" aria-live="polite">
      {STEPS.map((step, i) => (
        <span
          key={step}
          className={"pipeline-step" + (i === activeIndex ? " active" : i < activeIndex ? " done" : "")}
        >
          {i < activeIndex && <Check size={12} />}
          {step}
        </span>
      ))}
    </div>
  );
}
