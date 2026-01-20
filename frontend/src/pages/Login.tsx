import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Flex, Alert } from "antd";
import axios from "axios";
import LoginForm from "../components/storybook_components/login_form/login_form";
import type { LoginFormValues } from "../components/storybook_components/login_form/login_form";
import { useAuthentication } from "../auth/AuthProvider";


const Login: React.FC = () => {
    const {login} = useAuthentication();
    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);


const onSubmit = async (values: LoginFormValues) =>{
        if (submitting) return;
        setSubmitting(true);
        setError(null);


        try {
            await login(values);
            void navigate("/panel");
        }
        catch (err){
            // Handle displaying server side errors
            if (axios.isAxiosError(err) && err.response?.data) {
                const data = err.response.data as Record<string, unknown>;
                const firstValue = Object.values(data)[0];
                setError(Array.isArray(firstValue) ? String(firstValue[0]) : String(firstValue));
            } else {
                setError("Proces logowania nie przebiegł pomyślnie. Spróbuj ponownie.");
            }
        }
        finally{
            setSubmitting(false);
        }
    }


    return (

        <Flex align="center" style={{ width: '100%', height: '100%' }} vertical gap="middle">
            <div style={{ minHeight: 40 }}>
                {error && <Alert title={error} type="error" showIcon closable={{ closeIcon: true, onClose: () => { setError(null); } }} />}
            </div>
            <LoginForm onSubmit={onSubmit} />
        </Flex>

    )
}

export default Login;