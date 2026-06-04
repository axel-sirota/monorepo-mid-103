import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
  stories: ['../stories/**/*.mdx', '../stories/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-links',
    {
      name: 'storybook-design-token',
      options: {
        preserveCSSVars: true,
      },
    },
  ],
  docs: {
    autodocs: 'tag',
  },
  typescript: {
    check: false,
  },
};

export default config;
