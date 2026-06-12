import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import ReservationBooking from "./reservation_booking";
import type { Patient } from "../../types/patients";
import type {
    AppointmentType,
    BookableSlot,
    BookableTimeOptions,
    BookingTherapist,
    OfficeLocation,
} from "../../types/reservations";
import type { OfficeOption, ReservationBookingProps } from "./reservation_booking";

const meta: Meta<typeof ReservationBooking> = {
    title: "Components/ReservationBooking",
    component: ReservationBooking,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

const mockOffice1: OfficeLocation = {
    name: "Centrum Terapii",
    city: "Warszawa",
    address: "ul. Przykładowa 1",
    postal_code: "00-001",
    room_number: "12",
};

const mockOffice2: OfficeLocation = {
    name: "Gabinet Mokotów",
    city: "Warszawa",
    address: "ul. Przykładowa 10",
    postal_code: "00-002",
    room_number: "5",
};

const patients: Patient[] = [
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

const appointmentTypes: AppointmentType[] = [
    {
        id: "type-1",
        name: "Terapia indywidualna",
        duration_time_minutes: 60,
        price: "150.00",
        is_periodic: true,
    },
    {
        id: "type-2",
        name: "Konsultacja",
        duration_time_minutes: 45,
        price: "120.00",
        is_periodic: false,
    },
];

const therapists: BookingTherapist[] = [
    {
        id: "therapist-1",
        full_name: "Maria Nowak",
        office_id: "office-1",
        office: mockOffice1,
    },
    {
        id: "therapist-2",
        full_name: "Piotr Wiśniewski",
        office_id: "office-2",
        office: mockOffice2,
    },
];

const officeOptions: OfficeOption[] = [
    {
        value: "office-1",
        label: "Centrum Terapii · Warszawa, ul. Przykładowa 1 · pokój 12",
    },
    {
        value: "office-2",
        label: "Gabinet Mokotów · Warszawa, ul. Przykładowa 10 · pokój 5",
    },
];

const timeOptions: BookableTimeOptions = {
    start_times: ["09:00", "10:00", "11:00", "14:00", "15:00"],
    end_times: ["10:00", "11:00", "12:00", "15:00", "16:00", "17:00"],
};

const bookableSlots: BookableSlot[] = [
    {
        therapist_id: "therapist-1",
        therapist_name: "Maria Nowak",
        office_id: "office-1",
        office: mockOffice1,
        date: "2026-06-10",
        start_time: "09:00:00",
        end_time: "10:00:00",
    },
    {
        therapist_id: "therapist-2",
        therapist_name: "Piotr Wiśniewski",
        office_id: "office-2",
        office: mockOffice2,
        date: "2026-06-10",
        start_time: "14:00:00",
        end_time: "15:00:00",
    },
];

const noop = () => {};

const ReservationBookingWithState = (
    overrides: Partial<ReservationBookingProps> = {},
) => {
    const [patientId, setPatientId] = useState<string | undefined>(
        patients[0]?.id,
    );
    const [appointmentTypeId, setAppointmentTypeId] = useState<
        string | undefined
    >(overrides.appointmentTypeId);
    const [bookingMode, setBookingMode] = useState<"once" | "weekly">(
        overrides.bookingMode ?? "once",
    );
    const [visitDate, setVisitDate] = useState<string | undefined>(
        overrides.visitDate,
    );
    const [dayOfWeek, setDayOfWeek] = useState<number | undefined>(
        overrides.dayOfWeek,
    );
    const [startDate, setStartDate] = useState<string | undefined>(
        overrides.startDate,
    );
    const [locationFilterMode, setLocationFilterMode] = useState<
        "therapist" | "office"
    >(overrides.locationFilterMode ?? "therapist");
    const [therapistId, setTherapistId] = useState<string | undefined>(
        overrides.therapistId,
    );
    const [officeId, setOfficeId] = useState<string | undefined>(
        overrides.officeId,
    );
    const [timeFrom, setTimeFrom] = useState<string | undefined>(
        overrides.timeFrom,
    );
    const [timeTo, setTimeTo] = useState<string | undefined>(
        overrides.timeTo,
    );
    const [selectedSlotKey, setSelectedSlotKey] = useState<string | undefined>(
        overrides.selectedSlotKey,
    );

    return (
        <ReservationBooking
            patients={patients}
            appointmentTypes={appointmentTypes}
            therapists={therapists}
            officeOptions={officeOptions}
            bookableSlots={overrides.bookableSlots ?? []}
            timeOptions={overrides.timeOptions ?? timeOptions}
            slotsTotal={overrides.slotsTotal ?? 0}
            slotsPage={overrides.slotsPage ?? 1}
            slotsPageSize={overrides.slotsPageSize ?? 10}
            maxBookingDate={overrides.maxBookingDate ?? "2026-12-31"}
            hasSearched={overrides.hasSearched}
            loadingSlots={overrides.loadingSlots}
            loadingTimeOptions={overrides.loadingTimeOptions}
            submitting={overrides.submitting}
            error={overrides.error}
            patientId={patientId}
            appointmentTypeId={appointmentTypeId}
            bookingMode={bookingMode}
            visitDate={visitDate}
            dayOfWeek={dayOfWeek}
            startDate={startDate}
            locationFilterMode={locationFilterMode}
            therapistId={therapistId}
            officeId={officeId}
            timeFrom={timeFrom}
            timeTo={timeTo}
            selectedSlotKey={selectedSlotKey}
            onPatientChange={setPatientId}
            onAppointmentTypeChange={setAppointmentTypeId}
            onBookingModeChange={setBookingMode}
            onVisitDateChange={setVisitDate}
            onDayOfWeekChange={setDayOfWeek}
            onStartDateChange={setStartDate}
            onLocationFilterModeChange={setLocationFilterMode}
            onTherapistChange={(value) => {
                const therapist = therapists.find((item) => item.id === value);
                setTherapistId(value);
                setOfficeId(therapist?.office_id ?? undefined);
            }}
            onOfficeChange={(value) => {
                const therapist = therapists.find((item) => item.office_id === value);
                setOfficeId(value);
                setTherapistId(therapist?.id ?? undefined);
            }}
            onTimeFromChange={setTimeFrom}
            onTimeToChange={setTimeTo}
            onSlotSelect={setSelectedSlotKey}
            onSearchSlots={noop}
            onSlotsPageChange={noop}
            onSubmit={noop}
        />
    );
};

export const Initial: Story = {
    render: () => <ReservationBookingWithState />,
};

export const WithFilters: Story = {
    render: () => (
        <ReservationBookingWithState
            appointmentTypeId="type-1"
            visitDate="2026-06-10"
            therapistId="therapist-1"
            timeFrom="09:00"
            timeTo="12:00"
        />
    ),
};

export const WithSearchResults: Story = {
    render: () => (
        <ReservationBookingWithState
            appointmentTypeId="type-1"
            visitDate="2026-06-10"
            hasSearched
            bookableSlots={bookableSlots}
            slotsTotal={bookableSlots.length}
            selectedSlotKey="therapist-1|2026-06-10|09:00:00"
        />
    ),
};

export const WeeklyMode: Story = {
    render: () => (
        <ReservationBookingWithState
            appointmentTypeId="type-1"
            bookingMode="weekly"
            dayOfWeek={0}
            startDate="2026-06-09"
        />
    ),
};

export const WithError: Story = {
    render: () => (
        <ReservationBookingWithState
            appointmentTypeId="type-1"
            error={{
                title: "Nie udało się wyszukać terminów",
                description: "Spróbuj ponownie za chwilę lub zmień filtry.",
            }}
        />
    ),
};

export const LoadingSlots: Story = {
    render: () => (
        <ReservationBookingWithState
            appointmentTypeId="type-1"
            visitDate="2026-06-10"
            hasSearched
            loadingSlots
        />
    ),
};

export const Submitting: Story = {
    render: () => (
        <ReservationBookingWithState
            appointmentTypeId="type-1"
            visitDate="2026-06-10"
            hasSearched
            bookableSlots={bookableSlots}
            slotsTotal={bookableSlots.length}
            selectedSlotKey="therapist-1|2026-06-10|09:00:00"
            submitting
        />
    ),
};
