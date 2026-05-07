import React from "react";
import { DatePicker, Space } from "antd";
import dayjs from "dayjs";
import DayScheduleView from "./day_schedule_view";
import OverrideEditor from "./override_editor";
import type { BaseBlock, ScheduleOverride } from "./types";

interface ScheduleOverriderProps {
  value: ScheduleOverride[];
  onChange: (overrides: ScheduleOverride[]) => void;
  baseBlocks: BaseBlock[];
  editable?: boolean;
}

const ScheduleOverrider: React.FC<ScheduleOverriderProps> = ({
  value,
  onChange,
  baseBlocks,
  editable = true,
}) => {
  const [selectedDate, setSelectedDate] = React.useState(() =>
    dayjs().format("YYYY-MM-DD"),
  );

  return (
    <Space orientation="vertical" style={{ width: "100%" }} size="middle">
      <DatePicker
        value={dayjs(selectedDate, "YYYY-MM-DD")}
        format="DD.MM.YYYY (dddd)"
        onChange={(date) => {
          if (date) {
            setSelectedDate(date.format("YYYY-MM-DD"));
          }
        }}
        style={{ width: "100%" }}
      />

      <DayScheduleView
        selectedDate={selectedDate}
        baseBlocks={baseBlocks}
        overrides={value}
      />

      <OverrideEditor
        selectedDate={selectedDate}
        value={value}
        onChange={onChange}
        editable={editable}
      />
    </Space>
  );
};

export default ScheduleOverrider;
