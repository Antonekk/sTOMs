import type { Meta, StoryObj } from "@storybook/react";
import ActivateAccount from "./account_activation";

const meta: Meta<typeof ActivateAccount> = {
  component: ActivateAccount,
  title: "Auth/Activate",
};

export default meta;

type Story = StoryObj<typeof ActivateAccount>;

export const Success: Story = {
  args: {
    success: true,
    title: "Twoje konto zostało aktywowane!",
    subTitle: "Możesz się teraz zalogować za pomocą adresu email i hasła",
    onClick: () => {alert("Nawiguj do strony logowania")},
  },
};

export const Error: Story = {
  args: {
    success: false,
    title: "Proces aktywacji nie przebiegł pomyślnie.",
    subTitle: "Twój link aktywacyjny jest niepoprawny lub wygasł. Spróbuj ponownie.",
    onClick: () => {alert("Nawiguj do strony rejestracji")},
  },
};