import { useCallback, useRef, useState, type DragEvent } from 'react';
import { motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { IconUpload } from '@/components/common/Icons';
import { validateImageFile, type FileValidationError } from '@/utils/validators';

type ImageUploaderProps = {
  onSelect: (file: File) => void;
};

export function ImageUploader({ onSelect }: ImageUploaderProps) {
  const { t } = useLocalization();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<FileValidationError>(null);

  const handleFile = useCallback(
    (file: File | undefined) => {
      const error = validateImageFile(file);
      setValidationError(error);
      if (error || !file) return;
      onSelect(file);
    },
    [onSelect],
  );

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    handleFile(file);
  }

  function onDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(true);
  }

  function onDragLeave() {
    setIsDragging(false);
  }

  const errorMessage =
    validationError === 'type'
      ? t('upload.invalidType')
      : validationError === 'size'
        ? t('upload.invalidSize')
        : null;

  return (
    <Card>
      <div className="upload">
        <motion.div
          className={`upload__dropzone${isDragging ? ' upload__dropzone--active' : ''}`}
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault();
              inputRef.current?.click();
            }
          }}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          aria-label={t('upload.dragDrop')}
        >
          <span className="upload__icon" aria-hidden="true">
            <IconUpload />
          </span>
          <p className="upload__drag-text">{t('upload.dragDrop')}</p>
          <p className="upload__or">{t('upload.or')}</p>
          <Button
            variant="secondary"
            onClick={(event) => {
              event.stopPropagation();
              inputRef.current?.click();
            }}
          >
            {t('upload.browse')}
          </Button>
          <p className="upload__formats">{t('upload.supportedFormats')}</p>
        </motion.div>

        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,.jpg,.jpeg,.png"
          className="visually-hidden"
          onChange={(event) => handleFile(event.target.files?.[0])}
        />

        {errorMessage && (
          <motion.p
            className="upload__error"
            role="alert"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {errorMessage}
          </motion.p>
        )}
      </div>
    </Card>
  );
}