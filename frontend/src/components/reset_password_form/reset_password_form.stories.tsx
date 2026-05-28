import type { Meta, StoryObj } from "@storybook/react-vite";
import ResetPasswordForm from "./reset_password_form";

const meta: Meta<typeof ResetPasswordForm> = {
    title: "Forms/ResetPasswordForm",
    component: ResetPasswordForm,
    tags: ["autodocs"],
    argTypes: {
        onSubmit: { action: "submit" },
    },
};

export default meta;

type Story = StoryObj<typeof ResetPasswordForm>;

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
