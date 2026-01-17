import React from "react";
import {Card, Form, Input, Button, DatePicker} from 'antd';
import type { Dayjs } from 'dayjs';


export interface SignUpFormValues {
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    password: string;
    date_of_birth: Dayjs;
    re_password: string;
}

export interface SignUpFormProps {
    onSubmit: (values: SignUpFormValues) => void | Promise<void>;
}


export const SignUpForm: React.FC<SignUpFormProps> = ({ onSubmit }) => {

    const [form] = Form.useForm<SignUpFormValues>();

    const onFinish = (values: SignUpFormValues) => {
        void onSubmit(values);
    };

    return (
    <Card title="Rejestracja" style={{ width: '100%', maxWidth: 600 }}>
        <Form
            form={form}
            name="registration_form"
            layout="vertical"
            onFinish={onFinish}
        >
            <Form.Item
                label="Imię"
                name="first_name"
                rules={[
                    {
                        required: true,
                        message: 'Podaj swoje imię',
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item
                label="Nazwisko"
                name="last_name"
                rules={[
                    {
                        required: true,
                        message: 'Podaj swoje nazwisko',
                    },
                ]}
            >
                <Input />
            </Form.Item>
            
            <Form.Item
                label="E-mail"
                name="email"
                rules={[
                    {
                        type: 'email',
                        message: 'Podaj poprawny adres e-mail',
                    },
                    {
                        required: true,
                        message: 'Podaj swój adres e-mail',
                    },
                ]}
            >
                <Input />
            </Form.Item>

            <Form.Item
                label="Numer telefonu"
                name="phone_number"
                rules={[
                    {
                        required: true,
                        message: 'Podaj swój numer telefonu',
                    },
                    {
                        pattern: /^(?:\+48)?\d{9}$/,
                        message: 'Podaj poprawny numer telefonu',
                    },
                ]}
            >
                <Input />
            </Form.Item>

            <Form.Item
                label="Data urodzenia"
                name="date_of_birth"
                rules={[
                    {
                        required: true,
                        message: 'Podaj swoją datę urodzenia',
                    },
                ]}
            >
                <DatePicker style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
                label="Hasło"
                name="password"
                rules={[
                    {
                        required: true,
                        message: 'Podaj swoje hasło',
                    },
                ]}
            >
                <Input.Password />
            </Form.Item>

            <Form.Item
                label="Powtórz hasło"
                name="re_password"
                dependencies={['password']}
                hasFeedback
                rules={[
                    {
                        required: true,
                        message: 'Powtórz swoje hasło',
                    },
                    ({ getFieldValue }: { getFieldValue: (name: string) => string }) => ({
                        validator(_: unknown, value: string) {
                            if (!value || getFieldValue('password') === value) {
                                return Promise.resolve();
                            }
                            return Promise.reject(new Error('Hasła nie są takie same'));
                        },
                    }),
                ]}
            >
                <Input.Password />
            </Form.Item>

            <Form.Item>
                <Button type="primary" htmlType="submit">
                    Zarejestruj się
                </Button>
            </Form.Item>

        </Form>
    </Card>
    );
}