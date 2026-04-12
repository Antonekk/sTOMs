import { Card, Empty, List, Space, Tag } from "antd";
import type React from "react";
import type { Patient } from "../../../types/auth";

export interface PatientListProps {
    patients: Patient[];
}

const formatPatientName = (patient: Patient) => `${patient.first_name} ${patient.last_name}`;

const PatientList: React.FC<PatientListProps> = ({ patients }) => {
    return (
        <Card title="Pacjenci">
            {patients.length > 0 ? (
                <List
                    dataSource={patients}
                    renderItem={(patient) => (
                        <List.Item>
                            <List.Item.Meta
                                title={
                                    <Space>
                                        <span>{formatPatientName(patient)}</span>
                                        {patient.is_primary && <Tag color="gold">Główny</Tag>}
                                    </Space>
                                }
                                description={`Data urodzenia: ${patient.date_of_birth}`}
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
