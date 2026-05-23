import { Flex, Spin, message } from "antd";
import AppAlert from "../components/app_alert/app_alert";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import PatientList, { type PatientListAction } from "../components/user_profile/patient_list";
import { listPatients, restorePatient } from "../api/patients";
import { useAuthentication } from "../auth/AuthProvider";
import { getApiErrorMessage } from "../utils/apiError";
import type { Patient } from "../types/patients";

const PatientRestore: React.FC = () => {
    const navigate = useNavigate();
    const { refreshUser } = useAuthentication();
    const [patients, setPatients] = useState<Patient[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);
    const [actionPatientId, setActionPatientId] = useState<string | null>(null);

    const loadInactivePatients = useCallback(async () => {
        setLoading(true);
        setLoadError(null);
        try {
            const response = await listPatients({ is_active: false });
            setPatients(response.data);
        } catch (err) {
            setLoadError(
                getApiErrorMessage(
                    err,
                    "Nie udało się wczytać usuniętych profili pacjentów.",
                ),
            );
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadInactivePatients();
    }, [loadInactivePatients]);

    const handleAction = async (action: PatientListAction, patientId: string) => {
        if (action !== "restore") return;
        setActionPatientId(patientId);
        try {
            await restorePatient(patientId);
            await refreshUser();
            await loadInactivePatients();
            void message.success("Profil pacjenta został przywrócony");
        } catch (err) {
            void message.error(
                getApiErrorMessage(err, "Nie udało się przywrócić profilu pacjenta."),
            );
        } finally {
            setActionPatientId(null);
        }
    };

    if (loading) {
        return (
            <Flex justify="center" style={{ padding: 48 }}>
                <Spin size="large" />
            </Flex>
        );
    }

    return (
        <Flex justify="center" style={{ padding: 24 }}>
            <div style={{ width: "100%", maxWidth: 960 }}>
                {loadError && (
                    <AppAlert
                        title={loadError}
                        style={{ marginBottom: 16 }}
                    />
                )}
                <PatientList
                    patients={patients}
                    variant="inactive"
                    onNavigate={(path) => { void navigate(path); }}
                    onAction={handleAction}
                    patientId={actionPatientId}
                />
            </div>
        </Flex>
    );
};

export default PatientRestore;
