import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Input } from './Input';

describe('Input', () => {
  it('associates the label with the input via htmlFor/id', () => {
    render(<Input label="Email" placeholder="you@example.com" />);
    const input = screen.getByLabelText(/email/i);
    expect(input).toBeInTheDocument();
    expect(input.tagName).toBe('INPUT');
  });

  it('exposes hint text via aria-describedby', () => {
    render(<Input label="Email" hint="We will not share it." />);
    const input = screen.getByLabelText(/email/i);
    const describedBy = input.getAttribute('aria-describedby');
    expect(describedBy).toBeTruthy();
    const hint = document.getElementById(describedBy!.split(' ')[0]);
    expect(hint).toHaveTextContent(/we will not share it/i);
  });

  it('marks the input invalid and shows an error when error is provided', () => {
    render(<Input label="Email" error="Required" />);
    const input = screen.getByLabelText(/email/i);
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByRole('alert')).toHaveTextContent(/required/i);
  });
});
