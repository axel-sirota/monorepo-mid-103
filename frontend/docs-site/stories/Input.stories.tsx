import type { Meta, StoryObj } from '@storybook/react';
import { Input } from '@monorepo/component-library';

const meta = {
  title: 'Components/Input',
  component: Input,
  tags: ['autodocs'],
  args: {
    label: 'Email',
    placeholder: 'you@example.com',
  },
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Basic: Story = {};
export const WithHint: Story = {
  args: { hint: 'We will never share your email with anyone else.' },
};
export const WithError: Story = {
  args: { error: 'Email is required.', defaultValue: '' },
};
