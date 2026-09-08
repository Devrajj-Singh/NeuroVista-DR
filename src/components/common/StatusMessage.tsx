import type { ReactNode } from 'react';

type StatusTone = 'success' | 'warning' | 'error' | 'info';

type StatusMessageProps = {
  tone: StatusTone;
  icon: ReactNode;
  heading: string;
  children?: ReactNode;
};

const TONE_CLASS: Record<StatusTone, string> = {
  success: 'status-message--success',
  warning: 'status-message--warning',
  error: 'status-message--error',
  info: 'status-message--info',
};

export function StatusMessage({ tone, icon, heading, children }: StatusMessageProps) {
  return (
    <div className={`status-message ${TONE_CLASS[tone]}`} role="status">
      <div className="status-message__icon" aria-hidden="true">
        {icon}
      </div>
      <div className="status-message__body">
        <h2 className="status-message__heading">{heading}</h2>
        {children && <div className="status-message__content">{children}</div>}
      </div>
    </div>
  );
}