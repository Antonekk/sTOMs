import React, { useMemo } from "react";
import { Card, Empty, Flex, Tag, Typography } from "antd";
import dayjs from "dayjs";
import type { BaseBlock, DayBlockKind, ScheduleOverride } from "./types";
import { BLOCK_COLORS, BLOCK_LABELS, LANES } from "./constants";
import { blockPositionStyle, getBlocksForDate, TIMELINE_END_MINUTES, TIMELINE_START_MINUTES } from "./utils";

const { Text } = Typography;

interface DayScheduleViewProps {
  selectedDate: string;
  baseBlocks: BaseBlock[];
  overrides: ScheduleOverride[];
}

const formatTimelineLabel = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(mins).padStart(2, "0")}`;
};

const DayScheduleView: React.FC<DayScheduleViewProps> = ({
  selectedDate,
  baseBlocks,
  overrides,
}) => {
  const blocks = useMemo(
    () => getBlocksForDate(selectedDate, baseBlocks, overrides),
    [selectedDate, baseBlocks, overrides],
  );

  const blocksByKind = useMemo(() => {
    const grouped: Record<DayBlockKind, typeof blocks> = {
      BASE: [],
      INCLUSION: [],
      EXCLUSION: [],
    };

    for (const block of blocks) {
      grouped[block.kind].push(block);
    }

    return grouped;
  }, [blocks]);

  const formattedDate = dayjs(selectedDate, "YYYY-MM-DD").format("DD.MM.YYYY (dddd)");

  return (
    <Card title={formattedDate} size="small">
      <Flex gap={8} wrap="wrap" style={{ marginBottom: 16 }}>
        {LANES.map((kind) => (
          <Tag key={kind} color={BLOCK_COLORS[kind]}>
            {BLOCK_LABELS[kind]}
          </Tag>
        ))}
      </Flex>

      {blocks.length === 0 ? (
        <Empty description="Brak bloków w tym dniu" />
      ) : (
        <Flex vertical gap={12}>
          {LANES.map((kind) => {
            const laneBlocks = blocksByKind[kind];

            return (
              <Flex key={kind} align="center" gap={12}>
                <Text
                  type="secondary"
                  style={{ width: 120, flexShrink: 0, fontSize: 12 }}
                >
                  {BLOCK_LABELS[kind]}
                </Text>
                <div style={{ flex: 1, position: "relative" }}>
                  <div
                    style={{
                      position: "relative",
                      height: 28,
                      background: "#f5f5f5",
                      borderRadius: 4,
                      border: "1px solid #d9d9d9",
                    }}
                  >
                    {laneBlocks.map((block, index) => {
                      const position = blockPositionStyle(block.startTime, block.endTime);

                      return (
                        <div
                          key={`${kind}-${block.startTime}-${block.endTime}-${String(index)}`}
                          title={`${block.startTime} – ${block.endTime}`}
                          style={{
                            position: "absolute",
                            top: 2,
                            bottom: 2,
                            left: position.left,
                            width: position.width,
                            background: BLOCK_COLORS[kind],
                            borderRadius: 3,
                            minWidth: position.width === "0%" ? 0 : 2,
                          }}
                        />
                      );
                    })}
                  </div>
                  <Flex justify="space-between" style={{ marginTop: 4 }}>
                    <Text type="secondary" style={{ fontSize: 11 }}>
                      {formatTimelineLabel(TIMELINE_START_MINUTES)}
                    </Text>
                    <Text type="secondary" style={{ fontSize: 11 }}>
                      {formatTimelineLabel(TIMELINE_END_MINUTES)}
                    </Text>
                  </Flex>
                </div>
              </Flex>
            );
          })}
        </Flex>
      )}
    </Card>
  );
};

export default DayScheduleView;
