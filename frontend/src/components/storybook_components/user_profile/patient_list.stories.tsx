import type { Meta, StoryObj } from "@storybook/react-vite";
import PatientList from "./patient_list";

const meta: Meta<typeof PatientList> = {
    title: "Components/UserProfile/PatientList",
    component: PatientList,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const WithPatients: Story = {
    args: {
        patients: [
            {
                id: "ae55d1b3-9f43-4541-beb1-5526678053fa",
                user: "4e40aef3-c252-4d1e-a8df-8d1786d3d76b",
                first_name: "Anna",
                last_name: "Kowalska",
                date_of_birth: "1995-05-20",
                is_primary: true,
            },
            {
                id: "57a67de4-4a18-4dcb-acbd-18c977d0b455",
                user: "4e40aef3-c252-4d1e-a8df-8d1786d3d76b",
                first_name: "Jan",
                last_name: "Kowalski",
                date_of_birth: "2016-03-11",
                is_primary: false,
            },
        ],
    },
};

export const Empty: Story = {
    args: {
        patients: [],
    },
};
