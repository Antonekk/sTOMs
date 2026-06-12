import { Flex, Segmented, Switch, Typography, message } from "antd"
import AppAlert from "../components/app_alert/app_alert"
import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { cancelVisit, listVisits } from "../api/visits"
import VisitList from "../components/visit_list/visit_list"
import Loading from "../components/loading/loading"
import { useAuthentication } from "../auth/AuthProvider"
import { useAppConfig } from "../config/ConfigProvider"
import { getApiErrorMessage } from "../utils/apiError"
import { canCancelByWindow, isUpcomingVisit } from "../utils/timeSlots"
import type { Visit } from "../types/reservations"

const { Title, Text } = Typography

type TabValue = "upcoming" | "history"

const Visits: React.FC = () => {
    const navigate = useNavigate()
    const { user } = useAuthentication()
    const { config } = useAppConfig()
    const [visits, setVisits] = useState<Visit[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [tab, setTab] = useState<TabValue>("upcoming")
    const [includeCanceled, setIncludeCanceled] = useState(false)
    const [cancelingId, setCancelingId] = useState<string | null>(null)

    const isTherapist = user?.role === "THERAPIST"

    const loadVisits = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const response = await listVisits({
                include_canceled: includeCanceled,
            })
            setVisits(response.data)
        } catch (err) {
            setError(getApiErrorMessage(err, "Nie udało się wczytać wizyt."))
        } finally {
            setLoading(false)
        }
    }, [includeCanceled])

    useEffect(() => {
        void loadVisits()
    }, [loadVisits])

    const filteredVisits = useMemo(() => {
        return visits.filter((visit) => {
            const upcoming = isUpcomingVisit(visit.appointment_date)
            return tab === "upcoming" ? upcoming : !upcoming
        })
    }, [visits, tab])

    const canCancelVisit = (visit: Visit): boolean => {
        if (!config || visit.status !== "SCHEDULED") return false
        return canCancelByWindow(
            visit.appointment_date,
            visit.start_time,
            config.cancellation_window_hours,
        )
    }

    const handleCancel = async (id: string) => {
        setCancelingId(id)
        try {
            await cancelVisit(id)
            void message.success("Wizyta została anulowana.")
            await loadVisits()
        } catch (err) {
            setError(getApiErrorMessage(err, "Nie udało się anulować wizyty."))
        } finally {
            setCancelingId(null)
        }
    }

    if (loading && visits.length === 0) {
        return <Loading />
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
            <Title level={2} style={{ margin: 0 }}>
                {isTherapist ? "Moje zajęcia" : "Moje wizyty"}
            </Title>

            <Segmented
                value={tab}
                onChange={(value) => { setTab(value as TabValue); }}
                options={[
                    { label: "Nadchodzące", value: "upcoming" },
                    { label: "Historia", value: "history" },
                ]}
            />

            <Flex align="center" gap={8}>
                <Switch
                    checked={includeCanceled}
                    onChange={setIncludeCanceled}
                />
                <Text>Pokaż anulowane</Text>
            </Flex>

            {config && tab === "upcoming" && !isTherapist && (
                <AppAlert
                    type="info"
                    title={`Anulowanie możliwe najpóźniej ${String(config.cancellation_window_hours)} godzin przed wizytą.`}
                />
            )}

            {error && <AppAlert title={error} />}

            <VisitList
                visits={filteredVisits}
                loading={loading}
                showNotes={isTherapist}
                onOpen={(visitId) => { void navigate(`/wizyty/${visitId}`); }}
                onCancel={!isTherapist ? (visitId) => { void handleCancel(visitId); } : undefined}
                cancelingId={cancelingId}
                canCancelVisit={canCancelVisit}
            />
        </Flex>
    )
}

export default Visits
