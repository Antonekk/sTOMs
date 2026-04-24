import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useState,
    type ReactNode,
} from "react"
import { listNotifications } from "../api/notifications"
import { useAuthentication } from "../auth/AuthProvider"

interface NotificationsContextValue {
    unreadCount: number
    refreshUnreadCount: () => Promise<void>
}

const NotificationsContext = createContext<NotificationsContextValue | null>(null)

export const NotificationsProvider = ({ children }: { children: ReactNode }) => {
    const { isAuthenticated } = useAuthentication()
    const [unreadCount, setUnreadCount] = useState(0)

    const refreshUnreadCount = useCallback(async () => {
        if (!isAuthenticated) {
            setUnreadCount(0)
            return
        }

        try {
            const response = await listNotifications({ page_size: 50 })
            const unread = response.data.results.filter((notification) => !notification.is_read).length
            setUnreadCount(unread)
        } catch {
            setUnreadCount(0)
        }
    }, [isAuthenticated])

    useEffect(() => {
        void refreshUnreadCount()
    }, [refreshUnreadCount])

    useEffect(() => {
        const handleFocus = () => {
            void refreshUnreadCount()
        }
        window.addEventListener("focus", handleFocus)
        return () => {
            window.removeEventListener("focus", handleFocus)
        }
    }, [refreshUnreadCount])

    const value = useMemo(
        () => ({ unreadCount, refreshUnreadCount }),
        [unreadCount, refreshUnreadCount],
    )

    return (
        <NotificationsContext.Provider value={value}>
            {children}
        </NotificationsContext.Provider>
    )
}

export const useNotifications = (): NotificationsContextValue => {
    const context = useContext(NotificationsContext)
    if (!context) {
        throw new Error("useNotifications must be used within NotificationsProvider")
    }
    return context
}
