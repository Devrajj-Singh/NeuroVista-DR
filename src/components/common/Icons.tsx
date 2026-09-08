import type { SVGProps } from 'react';

type IconProps = SVGProps<SVGSVGElement>;

function base(props: IconProps, size: number): IconProps {
  return {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 2,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    'aria-hidden': true,
    ...props,
  };
}

export function IconCheck(props: IconProps = {}) {
  return (
    <svg {...base(props, 16)}>
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

export function IconWarning(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" x2="12" y1="9" y2="13" />
      <line x1="12" x2="12.01" y1="17" y2="17" />
    </svg>
  );
}

export function IconError(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <circle cx="12" cy="12" r="10" />
      <line x1="15" x2="9" y1="9" y2="15" />
      <line x1="9" x2="15" y1="9" y2="15" />
    </svg>
  );
}

export function IconInfo(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <circle cx="12" cy="12" r="10" />
      <line x1="12" x2="12" y1="16" y2="12" />
      <line x1="12" x2="12.01" y1="8" y2="8" />
    </svg>
  );
}

export function IconUpload(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" x2="12" y1="3" y2="15" />
    </svg>
  );
}

export function IconImage(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <polyline points="21 15 16 10 5 21" />
    </svg>
  );
}

export function IconEye(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

export function IconReport(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" x2="8" y1="13" y2="13" />
      <line x1="16" x2="8" y1="17" y2="17" />
    </svg>
  );
}

export function IconRefresh(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <polyline points="23 4 23 10 17 10" />
      <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
    </svg>
  );
}

export function IconArrowLeft(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <line x1="19" y1="12" x2="5" y2="12" />
      <polyline points="12 19 5 12 12 5" />
    </svg>
  );
}

export function IconGlobe(props: IconProps = {}) {
  return (
    <svg {...base(props, 18)}>
      <circle cx="12" cy="12" r="10" />
      <line x1="2" x2="22" y1="12" y2="12" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  );
}

export function IconSun(props: IconProps = {}) {
  return (
    <svg {...base(props, 18)}>
      <circle cx="12" cy="12" r="4" />
      <line x1="12" x2="12" y1="2" y2="4" />
      <line x1="12" x2="12" y1="20" y2="22" />
      <line x1="4.93" x2="6.34" y1="4.93" y2="6.34" />
      <line x1="17.66" x2="19.07" y1="17.66" y2="19.07" />
      <line x1="2" x2="4" y1="12" y2="12" />
      <line x1="20" x2="22" y1="12" y2="12" />
      <line x1="4.93" x2="6.34" y1="19.07" y2="17.66" />
      <line x1="17.66" x2="19.07" y1="6.34" y2="4.93" />
    </svg>
  );
}

export function IconMoon(props: IconProps = {}) {
  return (
    <svg {...base(props, 18)}>
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
}

export function IconScan(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <path d="M3 7V5a2 2 0 0 1 2-2h2" />
      <path d="M17 3h2a2 2 0 0 1 2 2v2" />
      <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
      <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
      <line x1="7" x2="17" y1="12" y2="12" />
    </svg>
  );
}

export function IconDots(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)} fill="currentColor" stroke="none">
      <circle cx="5" cy="12" r="1.6" />
      <circle cx="12" cy="12" r="1.6" />
      <circle cx="19" cy="12" r="1.6" />
    </svg>
  );
}

export function IconHome(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.5V21h14V9.5" />
      <path d="M9.5 21v-6h5v6" />
    </svg>
  );
}

export function IconBook(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
  );
}

export function IconClock(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

export function IconTrash(props: IconProps = {}) {
  return (
    <svg {...base(props, 20)}>
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </svg>
  );
}

export function IconChevronRight(props: IconProps = {}) {
  return (
    <svg {...base(props, 18)}>
      <polyline points="9 18 15 12 9 6" />
    </svg>
  );
}