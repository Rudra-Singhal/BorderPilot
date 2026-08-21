type IconProps = { size?: number };

export function IconGrid({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <rect x="2.5" y="2.5" width="6.5" height="6.5" rx="1.3" stroke="currentColor" strokeWidth="1.5" />
      <rect x="11" y="2.5" width="6.5" height="6.5" rx="1.3" stroke="currentColor" strokeWidth="1.5" />
      <rect x="2.5" y="11" width="6.5" height="6.5" rx="1.3" stroke="currentColor" strokeWidth="1.5" />
      <rect x="11" y="11" width="6.5" height="6.5" rx="1.3" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconTable({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <rect x="2.5" y="3.5" width="15" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      <line x1="2.5" y1="7.8" x2="17.5" y2="7.8" stroke="currentColor" strokeWidth="1.5" />
      <line x1="7.6" y1="7.8" x2="7.6" y2="16.5" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconFlow({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <circle cx="4" cy="5" r="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="4" cy="15" r="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="16" cy="10" r="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M5.8 5.9 14.3 9.1" stroke="currentColor" strokeWidth="1.5" />
      <path d="M5.8 14.1 14.3 10.9" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconSun({ size = 16 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="3.4" stroke="currentColor" strokeWidth="1.5" />
      <g stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <line x1="10" y1="2.2" x2="10" y2="4" />
        <line x1="10" y1="16" x2="10" y2="17.8" />
        <line x1="2.2" y1="10" x2="4" y2="10" />
        <line x1="16" y1="10" x2="17.8" y2="10" />
        <line x1="4.6" y1="4.6" x2="5.9" y2="5.9" />
        <line x1="14.1" y1="14.1" x2="15.4" y2="15.4" />
        <line x1="4.6" y1="15.4" x2="5.9" y2="14.1" />
        <line x1="14.1" y1="5.9" x2="15.4" y2="4.6" />
      </g>
    </svg>
  );
}

export function IconMoon({ size = 16 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <path
        d="M16.5 12.4A7 7 0 1 1 7.6 3.5a5.6 5.6 0 0 0 8.9 8.9Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconArrowRight({ size = 14 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
      <path d="M3 8h9.5M8.5 4l4.5 4-4.5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconDownload({ size = 14 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
      <path d="M8 2v8m0 0 3-3M8 10 5 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3 12.5v1a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

export function IconTrend({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <path d="M2.5 15 7 9.5l3 3 6-7.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M13 5h3v3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconBuildings({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <rect x="2.5" y="7" width="6" height="10.5" rx="1" stroke="currentColor" strokeWidth="1.5" />
      <rect x="11.5" y="2.5" width="6" height="15" rx="1" stroke="currentColor" strokeWidth="1.5" />
      <line x1="4.7" y1="9.5" x2="4.7" y2="9.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <line x1="13.7" y1="5.5" x2="13.7" y2="5.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <line x1="13.7" y1="9" x2="13.7" y2="9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

export function IconDroplet({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <path
        d="M10 2.5s5.5 6.4 5.5 10.2a5.5 5.5 0 1 1-11 0C4.5 8.9 10 2.5 10 2.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconExchange({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <path d="M3 6.5h11.5M14.5 6.5 11.5 3.5M14.5 6.5 11.5 9.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M17 13.5H5.5M5.5 13.5 8.5 10.5M5.5 13.5 8.5 16.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconShield({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <path
        d="M10 2.5 16.5 5v5c0 4-2.8 6.7-6.5 7.5C6.3 16.7 3.5 14 3.5 10V5L10 2.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path d="M7.3 10 9.2 11.9 12.9 8.1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconAssistant({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <rect x="2.5" y="4" width="15" height="10" rx="2.5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M7 17.5 8.5 14h3l1.5 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <line x1="6.5" y1="8" x2="6.5" y2="8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <line x1="10" y1="8" x2="10" y2="8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <line x1="13.5" y1="8" x2="13.5" y2="8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function IconActivity({ size = 17 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="7.5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M10 5.5V10l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
