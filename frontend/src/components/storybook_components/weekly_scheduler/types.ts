export interface WeeklyAvailabilityBlock {
  id: string;
  dayOfWeek: number; // 0 = Monday
  startTime: string; // "HH:mm"
  endTime: string;   // "HH:mm"
};
