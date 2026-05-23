import { Badge, Button, Card, Empty, List, Space, Typography } from "antd"
import type React from "react"
import type { Notification } from "../../types/notifications"
import { formatDateTimePl } from "../../utils/timeSlots"

const { Text, Paragraph } = Typography

export interface NotificationListProps {
    notifications: Notification[]
    loading?: boolean
    total: number
    page: number
    pageSize: number
    onPageChange: (page: number, pageSize: number) => void
    onMarkRead?: (id: string) => void
    markingReadId?: string | null
}

const NotificationList: React.FC<NotificationListProps> = ({
    notifications,
    loading = false,
    total,
    page,
    pageSize,
    onPageChange,
    onMarkRead,
    markingReadId,
}) => {
    return (
        <Card>
            <List
                itemLayout="vertical"
                loading={loading}
                dataSource={notifications}
                locale={{ emptyText: <Empty description="Brak powiadomień" /> }}
                pagination={{
                    current: page,
                    pageSize,
                    total,
                    hideOnSinglePage: true,
                    showSizeChanger: false,
                    onChange: onPageChange,
                }}
                renderItem={(notification) => (
                    <List.Item
                        style={{
                            opacity: notification.is_read ? 0.75 : 1,
                            background: notification.is_read ? undefined : "rgba(22, 119, 255, 0.04)",
                            borderRadius: 8,
                            paddingInline: 12,
                        }}
                        actions={
                            !notification.is_read && onMarkRead
                                ? [
                                    <Button
                                        key="read"
                                        type="link"
                                        loading={markingReadId === notification.id}
                                        onClick={() => { onMarkRead(notification.id); }}
                                    >
                                        Oznacz jako przeczytane
                                    </Button>,
                                ]
                                : undefined
                        }
                    >
                        <List.Item.Meta
                            title={(
                                <Space>
                                    {!notification.is_read && <Badge status="processing" />}
                                    <Text strong={!notification.is_read}>{notification.title}</Text>
                                </Space>
                            )}
                            description={(
                                <Space orientation="vertical" size={4} style={{ width: "100%" }}>
                                    <Paragraph style={{ marginBottom: 0, whiteSpace: "pre-wrap" }}>
                                        {notification.description}
                                    </Paragraph>
                                    <Text type="secondary">
                                        {formatDateTimePl(notification.creation_timestamp)}
                                    </Text>
                                </Space>
                            )}
                        />
                    </List.Item>
                )}
            />
        </Card>
    )
}

export default NotificationList
