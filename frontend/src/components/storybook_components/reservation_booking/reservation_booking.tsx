import {
    Button,
    Card,
    Flex,
    Radio,
    Select,
    Space,
    Spin,
    Typography,
} from "antd"
import type React from "react"
import ErrorAlert from "../../ErrorAlert"
import type { Patient } from "../../../types/patients"
import type { AppointmentType, BookableSlot } from "../../../types/reservations"
import { formatDatePl, formatTime } from "../../../utils/timeSlots"
import PatientSelector from "../patient_selector/patient_selector"

const { Title, Text } = Typography

const WEEKDAY_OPTIONS = [
    { value: 0, label: "Poniedziałek" },
    { value: 1, label: "Wtorek" },
    { value: 2, label: "Środa" },
    { value: 3, label: "Czwartek" },
    { value: 4, label: "Piątek" },
    { value: 5, label: "Sobota" },
    { value: 6, label: "Niedziela" },
]

export interface ReservationBookingProps {
    patients: Patient[]
    appointmentTypes: AppointmentType[]
    bookableSlots: BookableSlot[]
    loadingSlots?: boolean
    submitting?: boolean
    error?: { title: string; description: string } | null
    patientId?: string
    appointmentTypeId?: string
    dayOfWeek?: number
    therapistId?: string
    selectedSlotKey?: string
    bookingMode: "once" | "weekly"
    onPatientChange: (patientId: string) => void
    onAppointmentTypeChange: (typeId: string) => void
    onDayOfWeekChange: (day: number | undefined) => void
    onTherapistChange: (therapistId: string | undefined) => void
    onBookingModeChange: (mode: "once" | "weekly") => void
    onSlotSelect: (slotKey: string) => void
    onSearchSlots: () => void
    onSubmit: () => void
}

export const slotKey = (slot: BookableSlot): string =>
    `${slot.therapist_id}|${slot.date}|${slot.start_time}`

const ReservationBooking: React.FC<ReservationBookingProps> = ({
    patients,
    appointmentTypes,
    bookableSlots,
    loadingSlots = false,
    submitting = false,
    error,
    patientId,
    appointmentTypeId,
    dayOfWeek,
    therapistId,
    selectedSlotKey,
    bookingMode,
    onPatientChange,
    onAppointmentTypeChange,
    onDayOfWeekChange,
    onTherapistChange,
    onBookingModeChange,
    onSlotSelect,
    onSearchSlots,
    onSubmit,
}) => {
    const selectedType = appointmentTypes.find((type) => type.id === appointmentTypeId)
    const therapistOptions = Array.from(
        new Map(
            bookableSlots.map((slot) => [
                slot.therapist_id,
                { value: slot.therapist_id, label: slot.therapist_name },
            ]),
        ).values(),
    )

    const filteredSlots = bookableSlots.filter((slot) => {
        if (therapistId && slot.therapist_id !== therapistId) return false
        if (dayOfWeek !== undefined) {
            const date = new Date(`${slot.date}T12:00:00`)
            const weekday = date.getDay() === 0 ? 6 : date.getDay() - 1
            if (weekday !== dayOfWeek) return false
        }
        return true
    })

    const canBookWeekly = selectedType?.is_periodic ?? false

    return (
        <Flex vertical gap={16}>
            {error && (
                <ErrorAlert
                    title={error.title}
                    description={error.description}
                />
            )}

            <Card title="1. Pacjent">
                <PatientSelector
                    patients={patients}
                    value={patientId}
                    onChange={onPatientChange}
                />
            </Card>

            <Card title="2. Typ wizyty">
                <Select
                    style={{ width: "100%" }}
                    placeholder="Wybierz typ wizyty"
                    value={appointmentTypeId}
                    onChange={onAppointmentTypeChange}
                    options={appointmentTypes.map((type) => ({
                        value: type.id,
                        label: `${type.name} (${type.duration_time_minutes} min, ${type.price} zł)`,
                    }))}
                />
            </Card>

            <Card title="3. Filtry terminów">
                <Space wrap style={{ width: "100%" }}>
                    <Select
                        allowClear
                        placeholder="Dzień tygodnia"
                        style={{ minWidth: 180 }}
                        value={dayOfWeek}
                        onChange={onDayOfWeekChange}
                        options={WEEKDAY_OPTIONS}
                    />
                    <Select
                        allowClear
                        placeholder="Terapeuta"
                        style={{ minWidth: 220 }}
                        value={therapistId}
                        onChange={onTherapistChange}
                        options={therapistOptions}
                    />
                    <Button
                        type="primary"
                        onClick={onSearchSlots}
                        disabled={!appointmentTypeId}
                        loading={loadingSlots}
                    >
                        Szukaj terminów
                    </Button>
                </Space>
            </Card>

            <Card title="4. Dostępne terminy">
                {loadingSlots ? (
                    <Flex justify="center" style={{ padding: 24 }}>
                        <Spin />
                    </Flex>
                ) : filteredSlots.length === 0 ? (
                    <Text type="secondary">Brak dostępnych terminów dla wybranych filtrów.</Text>
                ) : (
                    <Radio.Group
                        style={{ width: "100%" }}
                        value={selectedSlotKey}
                        onChange={(event) => { onSlotSelect(event.target.value as string); }}
                    >
                        <Flex vertical gap={8}>
                            {filteredSlots.map((slot) => {
                                const key = slotKey(slot)
                                return (
                                    <Radio key={key} value={key}>
                                        <Space orientation="vertical" size={0}>
                                            <Text strong>
                                                {formatDatePl(slot.date)}, {formatTime(slot.start_time)}
                                                {" – "}
                                                {formatTime(slot.end_time)}
                                            </Text>
                                            <Text type="secondary">
                                                {slot.therapist_name}
                                                {slot.localization ? ` · ${slot.localization}` : ""}
                                            </Text>
                                        </Space>
                                    </Radio>
                                )
                            })}
                        </Flex>
                    </Radio.Group>
                )}
            </Card>

            {selectedType && (
                <Card title="5. Potwierdzenie">
                    <Space orientation="vertical">
                        <Text>Tryb rezerwacji:</Text>
                        <Radio.Group
                            value={bookingMode}
                            onChange={(event) => {
                                onBookingModeChange(event.target.value as "once" | "weekly")
                            }}
                        >
                            <Radio value="once">Jednorazowa</Radio>
                            <Radio value="weekly" disabled={!canBookWeekly}>
                                Cykliczna (co tydzień)
                            </Radio>
                        </Radio.Group>
                        {!canBookWeekly && (
                            <Text type="secondary">
                                Wybrany typ wizyty nie obsługuje rezerwacji cyklicznej.
                            </Text>
                        )}
                        <Button
                            type="primary"
                            size="large"
                            disabled={!patientId || !selectedSlotKey}
                            loading={submitting}
                            onClick={onSubmit}
                        >
                            Zarezerwuj
                        </Button>
                    </Space>
                </Card>
            )}
        </Flex>
    )
}

export default ReservationBooking
