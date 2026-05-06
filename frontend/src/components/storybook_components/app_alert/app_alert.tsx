import { Alert } from "antd";
import type { AlertProps } from "antd";
import type React from "react";

export interface AppAlertProps {
    type?: AlertProps["type"];
    title: string;
    description?: string;
    onClose?: () => void;
    style?: React.CSSProperties;
}

const AppAlert: React.FC<AppAlertProps> = ({
    type = "error",
    title,
    description,
    onClose,
    style,
}) => (
    <Alert
        type={type}
        showIcon
        title={title}
        description={description}
        style={style}
        closable={
            onClose
                ? { closeIcon: true, onClose }
                : undefined
        }
    />
);

export default AppAlert;
