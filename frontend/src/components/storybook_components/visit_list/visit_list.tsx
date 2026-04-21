import { Button, Card, Empty, Space, Table, Tag, Typography } from "antd"
import type { ColumnsType } from "antd/es/table"
import type React from "react"
import type { Visit, VisitStatus } from "../../../types/reservations"
import { formatDatePl, formatTime } from "../../../utils/timeSlots"

const { Text } = Typography

const STATUS_LABELS: Record<VisitStatus, string> = {
    SCHEDULED: "Zaplanowana",
    COMPLETED: "Zakończona",
    CANCELED: "Anulowana",
}

const STATUS_COLORS: Record<VisitStatus, string> = {
    SCHEDULED: "blue",
    COMPLETED: "green",
    CANCELED: "red",
}

export interface VisitListProps {
    visits: Visit[]
    loading?: boolean
    showNotes?: boolean
    onOpen?: (id: string) => void
    onCancel?: (id: string) => void
    cancelingId?: string | null
    canCancelVisit?: (visit: Visit) => boolean
}

const VisitList: React.FC<VisitListProps> = ({
    visits,
    loading = false,
    showNotes = false,
    onOpen,
    onCancel,
    cancelingId,
    canCancelVisit,
}) => {
    const columns: ColumnsType<Visit> = [
        {
            title: "Data",
            render: (_, row) => (
                <Space orientation="vertical" size={0}>
                    <Text>{formatDatePl(row.appointment_date)}</Text>
                    <Text type="secondary">
                        {formatTime(row.start_time)} – {formatTime(row.end_time)}
                    </Text>
                </Space>
            ),
        },
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
            title: "Cena",
            dataIndex: "final_price",
            render: (price: string) => `${price} zł`,
        },
        {
            title: "Status",
            dataIndex: "status",
            render: (status: VisitStatus) => (
                <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Tag>
            ),
        },
    ]

    if (showNotes) {
        columns.push({
            title: "Notatka",
            dataIndex: "notes",
            render: (notes?: string | null) => notes || "—",
            ellipsis: true,
        })
    }

    columns.push({
        title: "Akcje",
        render: (_, row) => (
            <Space>
                {onOpen && (
                    <Button type="link" onClick={() => { onOpen(row.id); }}>
                        Szczegóły
                    </Button>
                )}
                {onCancel
                    && row.status === "SCHEDULED"
                    && (canCancelVisit?.(row) ?? true) && (
                    <Button
                        danger
                        type="link"
                        loading={cancelingId === row.id}
                        onClick={() => { onCancel(row.id); }}
                    >
                        Anuluj
                    </Button>
                )}
            </Space>
        ),
    })

    return (
        <Card>
            <Table
                rowKey="id"
                columns={columns}
                dataSource={visits}
                loading={loading}
                locale={{ emptyText: <Empty description="Brak wizyt" /> }}
                pagination={{ pageSize: 10, hideOnSinglePage: true }}
            />
        </Card>
    )
}

export default VisitList
