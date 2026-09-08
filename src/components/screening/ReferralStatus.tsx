import { Badge } from '@/components/common/Badge';
import { IconCheck, IconWarning } from '@/components/common/Icons';
import { useLocalization } from '@/i18n';

type ReferralStatusProps = {
  referable: boolean;
};

export function ReferralStatus({ referable }: ReferralStatusProps) {
  const { t } = useLocalization();

  if (referable) {
    return (
      <div className="referral referral--referable">
        <Badge tone="warning" icon={<IconWarning />} subtle>
          {t('result.referable')}
        </Badge>
        <p className="referral__hint">{t('result.referableHint')}</p>
      </div>
    );
  }

  return (
    <div className="referral referral--non-referable">
      <Badge tone="success" icon={<IconCheck />} subtle>
        {t('result.nonReferable')}
      </Badge>
      <p className="referral__hint">{t('result.nonReferableHint')}</p>
    </div>
  );
}