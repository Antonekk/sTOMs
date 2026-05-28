import type { Meta, StoryObj } from "@storybook/react-vite";
import OfficeLocationDisplay from "./office_location";
import type { OfficeLocation } from "../../types/reservations";

const meta: Meta<typeof OfficeLocationDisplay> = {
    title: "Components/OfficeLocation",
    component: OfficeLocationDisplay,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

const mockOffice: OfficeLocation = {
    name: "Centrum Terapii",
    city: "Warszawa",
    address: "ul. Przykładowa 1",
    postal_code: "00-001",
    room_number: "12",
};

export const Default: Story = {
    args: {
        office: mockOffice,
    },
};

export const Compact: Story = {
    args: {
        office: mockOffice,
        compact: true,
    },
};

export const WithoutRoom: Story = {
    args: {
        office: {
            ...mockOffice,
            room_number: null,
        },
    },
};

export const Empty: Story = {
    args: {
        office: null,
    },
};
