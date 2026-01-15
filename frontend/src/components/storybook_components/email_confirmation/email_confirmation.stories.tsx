import type { Meta, StoryObj } from '@storybook/react-vite';
import { EmailConfirmation } from './email_confirmation.tsx';

const meta: Meta<typeof EmailConfirmation> = {
    component: EmailConfirmation,
    title: 'Email Confirmation',
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    render: () => {
        return (
            <EmailConfirmation
                    title="Zweryfikuj adres email"
                    description='Podaj kod składający się z 6 cyfr wysłany na podany adres email'
                    onChange={(value: string) => {
                        console.log('OTP Value:', value);
                    }}
                />          
        );
    },
};
