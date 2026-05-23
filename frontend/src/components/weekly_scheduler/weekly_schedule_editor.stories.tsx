import { useState } from "react";
import type { Meta, StoryObj } from '@storybook/react-vite';

import WeeklyScheduleEditor from "./weekly_schedule_editor";
import type { WeeklyAvailabilityBlock } from "./types.ts";

const meta: Meta<typeof WeeklyScheduleEditor> = {
  component: WeeklyScheduleEditor,
  title: "Scheduling/WeeklyScheduleEditor",
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Empty: Story = {
  render: () => {
    const [value, setValue] = useState<WeeklyAvailabilityBlock[]>([]);
    return (
      <WeeklyScheduleEditor
        value={value}
        onChange={setValue}
      />
    );
  },
};

export const TypicalWeek: Story = {
  render: () => {
    const [value, setValue] = useState<WeeklyAvailabilityBlock[]>([
      {
        id: "1",
        dayOfWeek: 0,
        startTime: "08:00",
        endTime: "16:00",
      },
      {
        id: "2",
        dayOfWeek: 2,
        startTime: "10:00",
        endTime: "18:00",
      },
      {
        id: "3",
        dayOfWeek: 4,
        startTime: "09:00",
        endTime: "14:00",
      },
    ]);

    return (
      <WeeklyScheduleEditor
        value={value}
        onChange={setValue}
      />
    );
  },
};

export const ReadOnly: Story = {
  render: () => {
    const [value, setValue] = useState<WeeklyAvailabilityBlock[]>([
      {
        id: "1",
        dayOfWeek: 0,
        startTime: "08:00",
        endTime: "16:00",
      },
      {
        id: "2",
        dayOfWeek: 2,
        startTime: "10:00",
        endTime: "18:00",
      },
      {
        id: "3",
        dayOfWeek: 4,
        startTime: "09:00",
        endTime: "14:00",
      },
    ]);

    return (
      <WeeklyScheduleEditor
        value={value}
        onChange={setValue}
        editable={false}
      />
    );
  },
};