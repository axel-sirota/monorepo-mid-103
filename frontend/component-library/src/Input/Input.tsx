import { forwardRef, useId } from 'react';
import type { InputHTMLAttributes, ReactNode } from 'react';
import './Input.css';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: ReactNode;
  hint?: ReactNode;
  error?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, hint, error, id, className, ...rest }, ref) => {
    const reactId = useId();
    const inputId = id ?? `ml-input-${reactId}`;
    const hintId = hint ? `${inputId}-hint` : undefined;
    const errorId = error ? `${inputId}-error` : undefined;
    const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined;

    const classes = ['ml-input', error ? 'ml-input--error' : '', className]
      .filter(Boolean)
      .join(' ');

    return (
      <div className="ml-input-field">
        <label htmlFor={inputId} className="ml-input__label">
          {label}
        </label>
        <input
          ref={ref}
          id={inputId}
          className={classes}
          aria-describedby={describedBy}
          aria-invalid={error ? true : undefined}
          {...rest}
        />
        {hint ? (
          <span id={hintId} className="ml-input__hint">
            {hint}
          </span>
        ) : null}
        {error ? (
          <span id={errorId} className="ml-input__error" role="alert">
            {error}
          </span>
        ) : null}
      </div>
    );
  },
);

Input.displayName = 'Input';
