import type { Meta, StoryObj } from "@storybook/react-vite";
import PatientForm from "./patient_form";

const meta: Meta<typeof PatientForm> = {
    title: "Components/PatientForm",
    component: PatientForm,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const NewPatient: Story = {
    args: {
        submitLabel: "Dodaj pacjenta",
        onSubmit: () => undefined,
    },
};

export const EditPatient: Story = {
    args: {
        submitLabel: "Zapisz zmiany",
        initialValues: {
            first_name: "Jan",
            last_name: "Kowalski",
            birthday: "2016-03-11",
        },
        onSubmit: () => undefined,
    },
};
