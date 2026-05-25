import { Button, Card, Empty, List, Popconfirm, Space, Tag } from "antd";
import {
    ArrowLeftOutlined,
    EditOutlined,
    PlusOutlined,
    UndoOutlined,
} from "@ant-design/icons";
import type React from "react";
import type { Patient } from "../../types/patients";

export type PatientListVariant = "active" | "inactive";
export type PatientListAction = "delete" | "restore";

export interface PatientListProps {
    patients: Patient[];
    onNavigate: (path: string) => void;
    variant?: PatientListVariant;
    onAction?: (action: PatientListAction, patientId: string) => Promise<void>;
    patientId?: string | null;
}

const formatPatientName = (patient: Patient) =>
    `${patient.first_name} ${patient.last_name}`;

const formatBirthday = (birthday: string) =>
    birthday.split("-").reverse().join(".");

const PatientList: React.FC<PatientListProps> = ({
    patients,
    onNavigate,
    variant = "active",
    onAction,
    patientId = null,
}) => {
    const isInactiveList = variant === "inactive";

    return (
        <Card
            title={isInactiveList ? "Usunięte profile pacjentów" : "Pacjenci"}
            extra={
                isInactiveList ? (
                    <Button
                        icon={<ArrowLeftOutlined />}
                        onClick={() => { onNavigate("/profil"); }}
                    >
                        Powrót do profilu
                    </Button>
                ) : (
                    <Space>
                        <Button
                            icon={<UndoOutlined />}
                            onClick={() => { onNavigate("/pacjenci/przywroc"); }}
                        >
                            Przywróć usunięte
                        </Button>
                        <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            onClick={() => { onNavigate("/pacjenci/nowy"); }}
                        >
                            Dodaj pacjenta
                        </Button>
                    </Space>
                )
            }
        >
            {patients.length > 0 ? (
                <List
                    dataSource={patients}
                    renderItem={(patient) => (
                        <List.Item
                            actions={
                                isInactiveList
                                    ? [
                                          onAction ? (
                                              <Popconfirm
                                                  key="restore"
                                                  title="Przywrócić profil pacjenta?"
                                                  description="Profil zostanie ponownie widoczny na liście pacjentów."
                                                  okText="Przywróć"
                                                  cancelText="Anuluj"
                                                  onConfirm={() => {
                                                      void onAction("restore", patient.id);
                                                  }}
                                              >
                                                  <Button
                                                      type="link"
                                                      icon={<UndoOutlined />}
                                                      loading={patientId === patient.id}
                                                  >
                                                      Przywróć
                                                  </Button>
                                              </Popconfirm>
                                          ) : null,
                                      ].filter(Boolean)
                                    : [
                                          <Button
                                              key="edit"
                                              type="link"
                                              icon={<EditOutlined />}
                                              onClick={() => {
                                                  onNavigate(
                                                      `/pacjenci/${patient.id}/edycja`,
                                                  );
                                              }}
                                          >
                                              Edytuj
                                          </Button>,
                                          !patient.is_primary && onAction ? (
                                              <Popconfirm
                                                  key="delete"
                                                  title="Usunąć profil pacjenta?"
                                                  description="Profil zostanie ukryty, ale historia wizyt pozostanie zachowana."
                                                  okText="Usuń"
                                                  cancelText="Anuluj"
                                                  onConfirm={() => {
                                                      void onAction("delete", patient.id);
                                                  }}
                                              >
                                                  <Button
                                                      type="link"
                                                      danger
                                                      loading={patientId === patient.id}
                                                  >
                                                      Usuń
                                                  </Button>
                                              </Popconfirm>
                                          ) : null,
                                      ].filter(Boolean)
                            }
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
                <Empty
                    description={
                        isInactiveList
                            ? "Brak usuniętych profili pacjentów"
                            : "Brak przypisanych pacjentów"
                    }
                />
            )}
        </Card>
    );
};

export default PatientList;
