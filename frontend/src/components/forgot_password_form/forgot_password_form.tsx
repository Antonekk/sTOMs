import React from "react";
import { Button, Card, Form, Input } from "antd";

export interface ForgotPasswordFormValues {
    email: string;
}

export interface ForgotPasswordFormProps {
    onSubmit: (values: ForgotPasswordFormValues) => void | Promise<void>;
    loading?: boolean;
}

const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({
    onSubmit,
    loading = false,
}) => {
    const [form] = Form.useForm<ForgotPasswordFormValues>();

    return (
        <Card
            title="Przypomnienie hasła"
            style={{ width: "100%", maxWidth: 600, margin: "0 auto" }}
        >
            <Form
                form={form}
                name="forgot_password_form"
                layout="vertical"
                onFinish={(values) => {
                    void onSubmit(values);
                }}
            >
                <Form.Item
                    label="E-mail"
                    name="email"
                    rules={[
                        {
                            type: "email",
                            message: "Podaj poprawny adres e-mail",
                        },
                        {
                            required: true,
                            message: "Podaj swój adres e-mail",
                        },
                    ]}
                >
                    <Input />
                </Form.Item>

                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                        Wyślij link do resetu hasła
                    </Button>
                </Form.Item>
            </Form>
        </Card>
    );
};

export default ForgotPasswordForm;
