import StatusBadge from "./StatusBadge.jsx";

export default function PageHeader({ title, subtitle, showStatus, backendOnline }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <div className="page-subtitle">{subtitle}</div>}
      </div>
      {showStatus && <StatusBadge online={backendOnline} />}
    </div>
  );
}
