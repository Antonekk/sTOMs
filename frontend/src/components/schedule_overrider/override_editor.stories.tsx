import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import OverrideEditor from "./override_editor";
import type { ScheduleOverride } from "./types";

const meta: Meta<typeof OverrideEditor> = {
    title: "Components/ScheduleOverrider/OverrideEditor",
    component: OverrideEditor,
    tags: ["autodocs"],
};

export default meta;

type Story = StoryObj<typeof meta>;

const SELECTED_DATE = "2026-06-09";

const INITIAL_OVERRIDES: ScheduleOverride[] = [
    {
        id: "1",
        specificDate: SELECTED_DATE,
        startTime: "10:00",
        endTime: "14:00",
        type: "INCLUSION",
    },
    {
        id: "2",
        specificDate: SELECTED_DATE,
        startTime: "09:00",
        endTime: "10:00",
        type: "EXCLUSION",
    },
];

const OverrideEditorWithState = ({
    initialValue = [],
    editable = true,
}: {
    initialValue?: ScheduleOverride[];
    editable?: boolean;
}) => {
    const [value, setValue] = useState<ScheduleOverride[]>(initialValue);

    return (
        <OverrideEditor
            selectedDate={SELECTED_DATE}
            value={value}
            onChange={setValue}
            editable={editable}
        />
    );
};

export const Empty: Story = {
    render: () => <OverrideEditorWithState />,
};

export const WithData: Story = {
    render: () => <OverrideEditorWithState initialValue={INITIAL_OVERRIDES} />,
};

export const ReadOnly: Story = {
    render: () => (
        <OverrideEditorWithState
            initialValue={INITIAL_OVERRIDES}
            editable={false}
        />
    ),
};
