import { Leaf, LayoutDashboard, ScanLine, History, BookOpen, Info } from "lucide-react";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "detect", label: "Disease Detection", icon: ScanLine },
  { id: "history", label: "Prediction History", icon: History },
  { id: "guide", label: "Crop Guide", icon: BookOpen },
  { id: "about", label: "About", icon: Info },
];

export default function Sidebar({ active, onNavigate, open, onClose, backendOnline }) {
  return (
    <>
      <aside className={"sidebar" + (open ? " open" : "")}>
        <div className="sidebar-brand">
          <div className="sidebar-brand-mark">
            <Leaf size={19} strokeWidth={2.2} />
          </div>
          <div className="sidebar-brand-text">
            <div className="name">CassavaCare</div>
            <div className="tagline">AI Crop Health Assistant</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={"sidebar-link" + (active === id ? " active" : "")}
              onClick={() => onNavigate(id)}
              aria-current={active === id ? "page" : undefined}
            >
              <Icon size={17} strokeWidth={2} />
              {label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-status-row">
            <span className={"status-dot" + (backendOnline ? "" : " offline")} />
            {backendOnline ? "AI Model Online" : "AI Model Offline"}
          </div>
          <div className="sidebar-version">v2.0.0</div>
        </div>
      </aside>
      <div className={"sidebar-backdrop" + (open ? " open" : "")} onClick={onClose} />
    </>
  );
}
