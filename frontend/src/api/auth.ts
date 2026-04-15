import api from "./api"
import { AUTH_ENDPOINTS } from "./endpoints"
import type { LoginData, LoginResponse, RegisterData, RefreshTokenData, RefreshTokenResponse ,ActivateData, User, AppConfig } from "../types/auth"


export const register = (data: RegisterData) => api.post(AUTH_ENDPOINTS.REGISTER, data)

export const login = (data: LoginData) => api.post<LoginResponse>(AUTH_ENDPOINTS.LOGIN, data)

export const tokenRefresh = (data: RefreshTokenData) => api.post<RefreshTokenResponse>(AUTH_ENDPOINTS.REFRESH, data )

export const activate = (data: ActivateData) => api.post(AUTH_ENDPOINTS.ACTIVATE, data)

export const getMe = () => api.get<User>(AUTH_ENDPOINTS.ME);

export const getConfig = () => api.get<AppConfig>(AUTH_ENDPOINTS.CONFIG);

