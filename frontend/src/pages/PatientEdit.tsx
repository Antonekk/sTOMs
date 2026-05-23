import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Flex, Typography } from "antd";
import AppAlert from "../components/app_alert/app_alert";
import PatientForm from "../components/patient_form/patient_form";
import { getPatient, updatePatient } from "../api/patients";
import { useAuthentication } from "../auth/AuthProvider";
import Loading from "../components/loading/loading";
import { getApiErrorMessage } from "../utils/apiError";
import type { Patient, PatientWrite } from "../types/patients";

const { Title } = Typography;

const PatientEdit: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { refreshUser } = useAuthentication();
    const [patient, setPatient] = useState<Patient | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        if (!id) {
            setLoading(false);
            return;
        }

        const fetchPatient = async () => {
            try {
                const response = await getPatient(id);
                setPatient(response.data);
            } catch (err) {
                setError(
                    getApiErrorMessage(err, "Nie udało się wczytać danych pacjenta."),
                );
            } finally {
                setLoading(false);
            }
        };

        void fetchPatient();
    }, [id]);

    const onSubmit = async (values: PatientWrite) => {
        if (!id || submitting) return;
        setSubmitting(true);
        setError(null);

        try {
            await updatePatient(id, values);
            await refreshUser();
            void navigate("/profil");
        } catch (err) {
            setError(
                getApiErrorMessage(err, "Nie udało się zapisać zmian. Spróbuj ponownie."),
            );
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return <Loading />;
    }

    if (!patient) {
        return (
            <Flex justify="center" style={{ padding: 24 }}>
                <AppAlert title={error ?? "Nie znaleziono pacjenta"} />
            </Flex>
        );
    }

    return (
        <Flex justify="center" style={{ padding: 24 }}>
            <Flex
                vertical
                gap={16}
                align="center"
                style={{ width: "100%", maxWidth: 600 }}
            >
                <Title level={2} style={{ margin: 0, textAlign: "center" }}>
                    Edycja pacjenta
                </Title>
                {error && (
                    <AppAlert
                        title={error}
                        style={{ width: "100%" }}
                        onClose={() => { setError(null); }}
                    />
                )}
                <PatientForm
                    initialValues={{
                        first_name: patient.first_name,
                        last_name: patient.last_name,
                        birthday: patient.birthday,
                    }}
                    submitLabel="Zapisz zmiany"
                    submitting={submitting}
                    onSubmit={onSubmit}
                />
            </Flex>
        </Flex>
    );
};

export default PatientEdit;
