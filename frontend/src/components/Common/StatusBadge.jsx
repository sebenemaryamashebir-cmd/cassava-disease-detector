export default function StatusBadge({ online = true, label }) {
  return (
    <div className="page-header-status">
      <span className={"status-dot" + (online ? "" : " offline")} />
      {label || (online ? "AI System Online" : "AI System Offline")}
    </div>
  );
}
