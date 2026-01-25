import React from "react";
import { Card, TimePicker, Button, Row, Col, Space } from "antd";
import { PlusOutlined, DeleteOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import type { WeeklyAvailabilityBlock } from "./types.ts";

interface WeeklyScheduleEditorProps  {
  value: WeeklyAvailabilityBlock[];
  onChange: (blocks: WeeklyAvailabilityBlock[]) => void;
  editable?: boolean;
};

const DAYS = [
  "Poniedziałek",
  "Wtorek",
  "Środa",
  "Czwartek",
  "Piątek",
  "Sobota",
  "Niedziela",
];

const WeeklyScheduleEditor: React.FC<WeeklyScheduleEditorProps> = ({
  value,
  onChange,
  editable = true,
}) => {
  const addBlock = (dayOfWeek: number) => {
    onChange([
      ...value,
      {
        id: crypto.randomUUID(),
        dayOfWeek,
        startTime: "08:00",
        endTime: "16:00",
      },
    ]);
  };

  const updateBlock = (
    id: string,
    startTime: string,
    endTime: string
  ) => {
    onChange(
      value.map((b) =>
        b.id === id ? { ...b, startTime, endTime } : b
      )
    );
  };

  const removeBlock = (id: string) => {
    onChange(value.filter((b) => b.id !== id));
  };

  return (
    <Space orientation="vertical" style={{ width: "100%" }}>
      {DAYS.map((day, dayOfWeek) => {
        const blocks = value.filter(
          (b) => b.dayOfWeek === dayOfWeek
        );

        return (
          <Card
            key={day}
            title={day}
            size="small"
            extra={
              editable && (
                <Button
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={() => {addBlock(dayOfWeek)}}
                >
                  Dodaj
                </Button>
              )
            }
          >
            {blocks.length === 0 && (
              <em style={{ color: "#999" }}>
                Brak dostępności
              </em>
            )}

            {blocks.map((block) => (
              <Row
                key={block.id}
                gutter={8}
                align="middle"
                style={{ marginBottom: 8 }}
              >
                <Col>
                  <TimePicker
                    value={dayjs(block.startTime, "HH:mm")}
                    format="HH:mm"
                    minuteStep={15}
                    disabled={!editable}
                    disabledTime={() => {
                      const endHour = dayjs(block.endTime, "HH:mm").hour();
                      const endMinute = dayjs(block.endTime, "HH:mm").minute();
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
                    onChange={(v) =>{
                      updateBlock(
                        block.id,
                        v?.format("HH:mm") ?? block.startTime,
                        block.endTime
                      )}
                    }
                  />
                </Col>
                <Col>-</Col>
                <Col>
                  <TimePicker
                    value={dayjs(block.endTime, "HH:mm")}
                    format="HH:mm"
                    minuteStep={15}
                    disabled={!editable}
                    disabledTime={() => {
                      const startHour = dayjs(block.startTime, "HH:mm").hour();
                      const startMinute = dayjs(block.startTime, "HH:mm").minute();
                      return {
                        disabledHours: () =>
                          Array.from({ length: 24 }, (_, i) => i).filter(
                            (h) => h < startHour || (h === startHour && startMinute === 45)
                          ),
                        disabledMinutes: (selectedHour) =>
                          selectedHour === startHour
                            ? Array.from({ length: 60 }, (_, i) => i).filter(
                                (m) => m <= startMinute
                              )
                            : [],
                      };
                    }}
                    onChange={(v) =>{
                      updateBlock(
                        block.id,
                        block.startTime,
                        v?.format("HH:mm") ?? block.endTime
                      )}}
                  />
                </Col>
                {editable && (
                  <Col>
                    <Button
                      danger
                      size="small"
                      icon={<DeleteOutlined />}
                      onClick={() => {removeBlock(block.id)}}
                    />
                  </Col>
                )}
              </Row>
            ))}
          </Card>
        );
      })}
    </Space>
  );
};


export default WeeklyScheduleEditor;
