import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import NotificationList from "./notification_list";
import type { Notification } from "../../types/notifications";

const meta: Meta<typeof NotificationList> = {
    title: "Components/NotificationList",
    component: NotificationList,
    tags: ["autodocs"],
    argTypes: {
        onPageChange: { action: "pageChange" },
        onMarkRead: { action: "markRead" },
    },
};

export default meta;

type Story = StoryObj<typeof meta>;

const mockNotifications: Notification[] = [
    {
        id: "notif-1",
        title: "Nowa wizyta",
        description: "Zarezerwowano wizytę na 10.06.2026 o godz. 09:00.",
        creation_timestamp: "2026-06-08T10:30:00+02:00",
        is_read: false,
    },
    {
        id: "notif-2",
        title: "Przypomnienie",
        description: "Twoja wizyta odbędzie się jutro o godz. 14:00.",
        creation_timestamp: "2026-06-07T18:00:00+02:00",
        is_read: false,
    },
    {
        id: "notif-3",
        title: "Wizyta anulowana",
        description: "Wizyta z dnia 20.05.2026 została anulowana.",
        creation_timestamp: "2026-05-19T09:15:00+02:00",
        is_read: true,
    },
];

const NotificationListWithState = ({
    notifications = mockNotifications,
    total = mockNotifications.length,
    markingReadId = null,
}: {
    notifications?: Notification[];
    total?: number;
    markingReadId?: string | null;
}) => {
    const [page, setPage] = useState(1);
    const pageSize = 10;

    return (
        <NotificationList
            notifications={notifications}
            total={total}
            page={page}
            pageSize={pageSize}
            markingReadId={markingReadId}
            onPageChange={(nextPage) => {
                setPage(nextPage);
            }}
            onMarkRead={(id) => {
                console.log("Mark read:", id);
            }}
        />
    );
};

export const Default: Story = {
    render: () => <NotificationListWithState />,
};

export const Empty: Story = {
    render: () => <NotificationListWithState notifications={[]} total={0} />,
};

export const Loading: Story = {
    args: {
        notifications: [],
        total: 0,
        page: 1,
        pageSize: 10,
        loading: true,
        onPageChange: () => {},
    },
};

export const MarkingRead: Story = {
    render: () => <NotificationListWithState markingReadId="notif-1" />,
};
