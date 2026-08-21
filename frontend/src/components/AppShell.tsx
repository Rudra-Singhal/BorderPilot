import { NavLink, Outlet } from "react-router-dom";
import { useTheme } from "../lib/theme";
import { IconFlow, IconGrid, IconMoon, IconSun, IconTable } from "./icons";
import styles from "./AppShell.module.css";

const NAV = [
  { to: "/", label: "Dashboard", icon: IconGrid, end: true },
  { to: "/receivables", label: "Receivables", icon: IconTable, end: false },
  { to: "/netting-runs", label: "Netting runs", icon: IconFlow, end: false },
];

export function AppShell() {
  const { theme, toggle } = useTheme();

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
          <span className={styles.footerLabel}>Pooled SME netting engine</span>
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
