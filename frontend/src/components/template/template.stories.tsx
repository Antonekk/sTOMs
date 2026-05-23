import type { Meta, StoryObj } from '@storybook/react-vite';


import Template from './template.tsx';


const meta: Meta<typeof Template> = {
  title: "Layout/Template",
  component: Template,
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof Template>;

export const Guest: Story = {
  args: {
    isAuthenticated: false,
    onNavigate: (path) => {alert(`Nawiguj do ${path}`)},
    children: <div>Public content</div>,
  },
};

export const Client: Story = {
  args: {
    isAuthenticated: true,
    role: "CLIENT",
    userName: "Klient",
    unreadNotificationCount: 2,
    onLogoutClick: () => {alert("Wyloguj")},
    onNavigate: (path) => {alert(`Nawiguj do ${path}`)},
    children: <div>Client dashboard</div>,
  },
};

export const Therapist: Story = {
  args: {
    isAuthenticated: true,
    role: "THERAPIST",
    userName: "Terapeuta",
    onLogoutClick: () => {alert("Wyloguj")},
    onNavigate: (path) => {alert(`Nawiguj do ${path}`)},
    children: <div>Therapist dashboard</div>,
  },
};

