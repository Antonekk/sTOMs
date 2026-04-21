import api from "./api"
import { VISIT_ENDPOINTS } from "./endpoints"
import type { Visit, VisitDetail, VisitStatus } from "../types/reservations"

export interface VisitListParams {
    include_canceled?: boolean
    status?: VisitStatus
    therapist_id?: string
}

export const listVisits = (params?: VisitListParams) =>
    api.get<Visit[]>(VISIT_ENDPOINTS.VISITS, { params })

export const getVisit = (id: string) =>
    api.get<VisitDetail>(VISIT_ENDPOINTS.VISIT(id))

export const cancelVisit = (id: string) =>
    api.patch<Visit>(VISIT_ENDPOINTS.CANCEL(id), {})

export const updateVisitStatus = (id: string, status: VisitStatus) =>
    api.patch<Visit>(VISIT_ENDPOINTS.STATUS(id), { status })

export const updateVisitNote = (id: string, notes: string) =>
    api.patch<Visit>(VISIT_ENDPOINTS.NOTE(id), { notes })
