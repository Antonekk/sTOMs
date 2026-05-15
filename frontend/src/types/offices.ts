export interface Office {
    id: string;
    room_number: string;
}

export interface Localization {
    id: string;
    name: string;
    city: string;
    postal_code: string;
    address: string;
    offices: Office[];
}
