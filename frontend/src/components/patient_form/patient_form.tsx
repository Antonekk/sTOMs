import React from "react";
import { Button, Card, DatePicker, Form, Input } from "antd";
import type { Dayjs } from "dayjs";
import dayjs from "dayjs";
import type { PatientWrite } from "../../types/patients";
import { ONLY_LETTERS_PATTERN } from "../../utils/validation";

export interface PatientFormValues {
    first_name: string;
    last_name: string;
    birthday: Dayjs;
}

export interface PatientFormProps {
    initialValues?: PatientWrite;
    submitLabel: string;
    submitting?: boolean;
    onSubmit: (values: PatientWrite) => void | Promise<void>;
}

const PatientForm: React.FC<PatientFormProps> = ({
    initialValues,
    submitLabel,
    submitting = false,
    onSubmit,
}) => {
    const [form] = Form.useForm<PatientFormValues>();

    const onFinish = (values: PatientFormValues) => {
        void onSubmit({
            first_name: values.first_name,
            last_name: values.last_name,
            birthday: values.birthday.format("YYYY-MM-DD"),
        });
    };

    return (
        <Card style={{ width: "100%", maxWidth: 600, margin: "0 auto" }}>
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                initialValues={
                    initialValues
                        ? {
                              ...initialValues,
                              birthday: dayjs(initialValues.birthday),
                          }
                        : undefined
                }
            >
                <Form.Item
                    label="Imię"
                    name="first_name"
                    rules={[
                        { required: true, message: "Podaj imię" },
                        {
                            pattern: ONLY_LETTERS_PATTERN,
                            message: "Pole może zawierać wyłącznie litery alfabetu",
                        },
                    ]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    label="Nazwisko"
                    name="last_name"
                    rules={[
                        { required: true, message: "Podaj nazwisko" },
                        {
                            pattern: ONLY_LETTERS_PATTERN,
                            message: "Pole może zawierać wyłącznie litery alfabetu",
                        },
                    ]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    label="Data urodzenia"
                    name="birthday"
                    rules={[{ required: true, message: "Podaj datę urodzenia" }]}
                >
                    <DatePicker
                        style={{ width: "100%" }}
                        maxDate={dayjs()}
                        minDate={dayjs().subtract(100, "year")}
                    />
                </Form.Item>

                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={submitting}>
                        {submitLabel}
                    </Button>
                </Form.Item>
            </Form>
        </Card>
    );
};

export default PatientForm;
