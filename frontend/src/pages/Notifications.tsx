import { Button, Flex, Typography, message } from "antd"
import AppAlert from "../components/app_alert/app_alert"
import { useCallback, useEffect, useState } from "react"
import {
    listNotifications,
    markAllNotificationsRead,
    markNotificationRead,
} from "../api/notifications"
import NotificationList from "../components/notification_list/notification_list"
import Loading from "../components/loading/loading"
import { useNotifications } from "../notifications/NotificationsProvider"
import { getApiErrorMessage } from "../utils/apiError"
import type { Notification } from "../types/notifications"

const { Title } = Typography

const PAGE_SIZE = 20

const Notifications: React.FC = () => {
    const { unreadCount, refreshUnreadCount } = useNotifications()
    const [notifications, setNotifications] = useState<Notification[]>([])
    const [total, setTotal] = useState(0)
    const [page, setPage] = useState(1)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [markingReadId, setMarkingReadId] = useState<string | null>(null)
    const [markingAllRead, setMarkingAllRead] = useState(false)

    const loadNotifications = useCallback(async (targetPage: number) => {
        setLoading(true)
        setError(null)
        try {
            const response = await listNotifications({
                page: targetPage,
                page_size: PAGE_SIZE,
            })
            setNotifications(response.data.results)
            setTotal(response.data.count)
            setPage(targetPage)
        } catch (err) {
            setError(getApiErrorMessage(err, "Nie udało się wczytać powiadomień."))
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        void loadNotifications(1)
    }, [loadNotifications])

    const handlePageChange = (nextPage: number) => {
        void loadNotifications(nextPage)
    }

    const handleMarkRead = async (id: string) => {
        setMarkingReadId(id)
        try {
            const response = await markNotificationRead(id)
            setNotifications((current) =>
                current.map((notification) =>
                    notification.id === id ? response.data : notification,
                ),
            )
            await refreshUnreadCount()
        } catch (err) {
            void message.error(getApiErrorMessage(err, "Nie udało się oznaczyć powiadomienia."))
        } finally {
            setMarkingReadId(null)
        }
    }

    const handleMarkAllRead = async () => {
        setMarkingAllRead(true)
        try {
            await markAllNotificationsRead()
            setNotifications((current) =>
                current.map((notification) => ({ ...notification, is_read: true })),
            )
            await refreshUnreadCount()
            void message.success("Wszystkie powiadomienia oznaczono jako przeczytane.")
        } catch (err) {
            void message.error(getApiErrorMessage(err, "Nie udało się oznaczyć powiadomień."))
        } finally {
            setMarkingAllRead(false)
        }
    }

    const hasUnread = unreadCount > 0

    if (loading && notifications.length === 0) {
        return <Loading />
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
            <Flex justify="space-between" align="center" wrap gap={12}>
                <Title level={2} style={{ margin: 0 }}>Powiadomienia</Title>
                {hasUnread && (
                    <Button loading={markingAllRead} onClick={() => { void handleMarkAllRead(); }}>
                        Oznacz wszystkie jako przeczytane
                    </Button>
                )}
            </Flex>

            {error && <AppAlert title={error} />}

            <NotificationList
                notifications={notifications}
                loading={loading}
                total={total}
                page={page}
                pageSize={PAGE_SIZE}
                onPageChange={handlePageChange}
                onMarkRead={(id) => { void handleMarkRead(id); }}
                markingReadId={markingReadId}
            />
        </Flex>
    )
}

export default Notifications
