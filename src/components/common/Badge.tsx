import type { ReactNode } from 'react';

type BadgeTone = 'success' | 'warning' | 'error' | 'info' | 'neutral';

type BadgeProps = {
  tone: BadgeTone;
  children: ReactNode;
  icon?: ReactNode;
  subtle?: boolean;
};

const TONE_CLASS: Record<BadgeTone, string> = {
  success: 'badge--success',
  warning: 'badge--warning',
  error: 'badge--error',
  info: 'badge--info',
  neutral: 'badge--neutral',
};

export function Badge({ tone, children, icon, subtle = false }: BadgeProps) {
  const classes = ['badge', TONE_CLASS[tone], subtle ? 'badge--subtle' : '']
    .filter(Boolean)
    .join(' ');

  return (
    <span className={classes} role="status">
      {icon && <span className="badge__icon" aria-hidden="true">{icon}</span>}
      <span className="badge__label">{children}</span>
    </span>
  );
}