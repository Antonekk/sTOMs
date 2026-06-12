export const timeToMinutes = (time: string): number => {
    const [hours, minutes] = time.slice(0, 5).split(":").map(Number)
    return hours * 60 + minutes
}

export const timeRangesOverlap = (
    aStart: string,
    aEnd: string,
    bStart: string,
    bEnd: string,
): boolean => {
    const aStartMinutes = timeToMinutes(aStart)
    const aEndMinutes = timeToMinutes(aEnd)
    const bStartMinutes = timeToMinutes(bStart)
    const bEndMinutes = timeToMinutes(bEnd)
    return aStartMinutes < bEndMinutes && aEndMinutes > bStartMinutes
}

export const djangoWeekdayFromDate = (isoDate: string): number => {
    const jsDay = new Date(`${isoDate}T12:00:00`).getDay()
    return (jsDay + 6) % 7
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

export const isPastVisit = (appointmentDate: string, endTime: string): boolean => {
    const [hours, minutes] = endTime.slice(0, 5).split(":").map(Number)
    const end = new Date(`${appointmentDate}T12:00:00`)
    end.setHours(hours, minutes, 0, 0)
    return Date.now() > end.getTime()
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
