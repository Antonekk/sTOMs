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
    uid: string;
    token: string;
}



export interface User{
    id: string
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    role: Role;
}