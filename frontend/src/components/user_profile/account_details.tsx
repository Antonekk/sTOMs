import { Card, Descriptions, Tag } from "antd";
import type { DescriptionsProps } from "antd";
import type React from "react";
import type { Role, User } from "../../types/auth";

const roleLabels: Record<Role, string> = {
    ADMIN: "Administrator",
    CLIENT: "Klient",
    THERAPIST: "Terapeuta",
};

const roleColors: Record<Role, string> = {
    ADMIN: "red",
    CLIENT: "blue",
    THERAPIST: "green",
};

export interface AccountDetailsProps {
    user: User;
}

const AccountDetails: React.FC<AccountDetailsProps> = ({ user }) => {
    const personalDetails: DescriptionsProps["items"] = [
        {
            key: "full_name",
            label: "Imię i nazwisko",
            children: `${user.first_name} ${user.last_name}`,
        },
        {
            key: "email",
            label: "E-mail",
            children: user.email,
        },
        {
            key: "phone_number",
            label: "Numer telefonu",
            children: user.phone_number,
        },
        {
            key: "role",
            label: "Rola",
            children: <Tag color={roleColors[user.role]}>{roleLabels[user.role]}</Tag>,
        },
    ];

    return (
        <Card title="Dane konta">
            <Descriptions bordered column={{ xs: 1, sm: 1, md: 2 }} items={personalDetails} />
        </Card>
    );
};

export default AccountDetails;
