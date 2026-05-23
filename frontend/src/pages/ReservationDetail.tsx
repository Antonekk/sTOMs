import { Button, Card, Flex, Space, Table, Tag, Typography, message } from "antd"
import AppAlert from "../components/app_alert/app_alert"
import { useCallback, useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { cancelReservation, getReservation } from "../api/reservations"
import Loading from "../components/loading/loading"
import { getApiErrorMessage } from "../utils/apiError"
import { formatDatePl, formatTime } from "../utils/timeSlots"
import OfficeLocationDisplay from "../components/office_location/office_location"
import type { ReservationSeriesDetail, SeriesStatus, VisitStatus } from "../types/reservations"

const { Title, Text } = Typography

const SERIES_STATUS: Record<SeriesStatus, string> = {
    ACTIVE: "Aktywna",
    ENDED: "Zakończona",
    CANCELED: "Anulowana",
}

const VISIT_STATUS: Record<VisitStatus, string> = {
    SCHEDULED: "Zaplanowana",
    COMPLETED: "Zakończona",
    CANCELED: "Anulowana",
}

const ReservationDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [reservation, setReservation] = useState<ReservationSeriesDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [canceling, setCanceling] = useState(false)

    const load = useCallback(async () => {
        if (!id) return
        setLoading(true)
        setError(null)
        try {
            const response = await getReservation(id)
            setReservation(response.data)
        } catch (err) {
            setError(getApiErrorMessage(err, "Nie udało się wczytać rezerwacji."))
        } finally {
            setLoading(false)
        }
    }, [id])

    useEffect(() => {
        void load()
    }, [load])

    const handleCancel = async () => {
        if (!id) return
        setCanceling(true)
        try {
            await cancelReservation(id)
            void message.success("Rezerwacja została anulowana.")
            await load()
        } catch (err) {
            void message.error(getApiErrorMessage(err, "Nie udało się anulować rezerwacji."))
        } finally {
            setCanceling(false)
        }
    }

    if (loading) return <Loading />
    if (error || !reservation) {
        return (
            <Flex style={{ padding: 24 }}>
                <AppAlert title={error ?? "Nie znaleziono rezerwacji."} />
            </Flex>
        )
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
            <Button type="link" onClick={() => { void navigate("/rezerwacje"); }} style={{ alignSelf: "flex-start" }}>
                ← Powrót do listy
            </Button>

            <Card>
                <Flex vertical gap={12}>
                    <Space>
                        <Title level={3} style={{ margin: 0 }}>{reservation.appointment_type_name}</Title>
                        <Tag>{SERIES_STATUS[reservation.status]}</Tag>
                    </Space>
                    <Text>Pacjent: {reservation.patient_name}</Text>
                    <Text>Terapeuta: {reservation.therapist_name}</Text>
                    <OfficeLocationDisplay office={reservation.office} />
                    <Text>
                        {formatDatePl(reservation.start_date)}, {formatTime(reservation.start_time)}
                        {" – "}
                        {formatTime(reservation.end_time)}
                    </Text>
                    {reservation.recurrence_display && (
                        <Text type="secondary">{reservation.recurrence_display}</Text>
                    )}
                    {reservation.status === "ACTIVE" && (
                        <Button danger loading={canceling} onClick={() => { void handleCancel(); }}>
                            Anuluj całą rezerwację
                        </Button>
                    )}
                </Flex>
            </Card>

            <Card title="Wizyty w serii">
                <Table
                    rowKey="id"
                    dataSource={reservation.appointments}
                    pagination={false}
                    columns={[
                        {
                            title: "Data",
                            dataIndex: "appointment_date",
                            render: (value: string) => formatDatePl(value),
                        },
                        {
                            title: "Status",
                            dataIndex: "status",
                            render: (value: VisitStatus) => VISIT_STATUS[value],
                        },
                        {
                            title: "Cena",
                            dataIndex: "final_price",
                            render: (value: string) => `${value} zł`,
                        },
                    ]}
                />
            </Card>
        </Flex>
    )
}

export default ReservationDetailPage
