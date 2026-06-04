import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NotificationBanner } from './NotificationBanner';

describe('NotificationBanner', () => {
  it('renders an alert role for danger variant (churn-risk demo)', () => {
    render(
      <NotificationBanner variant="danger" title="High churn risk">
        This account is at risk of churn within 30 days.
      </NotificationBanner>,
    );
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent(/high churn risk/i);
    expect(alert.className).toContain('ml-banner--danger');
  });

  it('renders a status role for info variant', () => {
    render(<NotificationBanner variant="info">heads up</NotificationBanner>);
    expect(screen.getByRole('status')).toHaveTextContent(/heads up/i);
  });

  it('renders the dismiss button only when onDismiss is provided', () => {
    const onDismiss = vi.fn();
    const { rerender } = render(
      <NotificationBanner variant="warning">x</NotificationBanner>,
    );
    expect(screen.queryByRole('button', { name: /dismiss/i })).toBeNull();
    rerender(
      <NotificationBanner variant="warning" onDismiss={onDismiss}>
        x
      </NotificationBanner>,
    );
    fireEvent.click(screen.getByRole('button', { name: /dismiss/i }));
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });
});
