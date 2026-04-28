import api from "./api"
import { PATIENT_ENDPOINTS } from "./endpoints"
import type { Patient, PatientWrite } from "../types/patients"

export interface ListPatientsParams {
    is_active?: boolean;
}

export const listPatients = (params?: ListPatientsParams) =>
    api.get<Patient[]>(PATIENT_ENDPOINTS.PATIENTS, { params })

export const getPatient = (id: string) =>
    api.get<Patient>(PATIENT_ENDPOINTS.PATIENT(id))

export const createPatient = (data: PatientWrite) =>
    api.post<Patient>(PATIENT_ENDPOINTS.PATIENTS, data)

export const updatePatient = (id: string, data: PatientWrite) =>
    api.put<Patient>(PATIENT_ENDPOINTS.PATIENT(id), data)

export const deletePatient = (id: string) =>
    api.delete(PATIENT_ENDPOINTS.PATIENT(id))

export const restorePatient = (id: string) =>
    api.post<Patient>(PATIENT_ENDPOINTS.RESTORE_PATIENT(id))
