import api from "./api"
import { THERAPIST_AVAILABILITY_ENDPOINTS } from "./endpoints"
import type {
    BaseScheduleRequest,
    BaseScheduleResponse,
    ScheduleOverrideRequest,
    ScheduleOverrideResponse,
} from "../types/therapistAvailability"

export const getWeeklySchedule = () =>
    api.get<BaseScheduleResponse>(THERAPIST_AVAILABILITY_ENDPOINTS.SELF_SCHEDULE)

export const saveWeeklySchedule = (data: BaseScheduleRequest) =>
    api.put(THERAPIST_AVAILABILITY_ENDPOINTS.SELF_SCHEDULE, data)

export const getScheduleOverrides = () =>
    api.get<ScheduleOverrideResponse[]>(THERAPIST_AVAILABILITY_ENDPOINTS.SELF_SCHEDULE_OVERRIDE)

export const createScheduleOverride = (data: ScheduleOverrideRequest) =>
    api.post<ScheduleOverrideResponse>(
        THERAPIST_AVAILABILITY_ENDPOINTS.SELF_SCHEDULE_OVERRIDE,
        data,
    )

export const deleteScheduleOverride = (id: string) =>
    api.delete(`${THERAPIST_AVAILABILITY_ENDPOINTS.SELF_SCHEDULE_OVERRIDE}/${id}`)
