import { Select } from "antd";
import type React from "react";
import type { Patient } from "../../types/patients";

export interface PatientSelectorProps {
    patients: Patient[];
    value?: string;
    onChange?: (patientId: string) => void;
    disabled?: boolean;
    placeholder?: string;
}

const formatPatientLabel = (patient: Patient) => {
    const name = `${patient.first_name} ${patient.last_name}`;
    return patient.is_primary ? `${name} (główny)` : name;
};

const PatientSelector: React.FC<PatientSelectorProps> = ({
    patients,
    value,
    onChange,
    disabled = false,
    placeholder = "Wybierz pacjenta",
}) => (
    <Select
        value={value}
        onChange={onChange}
        disabled={disabled || patients.length === 0}
        placeholder={patients.length === 0 ? "Brak dostępnych pacjentów" : placeholder}
        options={patients.map((patient) => ({
            value: patient.id,
            label: formatPatientLabel(patient),
        }))}
    />
);

export default PatientSelector;
