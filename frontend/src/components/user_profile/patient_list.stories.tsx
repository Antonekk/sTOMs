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
        onNavigate: (path) => { alert(`Nawiguj do ${path}`); },
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
};

export const Empty: Story = {
    args: {
        onNavigate: (path) => { alert(`Nawiguj do ${path}`); },
        patients: [],
    },
};

export const InactivePatients: Story = {
    args: {
        variant: "inactive",
        onNavigate: (path) => { alert(`Nawiguj do ${path}`); },
        onAction: async (action, id) => { alert(`${action} pacjenta ${id}`); },
        patients: [
            {
                id: "57a67de4-4a18-4dcb-acbd-18c977d0b455",
                first_name: "Jan",
                last_name: "Kowalski",
                birthday: "2016-03-11",
                is_primary: false,
                is_active: false,
            },
        ],
    },
};
