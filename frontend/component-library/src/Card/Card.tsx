import type { HTMLAttributes, ReactNode } from 'react';
import './Card.css';

export interface CardProps extends Omit<HTMLAttributes<HTMLElement>, 'title'> {
  title?: ReactNode;
  footer?: ReactNode;
  children?: ReactNode;
}

export function Card({ title, footer, children, className, ...rest }: CardProps) {
  const classes = ['ml-card', className].filter(Boolean).join(' ');
  return (
    <section className={classes} {...rest}>
      {title !== undefined ? <header className="ml-card__header">{title}</header> : null}
      <div className="ml-card__body">{children}</div>
      {footer !== undefined ? <footer className="ml-card__footer">{footer}</footer> : null}
    </section>
  );
}
