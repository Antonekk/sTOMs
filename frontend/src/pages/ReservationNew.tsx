import { Flex, Typography, message } from "antd"
import type { ApiErrorDisplay } from "../utils/apiError"
import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { listAppointmentTypes } from "../api/appointmentTypes"
import { getAvailability } from "../api/availability"
import { createReservation } from "../api/reservations"
import ReservationBooking, {
    slotKey,
} from "../components/storybook_components/reservation_booking/reservation_booking"
import { useAuthentication } from "../auth/AuthProvider"
import { useAppConfig } from "../config/ConfigProvider"
import { getApiErrorDisplay } from "../utils/apiError"
import { splitAvailabilityIntoBookableSlots } from "../utils/timeSlots"
import type { AppointmentType, BookableSlot } from "../types/reservations"

const { Title } = Typography

const formatIsoDate = (date: Date): string => date.toISOString().slice(0, 10)

const ReservationNew: React.FC = () => {
    const navigate = useNavigate()
    const { user } = useAuthentication()
    const { config } = useAppConfig()

    const [appointmentTypes, setAppointmentTypes] = useState<AppointmentType[]>([])
    const [bookableSlots, setBookableSlots] = useState<BookableSlot[]>([])
    const [loadingSlots, setLoadingSlots] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [error, setError] = useState<ApiErrorDisplay | null>(null)

    const [patientId, setPatientId] = useState<string>()
    const [appointmentTypeId, setAppointmentTypeId] = useState<string>()
    const [dayOfWeek, setDayOfWeek] = useState<number>()
    const [therapistId, setTherapistId] = useState<string>()
    const [selectedSlotKey, setSelectedSlotKey] = useState<string>()
    const [bookingMode, setBookingMode] = useState<"once" | "weekly">("once")

    const patients = useMemo(
        () => (user?.patients ?? []).filter((patient) => patient.is_active),
        [user?.patients],
    )

    useEffect(() => {
        const loadTypes = async () => {
            try {
                const response = await listAppointmentTypes()
                setAppointmentTypes(response.data)
            } catch (err) {
                setError(
                    getApiErrorDisplay(err, {
                        fallback: "Nie udało się wczytać typów wizyt. Odśwież stronę lub skontaktuj się z administratorem.",
                        title: "Błąd konfiguracji",
                    }),
                )
            }
        }
        void loadTypes()
    }, [])

    useEffect(() => {
        if (!patientId && patients.length > 0) {
            const primary = patients.find((patient) => patient.is_primary) ?? patients[0]
            setPatientId(primary.id)
        }
    }, [patients, patientId])

    const selectedType = appointmentTypes.find((type) => type.id === appointmentTypeId)

    useEffect(() => {
        if (selectedType && !selectedType.is_periodic) {
            setBookingMode("once")
        }
    }, [selectedType])

    const searchSlots = useCallback(async () => {
        if (!selectedType || !config) return

        setLoadingSlots(true)
        setError(null)
        setBookableSlots([])
        setSelectedSlotKey(undefined)

        const today = new Date()
        const dateTo = new Date(today)
        dateTo.setDate(dateTo.getDate() + config.appointment_booking_days)

        try {
            const response = await getAvailability({
                date_from: formatIsoDate(today),
                date_to: formatIsoDate(dateTo),
                therapist_id: therapistId,
                day_of_week: dayOfWeek,
            })
            setBookableSlots(
                splitAvailabilityIntoBookableSlots(response.data, selectedType),
            )
        } catch (err) {
            setError(
                getApiErrorDisplay(err, {
                    fallback: "Nie udało się pobrać wolnych terminów. Sprawdź filtry i spróbuj ponownie.",
                    context: "availability",
                }),
            )
        } finally {
            setLoadingSlots(false)
        }
    }, [selectedType, config, therapistId, dayOfWeek])

    const selectedSlot = bookableSlots.find((slot) => slotKey(slot) === selectedSlotKey)

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
                bookableSlots={bookableSlots}
                loadingSlots={loadingSlots}
                submitting={submitting}
                error={error}
                patientId={patientId}
                appointmentTypeId={appointmentTypeId}
                dayOfWeek={dayOfWeek}
                therapistId={therapistId}
                selectedSlotKey={selectedSlotKey}
                bookingMode={bookingMode}
                onPatientChange={setPatientId}
                onAppointmentTypeChange={setAppointmentTypeId}
                onDayOfWeekChange={setDayOfWeek}
                onTherapistChange={setTherapistId}
                onBookingModeChange={setBookingMode}
                onSlotSelect={setSelectedSlotKey}
                onSearchSlots={() => { void searchSlots(); }}
                onSubmit={() => { void handleSubmit(); }}
            />
        </Flex>
    )
}

export default ReservationNew
