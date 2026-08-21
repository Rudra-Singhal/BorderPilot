import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useTheme } from "../lib/theme";
import { useAuth } from "../lib/auth";
import {
  IconActivity,
  IconAssistant,
  IconBuildings,
  IconDroplet,
  IconExchange,
  IconFlow,
  IconGrid,
  IconMoon,
  IconShield,
  IconSun,
  IconTable,
  IconTrend,
} from "./icons";
import styles from "./AppShell.module.css";

const NAV = [
  { to: "/", label: "Overview", icon: IconGrid, end: true },
  { to: "/forecast", label: "Cash & Forecast", icon: IconTrend, end: false },
  { to: "/receivables", label: "Receivables", icon: IconTable, end: false },
  { to: "/counterparties", label: "Counterparties", icon: IconBuildings, end: false },
  { to: "/liquidity", label: "Liquidity", icon: IconDroplet, end: false },
  { to: "/netting-runs", label: "Netting", icon: IconFlow, end: false },
  { to: "/fx", label: "FX & Exposure", icon: IconExchange, end: false },
  { to: "/compliance", label: "Compliance", icon: IconShield, end: false },
  { to: "/assistant", label: "Assistant", icon: IconAssistant, end: false },
  { to: "/activity", label: "Activity", icon: IconActivity, end: false },
];

export function AppShell() {
  const { theme, toggle } = useTheme();
  const { logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <span className={styles.brandMark} />
          <span className={styles.brandName}>BorderPilot</span>
        </div>
        <nav className={styles.nav}>
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `${styles.navItem} ${isActive ? styles.navItemActive : ""}`}
            >
              <Icon />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className={styles.sidebarFooter}>
          <span className={styles.footerLabel}>Pooled SME underwriting orchestration</span>
          <button className={styles.logout} onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </aside>

      <div className={styles.main}>
        <header className={styles.topbar}>
          <div />
          <button className={styles.themeToggle} onClick={toggle} aria-label="Toggle color theme">
            {theme === "light" ? <IconMoon /> : <IconSun />}
          </button>
        </header>
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
