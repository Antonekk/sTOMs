import type { Meta, StoryObj } from "@storybook/react-vite";
import ForgotPasswordForm from "./forgot_password_form";

const meta: Meta<typeof ForgotPasswordForm> = {
    title: "Forms/ForgotPasswordForm",
    component: ForgotPasswordForm,
    tags: ["autodocs"],
    argTypes: {
        onSubmit: { action: "submit" },
    },
};

export default meta;

type Story = StoryObj<typeof ForgotPasswordForm>;

export const Default: Story = {
    args: {
        onSubmit: (values) => {
            console.log("Submitted values:", values);
        },
    },
};

export const Loading: Story = {
    args: {
        loading: true,
        onSubmit: (values) => {
            console.log("Submitted values:", values);
        },
    },
};
