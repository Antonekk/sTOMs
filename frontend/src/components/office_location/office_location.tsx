import { Space, Typography } from "antd"
import type React from "react"
import type { OfficeLocation } from "../../types/reservations"
import { formatOfficeAddress } from "../../utils/officeDisplay"

const { Text } = Typography

export interface OfficeLocationDisplayProps {
    office: OfficeLocation | null | undefined
    label?: string
    compact?: boolean
}

const OfficeLocationDisplay: React.FC<OfficeLocationDisplayProps> = ({
    office,
    label = "Lokalizacja",
    compact = false,
}) => {
    if (!office) return null

    if (compact) {
        return (
            <Text type="secondary">
                {office.name}
                {" · "}
                {formatOfficeAddress(office)}
                {office.room_number ? ` · pokój ${office.room_number}` : ""}
            </Text>
        )
    }

    return (
        <Space orientation="vertical" size={4}>
            <Text strong>{label}</Text>
            <Text>{office.name}</Text>
            <Text type="secondary">{formatOfficeAddress(office)}</Text>
            {office.room_number && (
                <Text type="secondary">Pokój {office.room_number}</Text>
            )}
        </Space>
    )
}

export default OfficeLocationDisplay
