import {
    Button,
    Card,
    DatePicker,
    Flex,
    Pagination,
    Radio,
    Select,
    Space,
    Spin,
    Typography,
} from "antd"
import dayjs from "dayjs"
import type React from "react"
import AppAlert from "../app_alert/app_alert"
import OfficeLocationDisplay from "../office_location/office_location"
import type { Patient } from "../../types/patients"
import type {
    AppointmentType,
    BookableSlot,
    BookableTimeOptions,
    BookingTherapist,
} from "../../types/reservations"
import { formatOfficeLocationShort } from "../../utils/officeDisplay"
import { formatDatePl, formatTime } from "../../utils/timeSlots"
import PatientSelector from "../patient_selector/patient_selector"

const { Text } = Typography

const WEEKDAY_OPTIONS = [
    { value: 0, label: "Poniedziałek" },
    { value: 1, label: "Wtorek" },
    { value: 2, label: "Środa" },
    { value: 3, label: "Czwartek" },
    { value: 4, label: "Piątek" },
    { value: 5, label: "Sobota" },
    { value: 6, label: "Niedziela" },
]

export interface OfficeOption {
    value: string
    label: string
}

export type LocationFilterMode = "therapist" | "office"

export interface ReservationBookingProps {
    patients: Patient[]
    appointmentTypes: AppointmentType[]
    therapists: BookingTherapist[]
    officeOptions: OfficeOption[]
    bookableSlots: BookableSlot[]
    timeOptions: BookableTimeOptions
    slotsTotal: number
    slotsPage: number
    slotsPageSize: number
    maxBookingDate?: string
    hasSearched?: boolean
    loadingSlots?: boolean
    loadingTimeOptions?: boolean
    submitting?: boolean
    error?: { title: string; description: string } | null
    patientId?: string
    appointmentTypeId?: string
    bookingMode: "once" | "weekly"
    visitDate?: string
    dayOfWeek?: number
    startDate?: string
    locationFilterMode: LocationFilterMode
    therapistId?: string
    officeId?: string
    timeFrom?: string
    timeTo?: string
    selectedSlotKey?: string
    onPatientChange: (patientId: string) => void
    onAppointmentTypeChange: (typeId: string) => void
    onBookingModeChange: (mode: "once" | "weekly") => void
    onVisitDateChange: (date: string | undefined) => void
    onDayOfWeekChange: (day: number | undefined) => void
    onStartDateChange: (date: string | undefined) => void
    onLocationFilterModeChange: (mode: LocationFilterMode) => void
    onTherapistChange: (therapistId: string | undefined) => void
    onOfficeChange: (officeId: string | undefined) => void
    onTimeFromChange: (time: string | undefined) => void
    onTimeToChange: (time: string | undefined) => void
    onSlotSelect: (slotKey: string) => void
    onSearchSlots: () => void
    onSlotsPageChange: (page: number) => void
    onSubmit: () => void
}

export const slotKey = (slot: BookableSlot): string =>
    `${slot.therapist_id}|${slot.date}|${slot.start_time}`

const djangoWeekdayFromDayjs = (value: { day: () => number }): number =>
    (value.day() + 6) % 7

