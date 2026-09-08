import { Component, type ReactNode } from 'react';
import { useLocalization } from '@/i18n';

type ErrorBoundaryProps = { children: ReactNode };
type ErrorBoundaryState = { hasError: boolean };

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <UnexpectedErrorFallback />;
    }
    return this.props.children;
  }
}

function UnexpectedErrorFallback() {
  const { t } = useLocalization();
  return (
    <div className="fatal-fallback" role="alert">
      <p>{t('error.title')}</p>
    </div>
  );
}