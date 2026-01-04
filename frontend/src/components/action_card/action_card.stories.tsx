import type { Meta, StoryObj } from '@storybook/react-vite';
import { PlusOutlined, BellFilled, FileTextOutlined } from '@ant-design/icons';
import { theme } from 'antd';

import { ActionCard } from './action_card.tsx';

const { useToken } = theme;

const meta: Meta<typeof ActionCard> = {
  component: ActionCard,
  title: 'Action Card',
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const NewReservation: Story = {
  render: () => {
    const { token } = useToken();
    return (
      <ActionCard
        icon={<PlusOutlined style={{ fontSize: 24, color: token.colorPrimary}} />}
        iconBgColor={token.colorPrimaryBg}
        title="Nowa rezerwacja"
        description="Zarezerwuj następną wizytę"
        buttonText="Zarezerwuj"
        buttonColor={token.colorPrimary}
      />
    );
  },
};

export const Exercises: Story = {
  render: () => {
    const { token } = useToken();
    return (
      <ActionCard
        icon={<BellFilled style={{ fontSize: 24, color: token.colorSuccess }} />}
        iconBgColor={token.colorSuccessBg}
        title="Ćwiczenia"
        description="Wykonaj ćwiczenia"
        buttonText="Ćwiczenia"
        buttonColor={token.colorSuccess}
      />
    );
  },
};

export const VisitHistory: Story = {
  render: () => {
    const { token } = useToken();
    return (
      <ActionCard
        icon={<FileTextOutlined style={{ fontSize: 24, color: token.colorInfo }} />}
        iconBgColor={token.colorInfoBg}
        title="Historia wizyt"
        description="Zobacz pełną historię wizyt"
        buttonText="Historia"
        buttonColor={token.colorInfo}
      />
    );
  },
};
