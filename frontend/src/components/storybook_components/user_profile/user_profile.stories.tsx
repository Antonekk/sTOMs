import type { Meta, StoryObj } from "@storybook/react-vite";
import UserProfile from "./user_profile";

const meta: Meta<typeof UserProfile> = {
    title: "Components/UserProfile",
    component: UserProfile,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Client: Story = {
    args: {
        onNavigate: (path) => { alert(`Nawiguj do ${path}`); },
        user: {
            id: "4e40aef3-c252-4d1e-a8df-8d1786d3d76b",
            first_name: "Anna",
            last_name: "Kowalska",
            email: "anna.kowalska@example.com",
            phone_number: "+48123456789",
            role: "CLIENT",
            patients: [
                {
                    id: "ae55d1b3-9f43-4541-beb1-5526678053fa",
                    first_name: "Anna",
                    last_name: "Kowalska",
                    birthday: "1995-05-20",
                    is_primary: true,
                    is_active: true,
                },
                {
                    id: "57a67de4-4a18-4dcb-acbd-18c977d0b455",
                    first_name: "Jan",
                    last_name: "Kowalski",
                    birthday: "2016-03-11",
                    is_primary: false,
                    is_active: true,
                },
            ],
        },
    },
};

export const Therapist: Story = {
    args: {
        onNavigate: (path) => { alert(`Nawiguj do ${path}`); },
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
