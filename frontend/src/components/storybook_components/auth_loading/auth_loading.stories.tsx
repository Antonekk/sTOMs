import type { Meta, StoryObj } from '@storybook/react';
import AuthLoading from './auth_loading';

const meta = {
    title: 'Components/AuthLoading',
    component: AuthLoading,
    parameters: {
        layout: 'fullscreen',
    },
    tags: ['autodocs'],
} satisfies Meta<typeof AuthLoading>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
