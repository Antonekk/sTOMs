import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Flex, Typography } from "antd";
import AppAlert from "../components/storybook_components/app_alert/app_alert";
import { requestPasswordReset } from "../api/auth";
import ForgotPasswordForm from "../components/storybook_components/forgot_password_form/forgot_password_form";
import type { ForgotPasswordFormValues } from "../components/storybook_components/forgot_password_form/forgot_password_form";
import { getApiErrorMessage } from "../utils/apiError";

const ForgotPassword: React.FC = () => {
    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const onSubmit = async (values: ForgotPasswordFormValues) => {
        if (submitting) return;
        setSubmitting(true);
        setError(null);

        try {
            await requestPasswordReset(values);
            setSuccess(true);
        } catch (err) {
            setError(
                getApiErrorMessage(
                    err,
                    "Nie udało się wysłać linku do resetu hasła. Spróbuj ponownie.",
                ),
            );
        } finally {
            setSubmitting(false);
        }
    };

    if (success) {
        return (
            <Flex align="center" style={{ width: "100%", height: "100%" }} vertical gap="middle">
                <AppAlert
                    type="success"
                    title="Sprawdź skrzynkę e-mail"
                    description="Jeśli konto z podanym adresem istnieje, wysłaliśmy link do ustawienia nowego hasła."
                />
                <Typography.Link onClick={() => { void navigate("/login"); }}>
                    Wróć do logowania
                </Typography.Link>
            </Flex>
        );
    }

    return (
        <Flex align="center" style={{ width: "100%", height: "100%" }} vertical gap="middle">
            <div style={{ minHeight: 40, width: "100%", maxWidth: 600 }}>
                {error && (
                    <AppAlert
                        title={error}
                        onClose={() => { setError(null); }}
                    />
                )}
            </div>
            <ForgotPasswordForm onSubmit={onSubmit} loading={submitting} />
            <Typography.Text>
                <Link to="/login">Wróć do logowania</Link>
            </Typography.Text>
        </Flex>
    );
};

export default ForgotPassword;
