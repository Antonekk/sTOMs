import type { DayBlockKind } from "./types";

export const BLOCK_COLORS: Record<DayBlockKind, string> = {
  BASE: "#1677ff",
  INCLUSION: "#52c41a",
  EXCLUSION: "#ff4d4f",
};

export const BLOCK_LABELS: Record<DayBlockKind, string> = {
  BASE: "Grafik bazowy",
  INCLUSION: "Dodatkowe godziny",
  EXCLUSION: "Wyjątek",
};

export const LANES: DayBlockKind[] = ["BASE", "INCLUSION", "EXCLUSION"];
