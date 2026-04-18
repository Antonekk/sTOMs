import api from "./api"
import { PATIENT_ENDPOINTS } from "./endpoints"
import type { Patient, PatientWrite } from "../types/patients"

export const listPatients = () =>
    api.get<Patient[]>(PATIENT_ENDPOINTS.PATIENTS)

export const getPatient = (id: string) =>
    api.get<Patient>(PATIENT_ENDPOINTS.PATIENT(id))

export const createPatient = (data: PatientWrite) =>
    api.post<Patient>(PATIENT_ENDPOINTS.PATIENTS, data)

export const updatePatient = (id: string, data: PatientWrite) =>
    api.put<Patient>(PATIENT_ENDPOINTS.PATIENT(id), data)

export const deletePatient = (id: string) =>
    api.delete(PATIENT_ENDPOINTS.PATIENT(id))
