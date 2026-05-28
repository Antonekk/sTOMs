import type { Meta, StoryObj } from "@storybook/react-vite";
import ReservationList from "./reservation_list";
import type { OfficeLocation, ReservationSeries } from "../../types/reservations";

const meta: Meta<typeof ReservationList> = {
    title: "Components/ReservationList",
    component: ReservationList,
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

const mockReservations: ReservationSeries[] = [
    {
        id: "series-1",
        status: "ACTIVE",
        patient_name: "Anna Kowalska",
        therapist_name: "Maria Nowak",
        appointment_type_name: "Terapia indywidualna",
        start_date: "2026-06-10",
        start_time: "09:00:00",
        end_time: "10:00:00",
        recurrence_display: "Co tydzień, poniedziałek",
        office: mockOffice,
    },
    {
        id: "series-2",
        status: "ENDED",
        patient_name: "Jan Kowalski",
        therapist_name: "Piotr Wiśniewski",
        appointment_type_name: "Konsultacja",
        start_date: "2026-03-15",
        start_time: "14:00:00",
        end_time: "15:00:00",
        recurrence_display: null,
        office: mockOffice,
    },
    {
        id: "series-3",
        status: "CANCELED",
        patient_name: "Anna Kowalska",
        therapist_name: "Maria Nowak",
        appointment_type_name: "Terapia indywidualna",
        start_date: "2026-05-01",
        start_time: "11:00:00",
        end_time: "12:00:00",
        recurrence_display: "Co tydzień, czwartek",
        office: mockOffice,
    },
];

export const Default: Story = {
    args: {
        reservations: mockReservations,
        onOpen: (id) => {
            console.log("Open reservation:", id);
        },
        onCancel: (id) => {
            console.log("Cancel reservation:", id);
        },
    },
};

export const Empty: Story = {
    args: {
        reservations: [],
    },
};

export const Loading: Story = {
    args: {
        reservations: [],
        loading: true,
    },
};

export const Canceling: Story = {
    args: {
        reservations: mockReservations,
        cancelingId: "series-1",
        onOpen: (id) => {
            console.log("Open reservation:", id);
        },
        onCancel: (id) => {
            console.log("Cancel reservation:", id);
        },
    },
};
