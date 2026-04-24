import type { AvailabilityDay, AppointmentType, BookableSlot } from "../types/reservations"

const timeToMinutes = (time: string): number => {
    const [hours, minutes] = time.slice(0, 5).split(":").map(Number)
    return hours * 60 + minutes
}

const minutesToTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${String(hours).padStart(2, "0")}:${String(mins).padStart(2, "0")}`
}

export const splitAvailabilityIntoBookableSlots = (
    days: AvailabilityDay[],
    appointmentType: AppointmentType,
): BookableSlot[] => {
    const duration = appointmentType.duration_time_minutes
    const bookable: BookableSlot[] = []

    for (const day of days) {
        for (const slot of day.slots) {
            let cursor = timeToMinutes(slot.start_time)
            const slotEnd = timeToMinutes(slot.end_time)

            while (cursor + duration <= slotEnd) {
                bookable.push({
                    therapist_id: day.therapist_id,
                    therapist_name: day.therapist_name,
                    office_id: day.office_id,
                    localization: day.localization,
                    date: day.date,
                    start_time: minutesToTime(cursor),
                    end_time: minutesToTime(cursor + duration),
                })
                cursor += duration
            }
        }
    }

    return bookable.sort((a, b) => {
        if (a.date !== b.date) return a.date.localeCompare(b.date)
        return a.start_time.localeCompare(b.start_time)
    })
}

export const formatDatePl = (isoDate: string): string => {
    const date = new Date(`${isoDate}T12:00:00`)
    return date.toLocaleDateString("pl-PL", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
    })
}

export const formatTime = (time: string): string => time.slice(0, 5)

export const formatDateTimePl = (isoDateTime: string): string =>
    new Date(isoDateTime).toLocaleString("pl-PL", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    })

export const isUpcomingVisit = (appointmentDate: string): boolean => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const visitDate = new Date(`${appointmentDate}T12:00:00`)
    return visitDate >= today
}

export const canCancelByWindow = (
    appointmentDate: string,
    startTime: string,
    cancellationWindowHours: number,
): boolean => {
    const [hours, minutes] = startTime.slice(0, 5).split(":").map(Number)
    const start = new Date(`${appointmentDate}T12:00:00`)
    start.setHours(hours, minutes, 0, 0)
    const deadline = start.getTime() - cancellationWindowHours * 60 * 60 * 1000
    return Date.now() < deadline
}
