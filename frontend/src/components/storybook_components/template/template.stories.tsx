import type { Meta, StoryObj } from '@storybook/react-vite';


import Template from './template.tsx';


const items = Array.from({ length: 4 }).map((_, index) => ({
  key: index + 1,
  label: `nav ${(index + 1).toString()}`,
}));


export const TemplatesData = {
  menu_items : items,
};

const meta : Meta<typeof Template> = {
  component: Template,
  title: 'Template',
  tags: ['autodocs'],

  excludeStories: /.*Data$/,
  args: {
    ...TemplatesData,
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {

};

