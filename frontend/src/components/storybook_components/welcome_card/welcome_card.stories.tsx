import type { Meta, StoryObj } from '@storybook/react-vite';
import { SmileOutlined, UserOutlined } from '@ant-design/icons';
import { theme } from 'antd';

import { WelcomeCard } from './welcome_card.tsx';

const { useToken } = theme;

const meta: Meta<typeof WelcomeCard> = {
    component: WelcomeCard,
    title: 'Welcome Card',
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    render: () => {
        const { token } = useToken();
        return (
            <WelcomeCard
                icon={<SmileOutlined style={{ fontSize: 24, color: token.colorPrimary }} />}
                iconBgColor={token.colorPrimaryBg}
                title="Witaj Pacjencie!"
                description="Miło Cię widzieć w systemie sTOMs"
            />
        );
    },
};

export const WithSubtitle: Story = {
    render: () => {
        const { token } = useToken();
        return (
            <WelcomeCard
                icon={<UserOutlined style={{ fontSize: 24, color: token.colorSuccess }} />}
                iconBgColor={token.colorSuccessBg}
                title="Witaj, Pacjencie!"
                subtitle="Następna wizyta: 15 stycznia 2026"
            />
        );
    },
};
