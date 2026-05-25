import { djangoWeekdayFromDate } from "../../utils/timeSlots";
import type { BaseBlock, DayBlock, ScheduleOverride } from "./types";

export const TIMELINE_START_MINUTES = 6 * 60;
export const TIMELINE_END_MINUTES = 22 * 60;

export const getBlocksForDate = (
  date: string,
  baseBlocks: BaseBlock[],
  overrides: ScheduleOverride[],
): DayBlock[] => {
  const dayOfWeek = djangoWeekdayFromDate(date);

  const base: DayBlock[] = baseBlocks
    .filter((block) => block.dayOfWeek === dayOfWeek)
    .map((block) => ({
      kind: "BASE" as const,
      startTime: block.startTime,
      endTime: block.endTime,
    }));

  const dayOverrides = overrides.filter((override) => override.specificDate === date);

  const inclusions: DayBlock[] = dayOverrides
    .filter((override) => override.type === "INCLUSION")
    .map((override) => ({
      kind: "INCLUSION" as const,
      startTime: override.startTime,
      endTime: override.endTime,
    }));

  const exclusions: DayBlock[] = dayOverrides
    .filter((override) => override.type === "EXCLUSION")
    .map((override) => ({
      kind: "EXCLUSION" as const,
      startTime: override.startTime,
      endTime: override.endTime,
    }));

  return [...base, ...inclusions, ...exclusions].sort((a, b) =>
    a.startTime.localeCompare(b.startTime),
  );
};

export const blockPositionStyle = (
  startTime: string,
  endTime: string,
): { left: string; width: string } => {
  const toMinutes = (time: string) => {
    const [hours, minutes] = time.split(":").map(Number);
    return hours * 60 + minutes;
  };

  const start = Math.max(toMinutes(startTime), TIMELINE_START_MINUTES);
  const end = Math.min(toMinutes(endTime), TIMELINE_END_MINUTES);
  const range = TIMELINE_END_MINUTES - TIMELINE_START_MINUTES;

  if (end <= start) {
    return { left: "0%", width: "0%" };
  }

  return {
    left: `${String(((start - TIMELINE_START_MINUTES) / range) * 100)}%`,
    width: `${String(((end - start) / range) * 100)}%`,
  };
};