const ReservationBooking: React.FC<ReservationBookingProps> = ({
    patients,
    appointmentTypes,
    therapists,
    officeOptions,
    bookableSlots,
    timeOptions,
    slotsTotal,
    slotsPage,
    slotsPageSize,
    maxBookingDate,
    hasSearched = false,
    loadingSlots = false,
    loadingTimeOptions = false,
    submitting = false,
    error,
    patientId,
    appointmentTypeId,
    bookingMode,
    visitDate,
    dayOfWeek,
    startDate,
    locationFilterMode,
    therapistId,
    officeId,
    timeFrom,
    timeTo,
    selectedSlotKey,
    onPatientChange,
    onAppointmentTypeChange,
    onBookingModeChange,
    onVisitDateChange,
    onDayOfWeekChange,
    onStartDateChange,
    onLocationFilterModeChange,
    onTherapistChange,
    onOfficeChange,
    onTimeFromChange,
    onTimeToChange,
    onSlotSelect,
    onSearchSlots,
    onSlotsPageChange,
    onSubmit,
}) => {
    const selectedType = appointmentTypes.find((type) => type.id === appointmentTypeId)
    const canBookWeekly = selectedType?.is_periodic ?? false
    const today = dayjs().startOf("day")
    const maxDate = maxBookingDate ? dayjs(maxBookingDate) : undefined

    const therapistOptions = therapists.map((therapist) => ({
        value: therapist.id,
        label: therapist.full_name,
    }))

    const selectedTherapist = therapists.find((therapist) => therapist.id === therapistId)
    const therapistForOffice = officeId
        ? therapists.find((therapist) => therapist.office_id === officeId)
        : undefined

    const dateFiltersReady =
        bookingMode === "once"
            ? Boolean(visitDate)
            : dayOfWeek !== undefined && Boolean(startDate)

    const validEndTimes = timeOptions.end_times.filter(
        (endTime) => !timeFrom || endTime > timeFrom,
    )

    const disableWeeklyStartDate = (current: Parameters<NonNullable<React.ComponentProps<typeof DatePicker>["disabledDate"]>>[0]) => {
        if (current.isBefore(today, "day")) return true
        if (maxDate && current.isAfter(maxDate, "day")) return true
        if (dayOfWeek !== undefined && djangoWeekdayFromDayjs(current) !== dayOfWeek) {
            return true
        }
        return false
    }

    return (
        <Flex vertical gap={16}>
            {error && (
                <AppAlert
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
                        label: `${type.name} (${String(type.duration_time_minutes)} min, ${type.price} zł)`,
                    }))}
                />
            </Card>

            {appointmentTypeId && (
                <Card title="3. Tryb rezerwacji">
                    <Radio.Group
                        value={bookingMode}
                        onChange={(event) => {
                            onBookingModeChange(event.target.value as "once" | "weekly")
                        }}
                    >
                        <Space orientation="vertical">
                            <Radio value="once">Jednorazowa</Radio>
                            <Radio value="weekly" disabled={!canBookWeekly}>
                                Cykliczna (co tydzień)
                            </Radio>
                        </Space>
                    </Radio.Group>
                    {!canBookWeekly && (
                        <Text type="secondary" style={{ display: "block", marginTop: 8 }}>
                            Wybrany typ wizyty nie obsługuje rezerwacji cyklicznej.
                        </Text>
                    )}
                </Card>
            )}

            {appointmentTypeId && (
                <Card title="4. Filtry terminów">
                    <Flex vertical gap={12}>
                        {bookingMode === "once" ? (
                            <DatePicker
                                placeholder="Dzień wizyty"
                                value={visitDate ? dayjs(visitDate) : undefined}
                                minDate={today}
                                maxDate={maxDate}
                                onChange={(value) => {
                                    onVisitDateChange(
                                        value ? value.format("YYYY-MM-DD") : undefined,
                                    )
                                }}
                                format="DD.MM.YYYY"
                            />
                        ) : (
                            <Space wrap style={{ width: "100%" }}>
                                <Select
                                    placeholder="Dzień tygodnia"
                                    style={{ minWidth: 180 }}
                                    value={dayOfWeek}
                                    onChange={onDayOfWeekChange}
                                    options={WEEKDAY_OPTIONS}
                                />
                                <DatePicker
                                    placeholder="Dzień początkowy"
                                    value={startDate ? dayjs(startDate) : undefined}
                                    disabled={dayOfWeek === undefined}
                                    disabledDate={disableWeeklyStartDate}
                                    onChange={(value) => {
                                        onStartDateChange(
                                            value ? value.format("YYYY-MM-DD") : undefined,
                                        )
                                    }}
                                    format="DD.MM.YYYY"
                                />
                            </Space>
                        )}

                        <Flex vertical gap={8} style={{ width: "100%" }}>
                            <Radio.Group
                                value={locationFilterMode}
                                onChange={(event) => {
                                    onLocationFilterModeChange(
                                        event.target.value as LocationFilterMode,
                                    )
                                }}
                            >
                                <Radio value="therapist">Terapeuta</Radio>
                                <Radio value="office">Lokalizacja</Radio>
                            </Radio.Group>

                            {locationFilterMode === "therapist" ? (
                                <Flex vertical gap={4}>
                                    <Select
                                        allowClear
                                        showSearch={{ optionFilterProp: "label" }}
                                        placeholder="Wybierz terapeutę"
                                        style={{ minWidth: 280 }}
                                        value={therapistId}
                                        onChange={onTherapistChange}
                                        options={therapistOptions}
                                    />
                                    {selectedTherapist?.office && (
                                        <Text type="secondary">
                                            Gabinet:{" "}
                                            {formatOfficeLocationShort(selectedTherapist.office)}
                                        </Text>
                                    )}
                                </Flex>
                            ) : (
                                <Flex vertical gap={4}>
                                    <Select
                                        allowClear
                                        showSearch={{ optionFilterProp: "label" }}
                                        placeholder="Wybierz lokalizację / gabinet"
                                        style={{ minWidth: 280 }}
                                        value={officeId}
                                        onChange={onOfficeChange}
                                        options={officeOptions}
                                    />
                                    {therapistForOffice && (
                                        <Text type="secondary">
                                            Terapeuta: {therapistForOffice.full_name}
                                        </Text>
                                    )}
                                </Flex>
                            )}
                        </Flex>

                        {dateFiltersReady && (
                            loadingTimeOptions ? (
                                <Flex align="center" gap={8}>
                                    <Spin size="small" />
                                    <Text type="secondary">Ładowanie dostępnych godzin…</Text>
                                </Flex>
                            ) : timeOptions.start_times.length === 0 ? (
                                <Text type="secondary">
                                    Brak wolnych godzin dla wybranych filtrów daty.
                                </Text>
                            ) : (
                                <Space wrap style={{ width: "100%" }}>
                                    <Select
                                        allowClear
                                        placeholder="Godzina od"
                                        style={{ minWidth: 140 }}
                                        value={timeFrom}
                                        onChange={onTimeFromChange}
                                        options={timeOptions.start_times.map((time) => ({
                                            value: time,
                                            label: time,
                                        }))}
                                    />
                                    <Select
                                        allowClear
                                        placeholder="Godzina do"
                                        style={{ minWidth: 140 }}
                                        value={timeTo}
                                        onChange={onTimeToChange}
                                        disabled={validEndTimes.length === 0}
                                        options={validEndTimes.map((time) => ({
                                            value: time,
                                            label: time,
                                        }))}
                                    />
                                </Space>
                            )
                        )}

                        <Button
                            type="primary"
                            onClick={onSearchSlots}
                            disabled={!dateFiltersReady || loadingTimeOptions}
                            loading={loadingSlots}
                        >
                            Szukaj terminów
                        </Button>
                    </Flex>
                </Card>
            )}

            {appointmentTypeId && (
                <Card title="5. Dostępne terminy">
                    {loadingSlots ? (
                        <Flex justify="center" style={{ padding: 24 }}>
                            <Spin />
                        </Flex>
                    ) : bookableSlots.length === 0 ? (
                        <Text type="secondary">
                            {hasSearched
                                ? "Brak dostępnych terminów dla wybranych filtrów."
                                : "Ustaw filtry i kliknij „Szukaj terminów”, aby zobaczyć wolne terminy."}
                        </Text>
                    ) : (
                        <Flex vertical gap={16}>
                            <Radio.Group
                                style={{ width: "100%" }}
                                value={selectedSlotKey}
                                onChange={(event) => {
                                    onSlotSelect(event.target.value as string)
                                }}
                            >
                                <Flex vertical gap={8}>
                                    {bookableSlots.map((slot) => {
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
                                                    </Text>
                                                    <OfficeLocationDisplay office={slot.office} compact />
                                                </Space>
                                            </Radio>
                                        )
                                    })}
                                </Flex>
                            </Radio.Group>
                            {slotsTotal > slotsPageSize && (
                                <Pagination
                                    current={slotsPage}
                                    pageSize={slotsPageSize}
                                    total={slotsTotal}
                                    onChange={onSlotsPageChange}
                                    showSizeChanger={false}
                                    showTotal={(total) => `Łącznie ${String(total)} terminów`}
                                />
                            )}
                        </Flex>
                    )}
                </Card>
            )}

            {appointmentTypeId && selectedSlotKey && (
                <Card title="6. Potwierdzenie">
                    <Space orientation="vertical">
                        <Text>
                            Tryb: {bookingMode === "once" ? "jednorazowa" : "cykliczna (co tydzień)"}
                        </Text>
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
