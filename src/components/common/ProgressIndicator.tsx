type StepStatus = 'done' | 'active' | 'pending';

type ProgressIndicatorProps = {
  steps: string[];
  current: number;
  labels?: string[];
};

export function ProgressIndicator({ steps, current, labels }: ProgressIndicatorProps) {
  return (
    <ol className="progress" aria-label={labels?.[0] ?? 'Progress'}>
      {steps.map((step, index) => {
        const status: StepStatus =
          index < current ? 'done' : index === current ? 'active' : 'pending';
        return (
          <li
            key={step}
            className={`progress__step progress__step--${status}`}
            aria-current={status === 'active' ? 'step' : undefined}
          >
            <span className="progress__marker" aria-hidden="true">
              {status === 'done' ? '✓' : status === 'active' ? '●' : '○'}
            </span>
            <span className="progress__label">{step}</span>
          </li>
        );
      })}
    </ol>
  );
}