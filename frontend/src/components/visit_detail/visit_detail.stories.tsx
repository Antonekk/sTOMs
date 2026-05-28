import type { Meta, StoryObj } from "@storybook/react-vite";
import VisitDetailCard from "./visit_detail";
import type { OfficeLocation, VisitDetail } from "../../types/reservations";

const meta: Meta<typeof VisitDetailCard> = {
    title: "Components/VisitDetail",
    component: VisitDetailCard,
    tags: ["autodocs"],
    argTypes: {
        onNotesChange: { action: "notesChange" },
        onSaveNote: { action: "saveNote" },
        onComplete: { action: "complete" },
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

const mockVisit: VisitDetail = {
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
    notes: "Pacjent wykazał wyraźną poprawę.",
};

export const ClientView: Story = {
    args: {
        visit: mockVisit,
        role: "CLIENT",
        canCancel: true,
        onCancel: () => {
            console.log("Cancel visit");
        },
    },
};

export const TherapistView: Story = {
    args: {
        visit: mockVisit,
        role: "THERAPIST",
        notes: mockVisit.notes ?? "",
        canCancel: true,
        canUpdateStatus: true,
        onNotesChange: (value) => {
            console.log("Notes changed:", value);
        },
        onSaveNote: () => {
            console.log("Save note");
        },
        onComplete: () => {
            console.log("Complete visit");
        },
        onCancel: () => {
            console.log("Cancel visit");
        },
    },
};

export const Completed: Story = {
    args: {
        visit: {
            ...mockVisit,
            status: "COMPLETED",
        },
        role: "THERAPIST",
        notes: mockVisit.notes ?? "",
        onSaveNote: () => {
            console.log("Save note");
        },
    },
};

export const Canceled: Story = {
    args: {
        visit: {
            ...mockVisit,
            status: "CANCELED",
        },
        role: "CLIENT",
    },
};
