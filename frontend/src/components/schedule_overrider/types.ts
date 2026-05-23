export type OverrideType = "INCLUSION" | "EXCLUSION";

export interface ScheduleOverride {
  id: string;
  specificDate: string; // "YYYY-MM-DD"
  startTime: string;    // "HH:mm"
  endTime: string;      // "HH:mm"
  type: OverrideType;
}

export interface BaseBlock {
  dayOfWeek: number;
  startTime: string;
  endTime: string;
}

export type DayBlockKind = "BASE" | "INCLUSION" | "EXCLUSION";

export interface DayBlock {
  kind: DayBlockKind;
  startTime: string;
  endTime: string;
}
