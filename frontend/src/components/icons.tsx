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
