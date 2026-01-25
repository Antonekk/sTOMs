import api from "./api"
import { AUTH_ENDPOINTS } from "./endpoints"
import type { LoginData, LoginResponse, RegisterData, RefreshTokenData, RefreshTokenResponse ,ActivateData, User, WeeklyScheduleResponse, WeeklyScheduleRequest, ScheduleOverrideResponse, ScheduleOverrideRequest } from "../types/auth"


export const register = (data: RegisterData) => api.post(AUTH_ENDPOINTS.REGISTER, data)

export const login = (data: LoginData) => api.post<LoginResponse>(AUTH_ENDPOINTS.LOGIN, data)

export const tokenRefresh = (data: RefreshTokenData) => api.post<RefreshTokenResponse>(AUTH_ENDPOINTS.REFRESH, data )

export const activate = (data: ActivateData) => api.post(AUTH_ENDPOINTS.ACTIVATE, data)

export const getMe = () => api.get<User>(AUTH_ENDPOINTS.ME);

export const getWeeklySchedule = () => api.get<WeeklyScheduleResponse>(AUTH_ENDPOINTS.WEEKLY_SCHEDULE);

export const saveWeeklySchedule = (data: WeeklyScheduleRequest) => api.post(AUTH_ENDPOINTS.WEEKLY_SCHEDULE, data);

export const getScheduleOverrides = () => api.get<ScheduleOverrideResponse[]>(AUTH_ENDPOINTS.SCHEDULE_OVERRIDE);

export const createScheduleOverride = (data: ScheduleOverrideRequest) => api.post<ScheduleOverrideResponse>(AUTH_ENDPOINTS.SCHEDULE_OVERRIDE, data);

export const deleteScheduleOverride = (id: string) => api.delete(`${AUTH_ENDPOINTS.SCHEDULE_OVERRIDE}${id}/`);

