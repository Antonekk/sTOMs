import { Card, Space, Typography } from "antd";
import { UserOutlined } from "@ant-design/icons";
import type React from "react";
import type { User } from "../../types/auth";
import AccountDetails from "./account_details";
import PatientList, { type PatientListAction } from "./patient_list";

const { Text, Title } = Typography;

export interface UserProfileProps {
    user: User;
    onNavigate: (path: string) => void;
    onAction?: (action: PatientListAction, patientId: string) => Promise<void>;
    patientId?: string | null;
}

const UserProfile: React.FC<UserProfileProps> = ({
    user,
    onNavigate,
    onAction,
    patientId,
}) => (
    <Space orientation="vertical" size="large" style={{ width: "100%" }}>
        <Card>
            <Space align="center" size="middle">
                <UserOutlined style={{ fontSize: 40 }} />
                <div>
                    <Title level={2} style={{ margin: 0 }}>
                        Profil użytkownika
                    </Title>
                    <Text type="secondary">{user.email}</Text>
                </div>
            </Space>
        </Card>

        <AccountDetails user={user} />
        {user.role === "CLIENT" && (
            <PatientList
                patients={user.patients}
                onNavigate={onNavigate}
                onAction={onAction}
                patientId={patientId}
            />
        )}
    </Space>
);

export default UserProfile;
