import type { Meta, StoryObj } from "@storybook/react-vite";
import VisitList from "./visit_list";
import type { OfficeLocation, Visit } from "../../types/reservations";

const meta: Meta<typeof VisitList> = {
    title: "Components/VisitList",
    component: VisitList,
    tags: ["autodocs"],
    argTypes: {
        onOpen: { action: "open" },
        onCancel: { action: "cancel" },
    },
};

export default meta;

type Story = StoryObj<typeof meta>;

const mockOffice: OfficeLocation = {
    name: "Centrum Terapii",
    city: "Warszawa",
    address: "ul. Przykładowa 1",
    postal_code: "00-001",
    room_number: "12",
};

const mockVisits: Visit[] = [
    {
        id: "visit-1",
        appointment_date: "2026-06-10",
        start_time: "09:00:00",
        end_time: "10:00:00",
        status: "SCHEDULED",
        final_price: "150.00",
        patient_name: "Anna Kowalska",
        therapist_name: "Maria Nowak",
        appointment_type_name: "Terapia indywidualna",
        office: mockOffice,
    },
    {
        id: "visit-2",
        appointment_date: "2026-06-03",
        start_time: "14:00:00",
        end_time: "15:00:00",
        status: "COMPLETED",
        final_price: "150.00",
        patient_name: "Jan Kowalski",
        therapist_name: "Maria Nowak",
        appointment_type_name: "Terapia indywidualna",
        office: mockOffice,
        notes: "Pacjent wykazał wyraźną poprawę.",
    },
    {
        id: "visit-3",
        appointment_date: "2026-05-20",
        start_time: "11:00:00",
        end_time: "12:00:00",
        status: "CANCELED",
        final_price: "150.00",
        patient_name: "Anna Kowalska",
        therapist_name: "Piotr Wiśniewski",
        appointment_type_name: "Konsultacja",
        office: mockOffice,
    },
];

export const Default: Story = {
    args: {
        visits: mockVisits,
        onOpen: (id) => {
            console.log("Open visit:", id);
        },
        onCancel: (id) => {
            console.log("Cancel visit:", id);
        },
    },
};

export const WithNotes: Story = {
    args: {
        visits: mockVisits,
        showNotes: true,
        onOpen: (id) => {
            console.log("Open visit:", id);
        },
    },
};

export const Empty: Story = {
    args: {
        visits: [],
    },
};

export const Loading: Story = {
    args: {
        visits: [],
        loading: true,
    },
};

export const Canceling: Story = {
    args: {
        visits: mockVisits,
        cancelingId: "visit-1",
        onOpen: (id) => {
            console.log("Open visit:", id);
        },
        onCancel: (id) => {
            console.log("Cancel visit:", id);
        },
    },
};
