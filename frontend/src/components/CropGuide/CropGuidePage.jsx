import { ShieldCheck, AlertTriangle } from "lucide-react";
import PageHeader from "../Common/PageHeader.jsx";
import { DISEASE_CLASSES } from "../../lib/diseaseInfo.js";

export default function CropGuidePage() {
  return (
    <div>
      <PageHeader
        title="Cassava Disease Guide"
        subtitle="General background on the classes this model recognizes. Not a substitute for expert advice."
      />

      <div className="crop-guide-grid">
        {DISEASE_CLASSES.map((d) => (
          <div className="crop-card" key={d.key}>
            <div className="crop-card-head">
              <div className={"crop-card-icon " + d.tone}>
                {d.tone === "healthy" ? <ShieldCheck size={18} /> : <AlertTriangle size={18} />}
              </div>
              <h4>{d.label}</h4>
            </div>
            <p className="desc">{d.description}</p>
            <div className="prevention">{d.prevention}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
