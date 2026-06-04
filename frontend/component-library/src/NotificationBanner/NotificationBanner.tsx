import type { HTMLAttributes, ReactNode } from 'react';
import './NotificationBanner.css';

export type NotificationVariant = 'info' | 'warning' | 'danger' | 'success';

export interface NotificationBannerProps
  extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  variant?: NotificationVariant;
  title?: ReactNode;
  children?: ReactNode;
  onDismiss?: () => void;
}

const ROLE: Record<NotificationVariant, 'alert' | 'status'> = {
  info: 'status',
  success: 'status',
  warning: 'alert',
  danger: 'alert',
};

export function NotificationBanner({
  variant = 'info',
  title,
  children,
  onDismiss,
  className,
  ...rest
}: NotificationBannerProps) {
  const classes = [
    'ml-banner',
    `ml-banner--${variant}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={classes} role={ROLE[variant]} {...rest}>
      <div className="ml-banner__content">
        {title ? <strong className="ml-banner__title">{title}</strong> : null}
        {children ? <div className="ml-banner__body">{children}</div> : null}
      </div>
      {onDismiss ? (
        <button
          type="button"
          className="ml-banner__dismiss"
          aria-label="Dismiss notification"
          onClick={onDismiss}
        >
          ×
        </button>
      ) : null}
    </div>
  );
}
