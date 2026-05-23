import type { Preview } from '@storybook/react-vite';
import { ConfigProvider } from 'antd';
import { MemoryRouter } from 'react-router-dom';

const preview: Preview = {
  decorators: [
    (Story) => (
      <MemoryRouter>
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
      </MemoryRouter>
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