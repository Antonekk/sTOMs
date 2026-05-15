import type { OfficeLocation } from "../types/reservations"

export const formatOfficeAddress = (office: OfficeLocation): string =>
    `${office.address}, ${office.postal_code} ${office.city}`

export const formatOfficeLocation = (
    office: OfficeLocation | null | undefined,
): string | null => {
    if (!office) return null

    const parts = [office.name, formatOfficeAddress(office)]
    if (office.room_number) {
        parts.push(`pokój ${office.room_number}`)
    }
    return parts.join(" · ")
}

export const formatOfficeLocationShort = (
    office: OfficeLocation | null | undefined,
): string | null => {
    if (!office) return null

    const parts = [office.city, office.address]
    if (office.room_number) {
        parts.push(`pok. ${office.room_number}`)
    }
    return parts.join(", ")
}
