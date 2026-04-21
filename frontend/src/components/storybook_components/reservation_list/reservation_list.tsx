import { Button, Card, Empty, Space, Table, Tag, Typography } from "antd"
import type { ColumnsType } from "antd/es/table"
import type React from "react"
import type { ReservationSeries, SeriesStatus } from "../../../types/reservations"
import { formatDatePl, formatTime } from "../../../utils/timeSlots"

const { Text } = Typography

const STATUS_LABELS: Record<SeriesStatus, string> = {
    ACTIVE: "Aktywna",
    ENDED: "Zakończona",
    CANCELED: "Anulowana",
}

const STATUS_COLORS: Record<SeriesStatus, string> = {
    ACTIVE: "green",
    ENDED: "default",
    CANCELED: "red",
}

export interface ReservationListProps {
    reservations: ReservationSeries[]
    loading?: boolean
    onOpen?: (id: string) => void
    onCancel?: (id: string) => void
    cancelingId?: string | null
}

const ReservationList: React.FC<ReservationListProps> = ({
    reservations,
    loading = false,
    onOpen,
    onCancel,
    cancelingId,
}) => {
    const columns: ColumnsType<ReservationSeries> = [
        {
            title: "Pacjent",
            dataIndex: "patient_name",
        },
        {
            title: "Terapeuta",
            dataIndex: "therapist_name",
        },
        {
            title: "Typ",
            dataIndex: "appointment_type_name",
        },
        {
            title: "Termin",
            render: (_, row) => (
                <Space orientation="vertical" size={0}>
                    <Text>{formatDatePl(row.start_date)}</Text>
                    <Text type="secondary">
                        {formatTime(row.start_time)} – {formatTime(row.end_time)}
                    </Text>
                    {row.recurrence_display && (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                            {row.recurrence_display}
                        </Text>
                    )}
                </Space>
            ),
        },
        {
            title: "Status",
            dataIndex: "status",
            render: (status: SeriesStatus) => (
                <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Tag>
            ),
        },
        {
            title: "Akcje",
            render: (_, row) => (
                <Space>
                    {onOpen && (
                        <Button type="link" onClick={() => { onOpen(row.id); }}>
                            Szczegóły
                        </Button>
                    )}
                    {onCancel && row.status === "ACTIVE" && (
                        <Button
                            danger
                            type="link"
                            loading={cancelingId === row.id}
                            onClick={() => { onCancel(row.id); }}
                        >
                            Anuluj serię
                        </Button>
                    )}
                </Space>
            ),
        },
    ]

    return (
        <Card>
            <Table
                rowKey="id"
                columns={columns}
                dataSource={reservations}
                loading={loading}
                locale={{ emptyText: <Empty description="Brak rezerwacji" /> }}
                pagination={{ pageSize: 10, hideOnSinglePage: true }}
            />
        </Card>
    )
}

export default ReservationList
