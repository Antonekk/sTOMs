import React from "react";
import {Card, Form, Input, Button} from 'antd';


export interface LoginFormValues {
    email: string;
    password: string;
}

export interface LoginFormProps {
    onSubmit: (values: LoginFormValues) => void | Promise<void>;
}


const SignUpForm: React.FC<LoginFormProps> = ({ onSubmit }) => {

    const [form] = Form.useForm<LoginFormValues>();

    const onFinish = (values: LoginFormValues) => {
        void onSubmit(values);
    };

    return (
    <Card title="Lowowanie" style={{ width: '100%', maxWidth: 600, margin: '0 auto' }}>
        <Form
            form={form}
            name="registration_form"
            layout="vertical"
            onFinish={onFinish}
        >  
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


            <Form.Item>
                <Button type="primary" htmlType="submit">
                    Zaloguj się
                </Button>
            </Form.Item>

        </Form>
    </Card>
    );
}

export default SignUpForm;