import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Flex, Alert } from "antd";
import axios from "axios";
import SignUpForm from "../components/storybook_components/sign_up_form/sign_up_form";
import type { SignUpFormValues } from "../components/storybook_components/sign_up_form/sign_up_form";
import {register} from "../api/auth";




// This component handles user registration
const Register: React.FC = () => {

    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    const onSubmit = async (values: SignUpFormValues) =>{
        if (submitting) return;
        setSubmitting(true);
        setError(null);


        try {
            // Adjust data to api schema
            const data = {
                ...values,
                date_of_birth: values.date_of_birth.format('YYYY-MM-DD')
            };
            await register(data);
            void navigate("/login");
        }
        catch (err){
            // Handle displaying server side errors
            if (axios.isAxiosError(err) && err.response?.data) {
                const data = err.response.data as Record<string, unknown>;
                const firstValue = Object.values(data)[0];
                setError(Array.isArray(firstValue) ? String(firstValue[0]) : String(firstValue));
            } else {
                setError("Proces rejestracji nie przebiegł pomyślnie. Spróbuj ponownie.");
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
            <SignUpForm onSubmit={onSubmit} />
        </Flex>

    )
}

export default Register;