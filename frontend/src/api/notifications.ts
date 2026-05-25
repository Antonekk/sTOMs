import api from "./api"
import { NOTIFICATION_ENDPOINTS } from "./endpoints"
import type {
    ListNotificationsParams,
    Notification,
    PaginatedNotifications,
} from "../types/notifications"

export const listNotifications = (params?: ListNotificationsParams) =>
    api.get<PaginatedNotifications>(NOTIFICATION_ENDPOINTS.NOTIFICATIONS, { params })

export const getNotification = (id: string) =>
    api.get<Notification>(NOTIFICATION_ENDPOINTS.NOTIFICATION(id))

export const markNotificationRead = (id: string) =>
    api.patch<Notification>(NOTIFICATION_ENDPOINTS.NOTIFICATION_READ(id))

export const markAllNotificationsRead = () =>
    api.patch(NOTIFICATION_ENDPOINTS.NOTIFICATIONS_READ_ALL)
