import type { Meta, StoryObj } from "@storybook/react";
import { SignUpForm } from "./sign_up_form";

const meta: Meta<typeof SignUpForm> = {
  title: "Forms/SignUpForm",
  component: SignUpForm,
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof SignUpForm>;

export const Default: Story = {
  args: {
    onSubmit: (values) => {
      console.log("Submitted values:", values);
    },
  },
};
