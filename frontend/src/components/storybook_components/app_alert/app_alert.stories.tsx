import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import AppAlert from "./app_alert";

const meta: Meta<typeof AppAlert> = {
    title: "Components/AppAlert",
    component: AppAlert,
    tags: ["autodocs"],
    argTypes: {
        onClose: { action: "close" },
    },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Error: Story = {
    args: {
        title: "Nie udało się wczytać danych.",
    },
};

export const ErrorWithDescription: Story = {
    args: {
        title: "Nie udało się zarezerwować terminu",
        description: "Wybrany slot jest już zajęty. Wybierz inny termin.",
    },
};

export const Success: Story = {
    args: {
        type: "success",
        title: "Sprawdź skrzynkę e-mail",
        description: "Jeśli konto z podanym adresem istnieje, wysłaliśmy link do ustawienia nowego hasła.",
    },
};

export const Warning: Story = {
    args: {
        type: "warning",
        title: "Nie udało się wczytać danych profilu",
    },
};

export const Info: Story = {
    args: {
        type: "info",
        title: "Anulowanie możliwe najpóźniej 24 godzin przed wizytą.",
    },
};

export const Closable: Story = {
    args: {
        title: "Proces logowania nie przebiegł pomyślnie. Spróbuj ponownie.",
        onClose: fn(),
    },
};
