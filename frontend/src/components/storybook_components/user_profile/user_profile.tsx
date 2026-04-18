import { Card, Space, Typography } from "antd";
import { UserOutlined } from "@ant-design/icons";
import type React from "react";
import type { User } from "../../../types/auth";
import AccountDetails from "./account_details";
import PatientList from "./patient_list";

const { Text, Title } = Typography;

export interface UserProfileProps {
    user: User;
    onNavigate: (path: string) => void;
    onDeletePatient?: (patientId: string) => Promise<void>;
    deletingPatientId?: string | null;
}

const UserProfile: React.FC<UserProfileProps> = ({
    user,
    onNavigate,
    onDeletePatient,
    deletingPatientId,
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
                onDeletePatient={onDeletePatient}
                deletingPatientId={deletingPatientId}
            />
        )}
    </Space>
);

export default UserProfile;
