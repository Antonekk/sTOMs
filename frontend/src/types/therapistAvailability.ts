export interface TimeBlock {
    start_time: string;
    end_time: string;
}

export interface BaseScheduleBlock extends TimeBlock {
    day_of_week: number;
}

export interface BaseScheduleResponse {
    blocks: BaseScheduleBlock[];
}

export interface BaseScheduleRequest {
    blocks: BaseScheduleBlock[];
}

export type OverrideType = "INCLUSION" | "EXCLUSION";

export interface ScheduleOverrideResponse {
    id: string;
    type: OverrideType;
    specific_date: string;
    start_time: string;
    end_time: string;
}

export interface ScheduleOverrideRequest {
    type: OverrideType;
    specific_date: string;
    start_time: string;
    end_time: string;
}
