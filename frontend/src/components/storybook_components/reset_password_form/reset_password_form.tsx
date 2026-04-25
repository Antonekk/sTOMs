import React from "react";
import { Button, Card, Form, Input } from "antd";

export interface ResetPasswordFormValues {
    new_password: string;
    re_new_password: string;
}

export interface ResetPasswordFormProps {
    onSubmit: (values: ResetPasswordFormValues) => void | Promise<void>;
    loading?: boolean;
}

const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({
    onSubmit,
    loading = false,
}) => {
    const [form] = Form.useForm<ResetPasswordFormValues>();

    return (
        <Card
            title="Ustaw nowe hasło"
            style={{ width: "100%", maxWidth: 600, margin: "0 auto" }}
        >
            <Form
                form={form}
                name="reset_password_form"
                layout="vertical"
                onFinish={(values) => {
                    void onSubmit(values);
                }}
            >
                <Form.Item
                    label="Nowe hasło"
                    name="new_password"
                    rules={[
                        {
                            required: true,
                            message: "Podaj nowe hasło",
                        },
                    ]}
                >
                    <Input.Password />
                </Form.Item>

                <Form.Item
                    label="Powtórz nowe hasło"
                    name="re_new_password"
                    dependencies={["new_password"]}
                    hasFeedback
                    rules={[
                        {
                            required: true,
                            message: "Powtórz nowe hasło",
                        },
                        ({ getFieldValue }: { getFieldValue: (name: string) => string }) => ({
                            validator(_: unknown, value: string) {
                                if (!value || getFieldValue("new_password") === value) {
                                    return Promise.resolve();
                                }
                                return Promise.reject(new Error("Hasła nie są takie same"));
                            },
                        }),
                    ]}
                >
                    <Input.Password />
                </Form.Item>

                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                        Zapisz hasło
                    </Button>
                </Form.Item>
            </Form>
        </Card>
    );
};

export default ResetPasswordForm;
