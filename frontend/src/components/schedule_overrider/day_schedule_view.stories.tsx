import type { Meta, StoryObj } from "@storybook/react-vite";
import DayScheduleView from "./day_schedule_view";
import type { BaseBlock, ScheduleOverride } from "./types";

const meta: Meta<typeof DayScheduleView> = {
    title: "Components/ScheduleOverrider/DayScheduleView",
    component: DayScheduleView,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

const MOCK_BASE_BLOCKS: BaseBlock[] = [
    { dayOfWeek: 0, startTime: "08:00", endTime: "12:00" },
    { dayOfWeek: 0, startTime: "13:00", endTime: "16:00" },
    { dayOfWeek: 1, startTime: "09:00", endTime: "17:00" },
];

const MOCK_OVERRIDES: ScheduleOverride[] = [
    {
        id: "1",
        specificDate: "2026-06-09",
        startTime: "10:00",
        endTime: "14:00",
        type: "INCLUSION",
    },
    {
        id: "2",
        specificDate: "2026-06-09",
        startTime: "09:00",
        endTime: "10:00",
        type: "EXCLUSION",
    },
];

export const WithBlocks: Story = {
    args: {
        selectedDate: "2026-06-09",
        baseBlocks: MOCK_BASE_BLOCKS,
        overrides: MOCK_OVERRIDES,
    },
};

export const BaseOnly: Story = {
    args: {
        selectedDate: "2026-06-09",
        baseBlocks: MOCK_BASE_BLOCKS,
        overrides: [],
    },
};

export const Empty: Story = {
    args: {
        selectedDate: "2026-06-10",
        baseBlocks: MOCK_BASE_BLOCKS,
        overrides: [],
    },
};
