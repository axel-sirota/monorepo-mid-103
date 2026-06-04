import type { Meta, StoryObj } from '@storybook/react';
import { Card, Button } from '@monorepo/component-library';

const meta = {
  title: 'Components/Card',
  component: Card,
  tags: ['autodocs'],
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Basic: Story = {
  args: {
    title: 'Account: Acme Corp',
    children:
      'A short description of this account. Lives inside the body of the card.',
  },
};

export const WithFooter: Story = {
  args: {
    title: 'Quarterly summary',
    footer: <Button size="sm">View details</Button>,
    children: 'Revenue is up 12% quarter-over-quarter.',
  },
};

export const BodyOnly: Story = {
  args: {
    children: 'No header, no footer — just content.',
  },
};
