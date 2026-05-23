import type { Meta, StoryObj } from "@storybook/react-vite";
import AccountDetails from "./account_details";

const meta: Meta<typeof AccountDetails> = {
    title: "Components/UserProfile/AccountDetails",
    component: AccountDetails,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Client: Story = {
    args: {
        user: {
            id: "4e40aef3-c252-4d1e-a8df-8d1786d3d76b",
            first_name: "Anna",
            last_name: "Kowalska",
            email: "anna.kowalska@example.com",
            phone_number: "+48123456789",
            role: "CLIENT",
            patients: [],
        },
    },
};

export const Therapist: Story = {
    args: {
        user: {
            id: "9cbd6904-4c47-4fa6-9399-542e8d787944",
            first_name: "Marek",
            last_name: "Nowak",
            email: "marek.nowak@example.com",
            phone_number: "+48987654321",
            role: "THERAPIST",
            patients: [],
        },
    },
};

export const Admin: Story = {
    args: {
        user: {
            id: "8afe6b7e-a777-4b4e-8e31-8c0e4e7b6b84",
            first_name: "Alicja",
            last_name: "Admin",
            email: "admin@example.com",
            phone_number: "+48555111222",
            role: "ADMIN",
            patients: [],
        },
    },
};
