import type { Patient } from "./patients";

export type { Patient } from "./patients";
export type Role = "ADMIN" | "CLIENT" | "THERAPIST"

export interface LoginData{
    email: string;
    password: string;
}


export interface LoginResponse{
    refresh: string;
    access: string;
}

export interface RefreshTokenData{
    refresh: string
}

export interface RefreshTokenResponse {
    access: string;
}

export interface RegisterData{
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    date_of_birth: string;
    password: string;
    re_password: string;
}

export interface ActivateData{
    uid?: string;
    token?: string;
}

export interface PasswordResetRequestData {
    email: string;
}

export interface PasswordResetConfirmData {
    uid: string;
    token: string;
    new_password: string;
    re_new_password: string;
}



export interface User{
    id: string
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    role: Role;
    patients: Patient[];
}

export interface AppConfig {
    appointment_generation_days: number;
    appointment_booking_days: number;
    cancellation_window_hours: number;
}
