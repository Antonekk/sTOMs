export interface Notification {
    id: string
    title: string
    description: string
    creation_timestamp: string
    is_read: boolean
}

export interface PaginatedNotifications {
    count: number
    next: string | null
    previous: string | null
    results: Notification[]
}

export interface ListNotificationsParams {
    page?: number
    page_size?: number
}
