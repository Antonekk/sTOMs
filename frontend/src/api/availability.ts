import api from "./api"
import { AVAILABILITY_ENDPOINT } from "./endpoints"
import type { AvailabilityDay } from "../types/reservations"

export interface AvailabilityQuery {
    date_from: string
    date_to: string
    therapist_id?: string
    office_id?: string
    day_of_week?: number
}

export const getAvailability = (params: AvailabilityQuery) =>
    api.get<AvailabilityDay[]>(AVAILABILITY_ENDPOINT, { params })
