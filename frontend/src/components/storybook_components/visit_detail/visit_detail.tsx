import { Button, Card, Flex, Input, Space, Tag, Typography } from "antd"
import type React from "react"
import type { VisitDetail, VisitStatus } from "../../../types/reservations"
import OfficeLocationDisplay from "../office_location/office_location"
import { formatDatePl, formatTime } from "../../../utils/timeSlots"

const { Title, Text } = Typography
const { TextArea } = Input

const STATUS_LABELS: Record<VisitStatus, string> = {
    SCHEDULED: "Zaplanowana",
    COMPLETED: "Zakończona",
    CANCELED: "Anulowana",
}

export interface VisitDetailCardProps {
    visit: VisitDetail
    role: "CLIENT" | "THERAPIST"
    notes?: string
    onNotesChange?: (value: string) => void
    onSaveNote?: () => void
    onComplete?: () => void
    onCancel?: () => void
    savingNote?: boolean
    updatingStatus?: boolean
    canCancel?: boolean
    canUpdateStatus?: boolean
}

const splitFullName = (fullName: string): [string, string] => {
    const parts = fullName.split(" ")
    return [parts[0] ?? "", parts.slice(1).join(" ")]
}

const VisitDetailCard: React.FC<VisitDetailCardProps> = ({
    visit,
    role,
    notes = "",
    onNotesChange,
    onSaveNote,
    onComplete,
    onCancel,
    savingNote = false,
    updatingStatus = false,
    canCancel = false,
    canUpdateStatus = false,
}) => {
    const [patientFirstName, patientLastName] = splitFullName(visit.patient_name)
    const [therapistFirstName, therapistLastName] = splitFullName(visit.therapist_name)

    return (
    <Card>
        <Flex vertical gap={16}>
            <Space align="center">
                <Title level={3} style={{ margin: 0 }}>
                    {visit.appointment_type_name}
                </Title>
                <Tag>{STATUS_LABELS[visit.status]}</Tag>
            </Space>

            <Space orientation="vertical" size={4}>
                <Text>
                    <Text strong>Data: </Text>
                    {formatDatePl(visit.appointment_date)}
                </Text>
                <Text>
                    <Text strong>Godzina: </Text>
                    {formatTime(visit.start_time)} – {formatTime(visit.end_time)}
                </Text>
                <Text>
                    <Text strong>Cena: </Text>
                    {visit.final_price} zł
                </Text>
            </Space>

            <Space orientation="vertical" size={4}>
                <Text strong>Pacjent</Text>
                <Text>
                    {patientFirstName} {patientLastName}
                </Text>
            </Space>

            <Space orientation="vertical" size={4}>
                <Text strong>Terapeuta</Text>
                <Text>
                    {therapistFirstName} {therapistLastName}
                </Text>
            </Space>

            <OfficeLocationDisplay office={visit.office} />

            {role === "THERAPIST" && (
                <Space orientation="vertical" style={{ width: "100%" }}>
                    <Text strong>Notatka terapeuty</Text>
                    <TextArea
                        rows={5}
                        value={notes}
                        onChange={(event) => { onNotesChange?.(event.target.value); }}
                        placeholder="Dodaj notatkę z zajęć..."
                    />
                    <Button
                        onClick={onSaveNote}
                        loading={savingNote}
                        disabled={!onSaveNote}
                    >
                        Zapisz notatkę
                    </Button>
                </Space>
            )}

            {role === "THERAPIST" && visit.status === "SCHEDULED" && (
                <Space wrap>
                    <Button
                        type="primary"
                        onClick={onComplete}
                        loading={updatingStatus}
                        disabled={!canUpdateStatus || !onComplete}
                    >
                        Oznacz jako zakończoną
                    </Button>
                    <Button
                        danger
                        onClick={onCancel}
                        loading={updatingStatus}
                        disabled={!canCancel || !onCancel}
                    >
                        Anuluj wizytę
                    </Button>
                </Space>
            )}

            {role === "CLIENT" && visit.status === "SCHEDULED" && (
                <Button
                    danger
                    onClick={onCancel}
                    loading={updatingStatus}
                    disabled={!canCancel || !onCancel}
                >
                    Anuluj wizytę
                </Button>
            )}
        </Flex>
    </Card>
    )
}

export default VisitDetailCard
