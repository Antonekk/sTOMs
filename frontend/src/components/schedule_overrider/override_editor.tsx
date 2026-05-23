import React, { useMemo } from "react";
import {
  Button,
  Card,
  Col,
  Empty,
  Row,
  Segmented,
  Space,
  TimePicker,
} from "antd";
import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import type { OverrideType, ScheduleOverride } from "./types";

interface OverrideEditorProps {
  selectedDate: string;
  value: ScheduleOverride[];
  onChange: (overrides: ScheduleOverride[]) => void;
  editable?: boolean;
}

const OverrideEditor: React.FC<OverrideEditorProps> = ({
  selectedDate,
  value,
  onChange,
  editable = true,
}) => {
  const [activeTab, setActiveTab] = React.useState<OverrideType>("INCLUSION");

  const dayOverrides = useMemo(
    () =>
      value
        .filter(
          (override) =>
            override.specificDate === selectedDate && override.type === activeTab,
        )
        .sort((a, b) => a.startTime.localeCompare(b.startTime)),
    [value, selectedDate, activeTab],
  );

  const addOverride = () => {
    onChange([
      ...value,
      {
        id: crypto.randomUUID(),
        specificDate: selectedDate,
        startTime: "08:00",
        endTime: "16:00",
        type: activeTab,
      },
    ]);
  };

  const updateOverride = (
    id: string,
    updates: Partial<Omit<ScheduleOverride, "id" | "type">>,
  ) => {
    onChange(value.map((override) => (override.id === id ? { ...override, ...updates } : override)));
  };

  const removeOverride = (id: string) => {
    onChange(value.filter((override) => override.id !== id));
  };

  return (
    <Card title="Edycja wyjątków" size="small">
      <Space orientation="vertical" style={{ width: "100%" }} size="middle">
        <Segmented
          value={activeTab}
          onChange={(v) => { setActiveTab(v as OverrideType); }}
          options={[
            { label: "Dodatkowe godziny", value: "INCLUSION" },
            { label: "Wyjątki", value: "EXCLUSION" },
          ]}
          block
        />

        {editable && (
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={addOverride}
            block
          >
            {activeTab === "INCLUSION"
              ? "Dodaj dodatkowe godziny"
              : "Dodaj wyjątek"}
          </Button>
        )}

        {dayOverrides.length === 0 && (
          <Empty
            description={
              activeTab === "INCLUSION"
                ? "Brak dodatkowych godzin w tym dniu"
                : "Brak wyjątków w tym dniu"
            }
          />
        )}

        {dayOverrides.map((override) => (
          <Row
            key={override.id}
            gutter={8}
            align="middle"
            style={{ marginBottom: 8 }}
          >
            <Col>
              <TimePicker
                value={dayjs(override.startTime, "HH:mm")}
                format="HH:mm"
                minuteStep={15}
                disabled={!editable}
                disabledTime={() => {
                  const endHour = dayjs(override.endTime, "HH:mm").hour();
                  const endMinute = dayjs(override.endTime, "HH:mm").minute();
                  return {
                    disabledHours: () =>
                      Array.from({ length: 24 }, (_, i) => i).filter(
                        (h) => h > endHour || (h === endHour && endMinute === 0),
                      ),
                    disabledMinutes: (selectedHour) =>
                      selectedHour === endHour
                        ? Array.from({ length: 60 }, (_, i) => i).filter(
                            (m) => m >= endMinute,
                          )
                        : [],
                  };
                }}
                onChange={(v) => {
                  updateOverride(override.id, {
                    startTime: v?.format("HH:mm") ?? override.startTime,
                  });
                }}
              />
            </Col>
            <Col>-</Col>
            <Col>
              <TimePicker
                value={dayjs(override.endTime, "HH:mm")}
                format="HH:mm"
                minuteStep={15}
                disabled={!editable}
                disabledTime={() => {
                  const startHour = dayjs(override.startTime, "HH:mm").hour();
                  const startMinute = dayjs(override.startTime, "HH:mm").minute();
                  return {
                    disabledHours: () =>
                      Array.from({ length: 24 }, (_, i) => i).filter(
                        (h) =>
                          h < startHour || (h === startHour && startMinute === 45),
                      ),
                    disabledMinutes: (selectedHour) =>
                      selectedHour === startHour
                        ? Array.from({ length: 60 }, (_, i) => i).filter(
                            (m) => m <= startMinute,
                          )
                        : [],
                  };
                }}
                onChange={(v) => {
                  updateOverride(override.id, {
                    endTime: v?.format("HH:mm") ?? override.endTime,
                  });
                }}
              />
            </Col>
            {editable && (
              <Col>
                <Button
                  danger
                  size="small"
                  icon={<DeleteOutlined />}
                  onClick={() => { removeOverride(override.id); }}
                />
              </Col>
            )}
          </Row>
        ))}
      </Space>
    </Card>
  );
};

export default OverrideEditor;
