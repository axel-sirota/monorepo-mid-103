import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card', () => {
  it('renders children inside the body', () => {
    render(<Card>hello world</Card>);
    expect(screen.getByText(/hello world/i)).toBeInTheDocument();
  });

  it('renders a header when title is provided', () => {
    render(<Card title="My Title">body</Card>);
    expect(screen.getByText(/my title/i)).toBeInTheDocument();
  });

  it('renders a footer when footer is provided', () => {
    render(<Card footer={<span>foot</span>}>body</Card>);
    expect(screen.getByText(/foot/i)).toBeInTheDocument();
  });
});
