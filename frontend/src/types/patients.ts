export interface Patient {
    id: string;
    first_name: string;
    last_name: string;
    birthday: string;
    is_primary: boolean;
    is_active: boolean;
}

export interface PatientWrite {
    first_name: string;
    last_name: string;
    birthday: string;
}
