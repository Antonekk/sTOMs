import type { Meta, StoryObj } from '@storybook/react-vite';


import ActionCard from './action_card.tsx';


export const ActionCardData = {
  title : "Card title",
  description: "Card description"
};


const meta : Meta<typeof ActionCard> ={
  component: ActionCard,
  title: 'Action Card',
  tags: ['autodocs'],

  excludeStories: /.*Data$/,
  args: {
    ...ActionCardData,
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {

};
