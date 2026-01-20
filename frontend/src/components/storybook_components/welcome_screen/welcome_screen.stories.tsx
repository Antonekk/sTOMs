import type { Meta, StoryObj } from '@storybook/react-vite';


import WelcomeScreen from './welcome_screen';


const meta: Meta<typeof WelcomeScreen> = {
  title: "Welcome/WelcomeScreen",
  component: WelcomeScreen,
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof WelcomeScreen>;

export const WelcomePage: Story = {
  args: {
    primaryButtonText: 'Zaloguj',
    secondaryButtonText: 'Zarejestruj',
    onPrimaryClick: () => {alert('Zaloguj')},
    onSecondaryClick: () => {alert('Zarejestruj')},
  },
};
