import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import ScheduleOverrider from "./schedule_overrider";
import type { ScheduleOverride } from "./types";

const meta: Meta<typeof ScheduleOverrider> = {
  title: "Components/ScheduleOverrider",
  component: ScheduleOverrider,
};

export default meta;
type Story = StoryObj<typeof ScheduleOverrider>;

const ScheduleOverriderWithState = (props: {
  initialValue?: ScheduleOverride[];
  editable?: boolean;
}) => {
  const [value, setValue] = useState<ScheduleOverride[]>(
    props.initialValue ?? []
  );
  return (
    <ScheduleOverrider
      value={value}
      onChange={setValue}
      editable={props.editable}
    />
  );
};

export const Empty: Story = {
  render: () => <ScheduleOverriderWithState />,
};

export const WithData: Story = {
  render: () => (
    <ScheduleOverriderWithState
      initialValue={[
        {
          id: "1",
          specificDate: "2025-01-20",
          startTime: "10:00",
          endTime: "14:00",
          type: "INCLUSION",
        },
        {
          id: "2",
          specificDate: "2025-01-20",
          startTime: "16:00",
          endTime: "18:00",
          type: "INCLUSION",
        },
        {
          id: "3",
          specificDate: "2025-01-25",
          startTime: "08:00",
          endTime: "12:00",
          type: "EXCLUSION",
        },
      ]}
    />
  ),
};

export const ReadOnly: Story = {
  render: () => (
    <ScheduleOverriderWithState
      editable={false}
      initialValue={[
        {
          id: "1",
          specificDate: "2025-01-20",
          startTime: "10:00",
          endTime: "14:00",
          type: "INCLUSION",
        },
        {
          id: "2",
          specificDate: "2025-01-25",
          startTime: "08:00",
          endTime: "12:00",
          type: "EXCLUSION",
        },
      ]}
    />
  ),
};
