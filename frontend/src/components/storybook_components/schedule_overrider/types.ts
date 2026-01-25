export type OverrideType = "INCLUSION" | "EXCLUSION";

export interface ScheduleOverride {
  id: string;
  specificDate: string; // "YYYY-MM-DD"
  startTime: string;    // "HH:mm"
  endTime: string;      // "HH:mm"
  type: OverrideType;
}
