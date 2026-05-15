export type SeriesStatus = "ACTIVE" | "ENDED" | "CANCELED";
export type VisitStatus = "SCHEDULED" | "COMPLETED" | "CANCELED";

export interface AppointmentType {
    id: string;
    name: string;
    duration_time_minutes: number;
    price: string;
    is_periodic: boolean;
}

export interface AppointmentSummary {
    id: string;
    appointment_date: string;
    status: VisitStatus;
    final_price: string;
}

export interface ReservationSeries {
    id: string;
    status: SeriesStatus;
    therapist_name: string;
    patient_name: string;
    appointment_type_name: string;
    start_time: string;
    end_time: string;
    start_date: string;
    recurrence_display: string | null;
}

export interface ReservationSeriesDetail extends ReservationSeries {
    appointments: AppointmentSummary[];
}

export interface ReservationCreatePayload {
    therapist_id: string;
    patient_id: string;
    appointment_type_id: string;
    start_time: string;
    start_date: string;
    is_weekly: boolean;
}

export interface Visit {
    id: string;
    appointment_date: string;
    status: VisitStatus;
    final_price: string;
    therapist_name: string;
    patient_name: string;
    appointment_type_name: string;
    start_time: string;
    end_time: string;
    notes?: string | null;
}

export interface VisitDetail extends Visit {
    patient_first_name?: string;
    patient_last_name?: string;
    therapist_first_name?: string;
    therapist_last_name?: string;
}

export interface AvailabilitySlot {
    start_time: string;
    end_time: string;
}

export interface OfficeLocation {
    name: string;
    city: string;
    address: string;
    postal_code: string;
    room_number: string | null;
}

export interface AvailabilityDay {
    therapist_id: string;
    therapist_name: string;
    office_id: string | null;
    localization: string | null;
    date: string;
    slots: AvailabilitySlot[];
}

export interface BookableSlot {
    therapist_id: string;
    therapist_name: string;
    office_id: string | null;
    office: OfficeLocation | null;
    date: string;
    start_time: string;
    end_time: string;
}

export interface BookingTherapist {
    id: string;
    full_name: string;
    office_id: string | null;
    office: OfficeLocation | null;
}

export interface PaginatedBookableSlots {
    count: number;
    next: string | null;
    previous: string | null;
    results: BookableSlot[];
}

export interface BookableTimeOptions {
    start_times: string[];
    end_times: string[];
}

export interface BookableSlotSearchParams {
    appointment_type_id: string;
    date_from?: string;
    date_to?: string;
    therapist_id?: string;
    office_id?: string;
    day_of_week?: number;
    time_from?: string;
    time_to?: string;
    page?: number;
    page_size?: number;
}
