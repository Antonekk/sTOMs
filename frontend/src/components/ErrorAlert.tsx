import { Alert } from "antd";
import type React from "react";

export interface ErrorAlertProps {
    title: string;
    description: string;
    onClose?: () => void;
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({ title, description, onClose }) => (
    <Alert
        type="error"
        showIcon
        title={title}
        description={description}
        closable={
            onClose
                ? { closeIcon: true, onClose }
                : undefined
        }
    />
);

export default ErrorAlert;
