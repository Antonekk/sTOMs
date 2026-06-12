import { Flex, Typography, message } from "antd"
import type { ApiErrorDisplay } from "../utils/apiError"
import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { listAppointmentTypes } from "../api/appointmentTypes"
import {
    createReservation,
    getBookableTimeOptions,
    listBookingTherapists,
    searchBookableSlots,
} from "../api/reservations"
import ReservationBooking, {
    slotKey,
} from "../components/reservation_booking/reservation_booking"
import { useAuthentication } from "../auth/AuthProvider"
import { useAppConfig } from "../config/ConfigProvider"
import { getApiErrorDisplay } from "../utils/apiError"
import { formatOfficeLocation } from "../utils/officeDisplay"
import type {
    LocationFilterMode,
    OfficeOption,
} from "../components/reservation_booking/reservation_booking"
import type {
    AppointmentType,
    BookableSlot,
    BookableTimeOptions,
    BookingTherapist,
} from "../types/reservations"

const { Title } = Typography

const SLOTS_PAGE_SIZE = 10
const EMPTY_TIME_OPTIONS: BookableTimeOptions = { start_times: [], end_times: [] }

const formatIsoDate = (date: Date): string => date.toISOString().slice(0, 10)

const ReservationNew: React.FC = () => {
    const navigate = useNavigate()
    const { user } = useAuthentication()
    const { config } = useAppConfig()

    const [appointmentTypes, setAppointmentTypes] = useState<AppointmentType[]>([])
    const [therapists, setTherapists] = useState<BookingTherapist[]>([])
    const [bookableSlots, setBookableSlots] = useState<BookableSlot[]>([])
    const [timeOptions, setTimeOptions] = useState<BookableTimeOptions>(EMPTY_TIME_OPTIONS)
    const [slotsTotal, setSlotsTotal] = useState(0)
    const [slotsPage, setSlotsPage] = useState(1)
    const [loadingSlots, setLoadingSlots] = useState(false)
    const [loadingTimeOptions, setLoadingTimeOptions] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [error, setError] = useState<ApiErrorDisplay | null>(null)

    const [patientId, setPatientId] = useState<string>()
    const [appointmentTypeId, setAppointmentTypeId] = useState<string>()
    const [bookingMode, setBookingMode] = useState<"once" | "weekly">("once")
    const [visitDate, setVisitDate] = useState<string>()
    const [dayOfWeek, setDayOfWeek] = useState<number>()
    const [startDate, setStartDate] = useState<string>()
    const [locationFilterMode, setLocationFilterMode] =
        useState<LocationFilterMode>("therapist")
    const [therapistId, setTherapistId] = useState<string>()
    const [officeId, setOfficeId] = useState<string>()
    const [timeFrom, setTimeFrom] = useState<string>()
    const [timeTo, setTimeTo] = useState<string>()
    const [selectedSlot, setSelectedSlot] = useState<BookableSlot>()
    const [hasSearched, setHasSearched] = useState(false)

    const patients = useMemo(
        () => (user?.patients ?? []).filter((patient) => patient.is_active),
        [user?.patients],
    )

    const maxBookingDate = useMemo(() => {
        if (!config) return undefined
        const date = new Date()
        date.setDate(date.getDate() + config.appointment_booking_days)
        return formatIsoDate(date)
    }, [config])

    const selectedType = appointmentTypes.find((type) => type.id === appointmentTypeId)

    const officeOptions = useMemo<OfficeOption[]>(() => {
        const seen = new Set<string>()
        return therapists
            .filter((therapist) => therapist.office_id && therapist.office)
            .filter((therapist) => {
                if (!therapist.office_id || seen.has(therapist.office_id)) {
                    return false
                }
                seen.add(therapist.office_id)
                return true
            })
            .map((therapist) => ({
                value: therapist.office_id!,
                label:
                    formatOfficeLocation(therapist.office!) ?? therapist.office!.name,
            }))
    }, [therapists])

    const dateSearchParams = useMemo(() => {
        if (bookingMode === "once") {
            if (!visitDate) return null
            return {
                date_from: visitDate,
                date_to: visitDate,
            }
        }
        if (dayOfWeek === undefined || !startDate || !maxBookingDate) return null
        return {
            date_from: startDate,
            date_to: maxBookingDate,
            day_of_week: dayOfWeek,
        }
    }, [bookingMode, visitDate, dayOfWeek, startDate, maxBookingDate])

    useEffect(() => {
        const loadInitialData = async () => {
            try {
                const [typesResponse, therapistsResponse] = await Promise.all([
                    listAppointmentTypes(),
                    listBookingTherapists(),
                ])
                setAppointmentTypes(typesResponse.data)
                setTherapists(therapistsResponse.data)
            } catch (err) {
                setError(
                    getApiErrorDisplay(err, {
                        fallback: "Nie udało się wczytać danych rezerwacji. Odśwież stronę lub skontaktuj się z administratorem.",
                        title: "Błąd konfiguracji",
                    }),
                )
            }
        }
        void loadInitialData()
    }, [])

    useEffect(() => {
        if (!patientId && patients.length > 0) {
            const primary = patients.find((patient) => patient.is_primary) ?? patients[0]
            setPatientId(primary.id)
        }
    }, [patients, patientId])

    useEffect(() => {
        if (selectedType && !selectedType.is_periodic && bookingMode === "weekly") {
            setBookingMode("once")
        }
    }, [selectedType, bookingMode])

    const resetSlotSearch = useCallback(() => {
        setBookableSlots([])
        setSlotsTotal(0)
        setSelectedSlot(undefined)
        setHasSearched(false)
    }, [])

    const handleBookingModeChange = useCallback(
        (mode: "once" | "weekly") => {
            setBookingMode(mode)
            setVisitDate(undefined)
            setDayOfWeek(undefined)
            setStartDate(undefined)
            setTimeFrom(undefined)
            setTimeTo(undefined)
            setTimeOptions(EMPTY_TIME_OPTIONS)
            resetSlotSearch()
        },
        [resetSlotSearch],
    )

    const handleDayOfWeekChange = useCallback((day: number | undefined) => {
        setDayOfWeek(day)
        setStartDate(undefined)
        setTimeFrom(undefined)
        setTimeTo(undefined)
        setTimeOptions(EMPTY_TIME_OPTIONS)
        resetSlotSearch()
    }, [resetSlotSearch])

    const handleVisitDateChange = useCallback(
        (value: string | undefined) => {
            setVisitDate(value)
            setTimeFrom(undefined)
            setTimeTo(undefined)
            resetSlotSearch()
        },
        [resetSlotSearch],
    )

    const handleStartDateChange = useCallback(
        (value: string | undefined) => {
            setStartDate(value)
            setTimeFrom(undefined)
            setTimeTo(undefined)
            resetSlotSearch()
        },
        [resetSlotSearch],
    )

    const handleLocationFilterModeChange = useCallback(
        (mode: LocationFilterMode) => {
            setLocationFilterMode(mode)
            setTherapistId(undefined)
            setOfficeId(undefined)
            resetSlotSearch()
        },
        [resetSlotSearch],
    )

    const handleTherapistChange = useCallback(
        (value: string | undefined) => {
            const therapist = therapists.find((item) => item.id === value)
            setTherapistId(value)
            setOfficeId(therapist?.office_id ?? undefined)
            resetSlotSearch()
        },
        [therapists, resetSlotSearch],
    )

    const handleOfficeChange = useCallback(
        (value: string | undefined) => {
            const therapist = therapists.find((item) => item.office_id === value)
            setOfficeId(value)
            setTherapistId(therapist?.id ?? undefined)
            resetSlotSearch()
        },
        [therapists, resetSlotSearch],
    )

    const handleTimeFromChange = useCallback(
        (value: string | undefined) => {
            setTimeFrom(value)
            setTimeTo((current) =>
                current && value && current <= value ? undefined : current,
            )
            resetSlotSearch()
        },
        [resetSlotSearch],
    )

    const handleTimeToChange = useCallback(
        (value: string | undefined) => {
            setTimeTo(value)
            resetSlotSearch()
        },
        [resetSlotSearch],
    )

    const loadTimeOptions = useCallback(async () => {
        if (!selectedType || !dateSearchParams) {
            setTimeOptions(EMPTY_TIME_OPTIONS)
            return
        }

        setLoadingTimeOptions(true)
        try {
            const response = await getBookableTimeOptions({
                appointment_type_id: selectedType.id,
                ...dateSearchParams,
                therapist_id: therapistId,
                office_id: officeId,
            })
            setTimeOptions(response.data)
            setTimeFrom((current) =>
                current && response.data.start_times.includes(current)
                    ? current
                    : undefined,
            )
            setTimeTo((current) =>
                current && response.data.end_times.includes(current)
                    ? current
                    : undefined,
            )
        } catch (err) {
            setTimeOptions(EMPTY_TIME_OPTIONS)
            setError(
                getApiErrorDisplay(err, {
                    fallback: "Nie udało się pobrać dostępnych godzin. Sprawdź filtry i spróbuj ponownie.",
                    context: "availability",
                }),
            )
        } finally {
            setLoadingTimeOptions(false)
        }
    }, [selectedType, dateSearchParams, therapistId, officeId])

    useEffect(() => {
        void loadTimeOptions()
    }, [loadTimeOptions])

    const fetchSlots = useCallback(
        async (page: number) => {
            if (!selectedType || !dateSearchParams) return

            setLoadingSlots(true)
            setError(null)

            try {
                const response = await searchBookableSlots({
                    appointment_type_id: selectedType.id,
                    ...dateSearchParams,
                    therapist_id: therapistId,
                    office_id: officeId,
                    time_from: timeFrom,
                    time_to: timeTo,
                    page,
                    page_size: SLOTS_PAGE_SIZE,
                })
                setBookableSlots(response.data.results)
                setSlotsTotal(response.data.count)
                setSlotsPage(page)
            } catch (err) {
                setBookableSlots([])
                setSlotsTotal(0)
                setError(
                    getApiErrorDisplay(err, {
                        fallback: "Nie udało się pobrać wolnych terminów. Sprawdź filtry i spróbuj ponownie.",
                        context: "availability",
                    }),
                )
            } finally {
                setLoadingSlots(false)
            }
        },
        [selectedType, dateSearchParams, therapistId, officeId, timeFrom, timeTo],
    )

    const handleSearchSlots = useCallback(() => {
        setSelectedSlot(undefined)
        setHasSearched(true)
        void fetchSlots(1)
    }, [fetchSlots])

    const handlePageChange = useCallback(
        (page: number) => {
            void fetchSlots(page)
        },
        [fetchSlots],
    )

    const handleSlotSelect = useCallback(
        (slotKeyValue: string) => {
            const slot = bookableSlots.find((item) => slotKey(item) === slotKeyValue)
            setSelectedSlot(slot)
        },
        [bookableSlots],
    )

    const handleSubmit = async () => {
        if (!patientId || !selectedType || !selectedSlot) return

        setSubmitting(true)
        setError(null)

        try {
            const response = await createReservation({
                therapist_id: selectedSlot.therapist_id,
                patient_id: patientId,
                appointment_type_id: selectedType.id,
                start_time: selectedSlot.start_time,
                start_date: selectedSlot.date,
                is_weekly: bookingMode === "weekly",
            })
            void message.success("Rezerwacja została utworzona.")
            void navigate(`/rezerwacje/${response.data.id}`)
        } catch (err) {
            const display = getApiErrorDisplay(err, {
                fallback: "Nie udało się utworzyć rezerwacji. Wybierz inny termin lub spróbuj ponownie.",
                context: "booking",
            })
            setError(display)
            void message.error(display.description)
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
            <Title level={2}>Nowa rezerwacja</Title>
            <ReservationBooking
                patients={patients}
                appointmentTypes={appointmentTypes}
                therapists={therapists}
                officeOptions={officeOptions}
                bookableSlots={bookableSlots}
                timeOptions={timeOptions}
                slotsTotal={slotsTotal}
                slotsPage={slotsPage}
                slotsPageSize={SLOTS_PAGE_SIZE}
                maxBookingDate={maxBookingDate}
                hasSearched={hasSearched}
                loadingSlots={loadingSlots}
                loadingTimeOptions={loadingTimeOptions}
                submitting={submitting}
                error={error}
                patientId={patientId}
                appointmentTypeId={appointmentTypeId}
                bookingMode={bookingMode}
                visitDate={visitDate}
                dayOfWeek={dayOfWeek}
                startDate={startDate}
                locationFilterMode={locationFilterMode}
                therapistId={therapistId}
                officeId={officeId}
                timeFrom={timeFrom}
                timeTo={timeTo}
                selectedSlotKey={selectedSlot ? slotKey(selectedSlot) : undefined}
                onPatientChange={setPatientId}
                onAppointmentTypeChange={setAppointmentTypeId}
                onBookingModeChange={handleBookingModeChange}
                onVisitDateChange={handleVisitDateChange}
                onDayOfWeekChange={handleDayOfWeekChange}
                onStartDateChange={handleStartDateChange}
                onLocationFilterModeChange={handleLocationFilterModeChange}
                onTherapistChange={handleTherapistChange}
                onOfficeChange={handleOfficeChange}
                onTimeFromChange={handleTimeFromChange}
                onTimeToChange={handleTimeToChange}
                onSlotSelect={handleSlotSelect}
                onSearchSlots={handleSearchSlots}
                onSlotsPageChange={handlePageChange}
                onSubmit={() => { void handleSubmit(); }}
            />
        </Flex>
    )
}

export default ReservationNew
