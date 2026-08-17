import { Menu, Leaf } from "lucide-react";

export default function MobileNav({ onOpenMenu }) {
  return (
    <div className="mobile-topbar">
      <div className="brand">
        <Leaf size={18} />
        CassavaCare
      </div>
      <button className="mobile-menu-btn" onClick={onOpenMenu} aria-label="Open navigation menu">
        <Menu size={20} />
      </button>
    </div>
  );
}
