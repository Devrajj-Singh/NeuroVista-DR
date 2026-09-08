import { MAX_FILE_SIZE, SUPPORTED_IMAGE_TYPES } from './constants';

export function isSupportedImage(file: File): boolean {
  return SUPPORTED_IMAGE_TYPES.includes(file.type as (typeof SUPPORTED_IMAGE_TYPES)[number]);
}

export function isValidFileSize(file: File): boolean {
  return file.size <= MAX_FILE_SIZE;
}

export type FileValidationError = 'type' | 'size' | null;

export function validateImageFile(file: File | undefined): FileValidationError {
  if (!file) return null;
  if (!isSupportedImage(file)) return 'type';
  if (!isValidFileSize(file)) return 'size';
  return null;
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
