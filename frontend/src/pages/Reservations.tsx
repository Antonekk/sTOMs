import { Button, Flex, Segmented, Typography, message } from "antd"
import AppAlert from "../components/storybook_components/app_alert/app_alert"
import { useCallback, useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { cancelReservation, listReservations } from "../api/reservations"
import ReservationList from "../components/storybook_components/reservation_list/reservation_list"
import Loading from "../components/storybook_components/loading/loading"
import { getApiErrorMessage } from "../utils/apiError"
import type { ReservationSeries, SeriesStatus } from "../types/reservations"

const { Title } = Typography

type FilterValue = "all" | SeriesStatus

const Reservations: React.FC = () => {
    const navigate = useNavigate()
    const [reservations, setReservations] = useState<ReservationSeries[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [filter, setFilter] = useState<FilterValue>("all")
    const [cancelingId, setCancelingId] = useState<string | null>(null)

    const loadReservations = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const status = filter === "all" ? undefined : filter
            const response = await listReservations(status)
            setReservations(response.data)
        } catch (err) {
            setError(getApiErrorMessage(err, "Nie udało się wczytać rezerwacji."))
        } finally {
            setLoading(false)
        }
    }, [filter])

    useEffect(() => {
        void loadReservations()
    }, [loadReservations])

    const handleCancel = async (id: string) => {
        setCancelingId(id)
        try {
            await cancelReservation(id)
            void message.success("Rezerwacja została anulowana.")
            await loadReservations()
        } catch (err) {
            void message.error(getApiErrorMessage(err, "Nie udało się anulować rezerwacji."))
        } finally {
            setCancelingId(null)
        }
    }

    if (loading && reservations.length === 0) {
        return <Loading />
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
            <Flex justify="space-between" align="center" wrap gap={12}>
                <Title level={2} style={{ margin: 0 }}>Moje rezerwacje</Title>
                <Button type="primary" onClick={() => { void navigate("/rezerwacje/nowa"); }}>
                    Nowa rezerwacja
                </Button>
            </Flex>

            <Segmented
                value={filter}
                onChange={(value) => { setFilter(value as FilterValue); }}
                options={[
                    { label: "Wszystkie", value: "all" },
                    { label: "Aktywne", value: "ACTIVE" },
                    { label: "Zakończone", value: "ENDED" },
                    { label: "Anulowane", value: "CANCELED" },
                ]}
            />

            {error && <AppAlert title={error} />}

            <ReservationList
                reservations={reservations}
                loading={loading}
                onOpen={(id) => { void navigate(`/rezerwacje/${id}`); }}
                onCancel={(id) => { void handleCancel(id); }}
                cancelingId={cancelingId}
            />
        </Flex>
    )
}

export default Reservations
