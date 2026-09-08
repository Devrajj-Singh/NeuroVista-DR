import type { QualityReason } from '@/types/screening';

export const SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/png'] as const;
export const SUPPORTED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png'] as const;
export const MAX_FILE_SIZE = 10 * 1024 * 1024;

export const REFERABLE_THRESHOLD = 2;

interface ICDRGradeInfo {
  name: string;
  severityKey: string;
  referable: boolean;
}

export const ICDR_GRADES: Record<number, ICDRGradeInfo> = {
  0: { name: 'Grade 0', severityKey: 'icdr.grade0', referable: false },
  1: { name: 'Grade 1', severityKey: 'icdr.grade1', referable: false },
  2: { name: 'Grade 2', severityKey: 'icdr.grade2', referable: true },
  3: { name: 'Grade 3', severityKey: 'icdr.grade3', referable: true },
  4: { name: 'Grade 4', severityKey: 'icdr.grade4', referable: true },
};

export const QUALITY_REASON_KEYS: Record<Exclude<QualityReason, null>, string> = {
  low_focus: 'quality.whyBlurry',
  too_dark: 'quality.whyDark',
  poor_field_of_view: 'quality.whyFieldOfView',
  insufficient_quality: 'quality.whyInsufficient',
};

export const SCREEN_TRANSITION_MS = 300;
