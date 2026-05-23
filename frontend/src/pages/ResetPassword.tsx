import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Flex } from "antd";
import AppAlert from "../components/app_alert/app_alert";
import { confirmPasswordReset } from "../api/auth";
import AccountActivation from "../components/account_activation/account_activation";
import ResetPasswordForm from "../components/reset_password_form/reset_password_form";
import type { ResetPasswordFormValues } from "../components/reset_password_form/reset_password_form";
import { getApiErrorMessage } from "../utils/apiError";

const ResetPassword: React.FC = () => {
    const { uid, token } = useParams();
    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const onSubmit = async (values: ResetPasswordFormValues) => {
        if (!uid || !token || submitting) return;
        setSubmitting(true);
        setError(null);

        try {
            await confirmPasswordReset({
                uid,
                token,
                new_password: values.new_password,
                re_new_password: values.re_new_password,
            });
            setSuccess(true);
        } catch (err) {
            setError(
                getApiErrorMessage(
                    err,
                    "Nie udało się ustawić nowego hasła. Link mógł wygasnąć.",
                ),
            );
        } finally {
            setSubmitting(false);
        }
    };

    if (!uid || !token) {
        return (
            <AccountActivation
                success={false}
                title="Nieprawidłowy link"
                subTitle="Link do resetu hasła jest niekompletny. Poproś o nowy link z formularza przypomnienia hasła."
                onClick={() => { void navigate("/haslo/reset"); }}
                buttonLabel="Poproś o nowy link"
            />
        );
    }

    if (success) {
        return (
            <AccountActivation
                success
                title="Hasło zostało zmienione"
                subTitle="Możesz się teraz zalogować, używając nowego hasła."
                onClick={() => { void navigate("/login"); }}
            />
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
            <ResetPasswordForm onSubmit={onSubmit} loading={submitting} />
        </Flex>
    );
};

export default ResetPassword;
