import api from "./api"
import { RESERVATION_ENDPOINTS } from "./endpoints"
import type {
    BookableSlotSearchParams,
    BookableTimeOptions,
    BookingTherapist,
    PaginatedBookableSlots,
    ReservationCreatePayload,
    ReservationSeries,
    ReservationSeriesDetail,
    SeriesStatus,
} from "../types/reservations"

export const listBookingTherapists = () =>
    api.get<BookingTherapist[]>(RESERVATION_ENDPOINTS.THERAPISTS)

export const searchBookableSlots = (params: BookableSlotSearchParams) =>
    api.get<PaginatedBookableSlots>(RESERVATION_ENDPOINTS.BOOKABLE_SLOTS, { params })

export const getBookableTimeOptions = (
    params: Omit<BookableSlotSearchParams, "time_from" | "time_to" | "page" | "page_size">,
) =>
    api.get<BookableTimeOptions>(
        RESERVATION_ENDPOINTS.BOOKABLE_SLOT_TIME_OPTIONS,
        { params },
    )

export const listReservations = (status?: SeriesStatus) =>
    api.get<ReservationSeries[]>(RESERVATION_ENDPOINTS.RESERVATIONS, {
        params: status ? { status } : undefined,
    })

export const getReservation = (id: string) =>
    api.get<ReservationSeriesDetail>(RESERVATION_ENDPOINTS.RESERVATION(id))

export const createReservation = (data: ReservationCreatePayload) =>
    api.post<ReservationSeriesDetail>(RESERVATION_ENDPOINTS.RESERVATIONS, data)

export const cancelReservation = (id: string) =>
    api.patch<ReservationSeriesDetail>(RESERVATION_ENDPOINTS.RESERVATION(id), {
        status: "CANCELED",
    })
