import type { Meta, StoryObj } from '@storybook/react';
import { NotificationBanner } from '@monorepo/component-library';

const meta = {
  title: 'Components/NotificationBanner',
  component: NotificationBanner,
  tags: ['autodocs'],
  args: {
    title: 'Something happened',
    children: 'Additional context lives here.',
    variant: 'info',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['info', 'warning', 'danger', 'success'],
    },
  },
} satisfies Meta<typeof NotificationBanner>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Info: Story = {};
export const Success: Story = {
  args: { variant: 'success', title: 'Saved', children: 'Your changes have been saved.' },
};
export const Warning: Story = {
  args: { variant: 'warning', title: 'Heads up', children: 'This will affect downstream consumers.' },
};
export const ChurnRiskDanger: Story = {
  name: 'Churn-risk (danger)',
  args: {
    variant: 'danger',
    title: 'High churn risk',
    children:
      'This account scored 0.87 on the churn-risk model. The CSM should reach out within 7 days.',
  },
};
export const Dismissable: Story = {
  args: {
    variant: 'info',
    title: 'Dismiss me',
    children: 'Has an X to dismiss.',
    onDismiss: () => console.log('dismissed'),
  },
};
