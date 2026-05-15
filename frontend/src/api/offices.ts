import api from "./api"
import type { Localization } from "../types/offices"

export const listLocalizations = () =>
    api.get<Localization[]>("/api/localizations/")
