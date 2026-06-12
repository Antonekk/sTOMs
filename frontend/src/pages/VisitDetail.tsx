import { Button, Flex, message } from "antd"
import AppAlert from "../components/app_alert/app_alert"
import { useCallback, useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import {
    cancelVisit,
    getVisit,
    updateVisitNote,
    updateVisitStatus,
} from "../api/visits"
import VisitDetailCard from "../components/visit_detail/visit_detail"
import Loading from "../components/loading/loading"
import { useAuthentication } from "../auth/AuthProvider"
import { useAppConfig } from "../config/ConfigProvider"
import { getApiErrorMessage } from "../utils/apiError"
import { canCancelByWindow, isPastVisit } from "../utils/timeSlots"
import type { VisitDetail } from "../types/reservations"

const VisitDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const { user } = useAuthentication()
    const { config } = useAppConfig()

    const [visit, setVisit] = useState<VisitDetail | null>(null)
    const [notes, setNotes] = useState("")
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [savingNote, setSavingNote] = useState(false)
    const [updatingStatus, setUpdatingStatus] = useState(false)

    const isTherapist = user?.role === "THERAPIST"
    const role = isTherapist ? "THERAPIST" : "CLIENT"

    const load = useCallback(async () => {
        if (!id) return
        setLoading(true)
        setError(null)
        try {
            const response = await getVisit(id)
            setVisit(response.data)
            setNotes(response.data.notes ?? "")
        } catch (err) {
            setError(getApiErrorMessage(err, "Nie udało się wczytać wizyty."))
        } finally {
            setLoading(false)
        }
    }, [id])

    useEffect(() => {
        void load()
    }, [load])

    const canCancel = Boolean(
        visit
        && config
        && visit.status === "SCHEDULED"
        && canCancelByWindow(
            visit.appointment_date,
            visit.start_time,
            config.cancellation_window_hours,
        ),
    )

    const canComplete = Boolean(
        visit
        && visit.status === "SCHEDULED"
        && isPastVisit(visit.appointment_date, visit.end_time),
    )

    const handleSaveNote = async () => {
        if (!id) return
        setSavingNote(true)
        try {
            const response = await updateVisitNote(id, notes)
            setVisit(response.data)
            void message.success("Notatka została zapisana.")
        } catch (err) {
            void message.error(getApiErrorMessage(err, "Nie udało się zapisać notatki."))
        } finally {
            setSavingNote(false)
        }
    }

    const handleComplete = async () => {
        if (!id) return
        setUpdatingStatus(true)
        try {
            const response = await updateVisitStatus(id, "COMPLETED")
            setVisit(response.data)
            void message.success("Wizyta oznaczona jako zakończona.")
        } catch (err) {
            void message.error(getApiErrorMessage(err, "Nie udało się zaktualizować statusu."))
        } finally {
            setUpdatingStatus(false)
        }
    }

    const handleCancel = async () => {
        if (!id) return
        setUpdatingStatus(true)
        try {
            if (isTherapist) {
                await updateVisitStatus(id, "CANCELED")
            } else {
                await cancelVisit(id)
            }
            await load()
            void message.success("Wizyta została anulowana.")
        } catch (err) {
            void message.error(getApiErrorMessage(err, "Nie udało się anulować wizyty."))
        } finally {
            setUpdatingStatus(false)
        }
    }

    if (loading) return <Loading />

    if (error || !visit) {
        return (
            <Flex style={{ padding: 24 }}>
                <AppAlert title={error ?? "Nie znaleziono wizyty."} />
            </Flex>
        )
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24, maxWidth: 720, margin: "0 auto" }}>
            <Button type="link" onClick={() => { void navigate("/wizyty"); }} style={{ alignSelf: "flex-start" }}>
                ← Powrót do listy
            </Button>
            <VisitDetailCard
                visit={visit}
                role={role}
                notes={notes}
                onNotesChange={setNotes}
                onSaveNote={isTherapist ? () => { void handleSaveNote(); } : undefined}
                onComplete={isTherapist ? () => { void handleComplete(); } : undefined}
                onCancel={() => { void handleCancel(); }}
                savingNote={savingNote}
                updatingStatus={updatingStatus}
                canCancel={canCancel}
                canUpdateStatus={canComplete}
            />
        </Flex>
    )
}

export default VisitDetailPage
