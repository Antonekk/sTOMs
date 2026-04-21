import api from "./api"
import { RESERVATION_ENDPOINTS } from "./endpoints"
import type {
    ReservationCreatePayload,
    ReservationSeries,
    ReservationSeriesDetail,
    SeriesStatus,
} from "../types/reservations"

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
