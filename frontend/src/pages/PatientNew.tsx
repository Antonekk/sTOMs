import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Alert, Flex, Typography } from "antd";
import PatientForm from "../components/storybook_components/patient_form/patient_form";
import { createPatient } from "../api/patients";
import { useAuthentication } from "../auth/AuthProvider";
import { getApiErrorMessage } from "../utils/apiError";
import type { PatientWrite } from "../types/patients";

const { Title } = Typography;

const PatientNew: React.FC = () => {
    const navigate = useNavigate();
    const { refreshUser } = useAuthentication();
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    const onSubmit = async (values: PatientWrite) => {
        if (submitting) return;
        setSubmitting(true);
        setError(null);

        try {
            await createPatient(values);
            await refreshUser();
            void navigate("/profil");
        } catch (err) {
            setError(
                getApiErrorMessage(err, "Nie udało się dodać pacjenta. Spróbuj ponownie."),
            );
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Flex vertical gap={16} style={{ padding: 24 }}>
            <Title level={2}>Nowy pacjent</Title>
            {error && (
                <Alert
                    title={error}
                    type="error"
                    showIcon
                    closable={{ closeIcon: true, onClose: () => { setError(null); } }}
                />
            )}
            <PatientForm
                submitLabel="Dodaj pacjenta"
                submitting={submitting}
                onSubmit={onSubmit}
            />
        </Flex>
    );
};

export default PatientNew;
