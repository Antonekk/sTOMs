import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Alert, Flex, Typography } from "antd";
import PatientForm from "../components/storybook_components/patient_form/patient_form";
import { getPatient, updatePatient } from "../api/patients";
import { useAuthentication } from "../auth/AuthProvider";
import Loading from "../components/storybook_components/loading/loading";
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
                <Alert
                    type="error"
                    showIcon
                    title={error ?? "Nie znaleziono pacjenta"}
                />
            </Flex>
        );
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24 }}>
            <Title level={2}>Edycja pacjenta</Title>
            {error && (
                <Alert
                    title={error}
                    type="error"
                    showIcon
                    closable={{ closeIcon: true, onClose: () => { setError(null); } }}
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
    );
};

export default PatientEdit;
