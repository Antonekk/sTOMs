import { Flex, message } from "antd";
import AppAlert from "../components/app_alert/app_alert";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import UserProfile from "../components/user_profile/user_profile";
import type { PatientListAction } from "../components/user_profile/patient_list";
import { useAuthentication } from "../auth/AuthProvider";
import { deletePatient } from "../api/patients";
import { getApiErrorMessage } from "../utils/apiError";

const Profile: React.FC = () => {
    const navigate = useNavigate();
    const { user, refreshUser } = useAuthentication();
    const [actionPatientId, setActionPatientId] = useState<string | null>(null);

    const handleAction = async (action: PatientListAction, patientId: string) => {
        if (action !== "delete") return;
        setActionPatientId(patientId);
        try {
            await deletePatient(patientId);
            await refreshUser();
            void message.success("Profil pacjenta został usunięty");
        } catch (err) {
            void message.error(
                getApiErrorMessage(err, "Nie udało się usunąć profilu pacjenta."),
            );
        } finally {
            setActionPatientId(null);
        }
    };

    if (!user) {
        return (
            <Flex justify="center" style={{ padding: 24 }}>
                <AppAlert
                    type="warning"
                    title="Nie udało się wczytać danych profilu"
                />
            </Flex>
        );
    }

    return (
        <Flex justify="center" style={{ padding: 24 }}>
            <div style={{ width: "100%", maxWidth: 960 }}>
                <UserProfile
                    user={user}
                    onNavigate={(path) => { void navigate(path); }}
                    onAction={handleAction}
                    patientId={actionPatientId}
                />
            </div>
        </Flex>
    );
};

export default Profile;
