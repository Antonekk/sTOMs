import api from "./api"
import { OFFICE_ENDPOINTS } from "./endpoints"
import type { Localization } from "../types/offices"

export const listLocalizations = () =>
    api.get<Localization[]>(OFFICE_ENDPOINTS.LOCALIZATIONS)
