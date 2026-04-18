import { Button, Card, Empty, List, Popconfirm, Space, Tag } from "antd";
import { EditOutlined, PlusOutlined } from "@ant-design/icons";
import type React from "react";
import type { Patient } from "../../../types/patients";

export interface PatientListProps {
    patients: Patient[];
    onNavigate: (path: string) => void;
    onDeletePatient?: (patientId: string) => Promise<void>;
    deletingPatientId?: string | null;
}

const formatPatientName = (patient: Patient) =>
    `${patient.first_name} ${patient.last_name}`;

const formatBirthday = (birthday: string) =>
    birthday.split("-").reverse().join(".");

const PatientList: React.FC<PatientListProps> = ({
    patients,
    onNavigate,
    onDeletePatient,
    deletingPatientId = null,
}) => {
    return (
        <Card
            title="Pacjenci"
            extra={
                <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => { onNavigate("/pacjenci/nowy"); }}
                >
                    Dodaj pacjenta
                </Button>
            }
        >
            {patients.length > 0 ? (
                <List
                    dataSource={patients}
                    renderItem={(patient) => (
                        <List.Item
                            actions={[
                                <Button
                                    key="edit"
                                    type="link"
                                    icon={<EditOutlined />}
                                    onClick={() => {
                                        onNavigate(`/pacjenci/${patient.id}/edycja`);
                                    }}
                                >
                                    Edytuj
                                </Button>,
                                !patient.is_primary && onDeletePatient ? (
                                    <Popconfirm
                                        key="delete"
                                        title="Usunąć profil pacjenta?"
                                        description="Profil zostanie ukryty, ale historia wizyt pozostanie zachowana."
                                        okText="Usuń"
                                        cancelText="Anuluj"
                                        onConfirm={() => onDeletePatient(patient.id)}
                                    >
                                        <Button
                                            type="link"
                                            danger
                                            loading={deletingPatientId === patient.id}
                                        >
                                            Usuń
                                        </Button>
                                    </Popconfirm>
                                ) : null,
                            ].filter(Boolean)}
                        >
                            <List.Item.Meta
                                title={
                                    <Space>
                                        <span>{formatPatientName(patient)}</span>
                                        {patient.is_primary && (
                                            <Tag color="gold">Główny</Tag>
                                        )}
                                    </Space>
                                }
                                description={`Data urodzenia: ${formatBirthday(patient.birthday)}`}
                            />
                        </List.Item>
                    )}
                />
            ) : (
                <Empty description="Brak przypisanych pacjentów" />
            )}
        </Card>
    );
};

export default PatientList;
