import React from "react";
import {Card, Form, Input, Button} from 'antd';
import FormItem from "antd/es/form/FormItem";


export interface SignUpFormValues {
    name: string;
    surname: string;
    email: string;
    phone_number: string;
    password: string;
    repeat_password: string;
}

export interface SignUpFormProps {
    onSubmit: (values: SignUpFormValues) => void;
}


export const SignUpForm: React.FC<SignUpFormProps> = ({ onSubmit }) => {

    const [form] = Form.useForm<SignUpFormValues>();

    const onFinish = (values: SignUpFormValues) => {
        onSubmit(values);
    };

    return (
    <Card title="Rejestracja" style={{ maxWidth: 600 }}>
        <Form
            form={form}
            name="registration_form"
            layout="vertical"
            onFinish={onFinish}
        >
            <Form.Item
                label="Imię"
                name="name"
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
                name="surname"
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

            <FormItem
                label="Numer telefonu"
                name="phone_number"
                rules={[
                    {
                        required: true,
                        message: 'Podaj swój numer telefonu',
                    },
                ]}
            >
                <Input />
            </FormItem>

            <FormItem
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
            </FormItem>

            <FormItem
                label="Powtórz hasło"
                name="repeat_password"
                dependencies={['password']}
                hasFeedback
                rules={[
                    {
                        required: true,
                        message: 'Powtórz swoje hasło',
                    },
                    ({ getFieldValue }) => ({
                        validator(_, value) {
                            if (!value || getFieldValue('password') === value) {
                                return Promise.resolve();
                            }
                            return Promise.reject(new Error('Hasła nie są takie same'));
                        },
                    }),
                ]}
            >
                <Input.Password />
            </FormItem>

            <FormItem>
                <Button type="primary" htmlType="submit">
                    Zarejestruj się
                </Button>
            </FormItem>

        </Form>
    </Card>
    );
}