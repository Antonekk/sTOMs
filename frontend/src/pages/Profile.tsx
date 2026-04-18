import { Alert, Flex, message } from "antd";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import UserProfile from "../components/storybook_components/user_profile/user_profile";
import { useAuthentication } from "../auth/AuthProvider";
import { deletePatient } from "../api/patients";
import { getApiErrorMessage } from "../utils/apiError";

const Profile: React.FC = () => {
    const navigate = useNavigate();
    const { user, refreshUser } = useAuthentication();
    const [deletingPatientId, setDeletingPatientId] = useState<string | null>(null);

    const handleDeletePatient = async (patientId: string) => {
        setDeletingPatientId(patientId);
        try {
            await deletePatient(patientId);
            await refreshUser();
            void message.success("Profil pacjenta został usunięty");
        } catch (err) {
            void message.error(
                getApiErrorMessage(err, "Nie udało się usunąć profilu pacjenta."),
            );
        } finally {
            setDeletingPatientId(null);
        }
    };

    if (!user) {
        return (
            <Flex justify="center" style={{ padding: 24 }}>
                <Alert
                    type="warning"
                    showIcon
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
                    onDeletePatient={handleDeletePatient}
                    deletingPatientId={deletingPatientId}
                />
            </div>
        </Flex>
    );
};

export default Profile;
