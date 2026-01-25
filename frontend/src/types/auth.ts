export type Role = "CLIENT" | "THERAPIST"

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



export interface User{
    id: string
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    role: Role;
}

export interface TimeBlock {
    start_time: string;
    end_time: string;
}

export type DayOfWeek = "0" | "1" | "2" | "3" | "4" | "5" | "6";

export type WeeklyScheduleResponse = Partial<Record<DayOfWeek, TimeBlock[]>>;

export interface WeeklyScheduleRequest {
    weekly_schedule: Partial<Record<DayOfWeek, TimeBlock[]>>;
}

export type AvailabilityType = "INCLUSION" | "EXCLUSION";

export interface ScheduleOverrideResponse {
    id: string;
    therapist: string;
    specific_date: string;
    start_time: string;
    end_time: string;
    availability_type: AvailabilityType;
}

export interface ScheduleOverrideRequest {
    specific_date: string;
    start_time: string;
    end_time: string;
    availability_type: AvailabilityType;
}
