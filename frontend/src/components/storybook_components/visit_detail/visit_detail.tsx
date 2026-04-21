import { Button, Card, Flex, Input, Space, Tag, Typography } from "antd"
import type React from "react"
import type { VisitDetail, VisitStatus } from "../../../types/reservations"
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
}) => (
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
                    {visit.patient_first_name ?? visit.patient_name.split(" ")[0]}{" "}
                    {visit.patient_last_name ?? visit.patient_name.split(" ").slice(1).join(" ")}
                </Text>
            </Space>

            <Space orientation="vertical" size={4}>
                <Text strong>Terapeuta</Text>
                <Text>
                    {visit.therapist_first_name ?? visit.therapist_name.split(" ")[0]}{" "}
                    {visit.therapist_last_name ?? visit.therapist_name.split(" ").slice(1).join(" ")}
                </Text>
            </Space>

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

export default VisitDetailCard
