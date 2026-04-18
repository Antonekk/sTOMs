import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import PatientSelector from "./patient_selector";

const meta: Meta<typeof PatientSelector> = {
    title: "Components/PatientSelector",
    component: PatientSelector,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

const patients = [
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
];

export const Default: Story = {
    render: () => {
        const [value, setValue] = useState<string | undefined>(patients[0]?.id);
        return (
            <PatientSelector
                patients={patients}
                value={value}
                onChange={setValue}
            />
        );
    },
};

export const Empty: Story = {
    args: {
        patients: [],
    },
};
