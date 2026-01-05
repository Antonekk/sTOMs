import type { Preview } from '@storybook/react-vite';
import { ConfigProvider } from 'antd';
import 'antd/dist/reset.css';

const preview: Preview = {
  decorators: [
    (Story) => (
      <ConfigProvider
        theme={{
          components: {
            Input: {
              controlHeightLG: 64,
              fontSizeLG: 28,
            },
          },
        }}
      >
        <Story />
      </ConfigProvider>
    ),
  ],

  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    a11y: {
      test: 'todo',
    },
  },
};

export default preview;