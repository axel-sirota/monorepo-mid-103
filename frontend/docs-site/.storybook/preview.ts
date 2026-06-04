import type { Preview } from '@storybook/react';
import '@monorepo/design-tokens/tokens.css';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    designToken: {
      defaultTab: 'Colors',
    },
  },
};

export default preview;
