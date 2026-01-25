import React, { useMemo } from "react";
import {
  Card,
  TimePicker,
  DatePicker,
  Button,
  Row,
  Col,
  Space,
  Segmented,
  Empty,
} from "antd";
import { PlusOutlined, DeleteOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import type { ScheduleOverride, OverrideType } from "./types";

interface ScheduleOverriderProps {
  value: ScheduleOverride[];
  onChange: (overrides: ScheduleOverride[]) => void;
  editable?: boolean;
}

const ScheduleOverrider: React.FC<ScheduleOverriderProps> = ({
  value,
  onChange,
  editable = true,
}) => {
  const [activeTab, setActiveTab] = React.useState<OverrideType>("INCLUSION");

  const filteredOverrides = useMemo(() => {
    return value
      .filter((o) => o.type === activeTab)
      .sort((a, b) => {
        const dateCompare = a.specificDate.localeCompare(b.specificDate);
        if (dateCompare !== 0) return dateCompare;
        return a.startTime.localeCompare(b.startTime);
      });
  }, [value, activeTab]);

  const groupedByDate = useMemo(() => {
    const groups: Record<string, ScheduleOverride[]> = {};
    for (const override of filteredOverrides) {
      groups[override.specificDate] ??= [];
      groups[override.specificDate].push(override);
    }
    return groups;
  }, [filteredOverrides]);

  const addOverride = (date: string) => {
    onChange([
      ...value,
      {
        id: crypto.randomUUID(),
        specificDate: date,
        startTime: "08:00",
        endTime: "16:00",
        type: activeTab,
      },
    ]);
  };

  const addNewDateOverride = () => {
    const today = dayjs().format("YYYY-MM-DD");
    addOverride(today);
  };

  const updateOverride = (
    id: string,
    updates: Partial<Omit<ScheduleOverride, "id" | "type">>
  ) => {
    onChange(
      value.map((o) => (o.id === id ? { ...o, ...updates } : o))
    );
  };

  const removeOverride = (id: string) => {
    onChange(value.filter((o) => o.id !== id));
  };

  const formatDate = (dateStr: string) => {
    return dayjs(dateStr).format("DD.MM.YYYY (dddd)");
  };

  return (
    <Space orientation="vertical" style={{ width: "100%" }}>
      <Segmented
        value={activeTab}
        onChange={(v) => {setActiveTab(v as OverrideType)}}
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
          onClick={addNewDateOverride}
          block
        >
          {activeTab === "INCLUSION"
            ? "Dodaj dodatkowe godziny"
            : "Dodaj wyjątek"}
        </Button>
      )}

      {Object.keys(groupedByDate).length === 0 && (
        <Empty
          description={
            activeTab === "INCLUSION"
              ? "Brak dodatkowych godzin"
              : "Brak wyjątków"
          }
        />
      )}

      {Object.entries(groupedByDate).map(([date, overrides]) => (
        <Card
          key={date}
          title={formatDate(date)}
          size="small"
          extra={
            editable && (
              <Button
                size="small"
                icon={<PlusOutlined />}
                onClick={() => {addOverride(date)}}
              >
                Dodaj
              </Button>
            )
          }
        >
          {overrides.map((override) => (
            <Row
              key={override.id}
              gutter={8}
              align="middle"
              style={{ marginBottom: 8 }}
            >
              <Col>
                <DatePicker
                  value={dayjs(override.specificDate)}
                  format="DD.MM.YYYY"
                  disabled={!editable}
                  onChange={(v) => {
                    if (v) {
                      updateOverride(override.id, {
                        specificDate: v.format("YYYY-MM-DD"),
                      });
                    }
                  }}
                />
              </Col>
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
                          (h) => h > endHour || (h === endHour && endMinute === 0)
                        ),
                      disabledMinutes: (selectedHour) =>
                        selectedHour === endHour
                          ? Array.from({ length: 60 }, (_, i) => i).filter(
                              (m) => m >= endMinute
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
                            h < startHour || (h === startHour && startMinute === 45)
                        ),
                      disabledMinutes: (selectedHour) =>
                        selectedHour === startHour
                          ? Array.from({ length: 60 }, (_, i) => i).filter(
                              (m) => m <= startMinute
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
                    onClick={() => {removeOverride(override.id)}}
                  />
                </Col>
              )}
            </Row>
          ))}
        </Card>
      ))}
    </Space>
  );
};

export default ScheduleOverrider;
