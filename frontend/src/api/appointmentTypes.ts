import api from "./api"
import { RESERVATION_ENDPOINTS } from "./endpoints"
import type { AppointmentType } from "../types/reservations"

export const listAppointmentTypes = () =>
    api.get<AppointmentType[]>(RESERVATION_ENDPOINTS.APPOINTMENT_TYPES)
