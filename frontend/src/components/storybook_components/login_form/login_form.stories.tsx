import type { Meta, StoryObj } from "@storybook/react";
import LoginForm from "./login_form";

const meta: Meta<typeof LoginForm> = {
  title: "Forms/LoginForm",
  component: LoginForm,
  tags: ['autodocs'],
  argTypes: {
    onSubmit: { action: "submit" },
  },
};

export default meta;

type Story = StoryObj<typeof LoginForm>;

export const Default: Story = {
  args: {
    onSubmit: (values) => {
      console.log("Submitted values:", values);
    },
  },
};
