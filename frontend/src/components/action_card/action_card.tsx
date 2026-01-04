import { Card, Button, Space, Typography, Avatar } from 'antd';
import type React from 'react';
import {type ReactNode } from 'react';

const { Title, Text } = Typography;


interface ActionCardProps {
    icon: ReactNode;
    iconBgColor?: string;
    title: string;
    description: string;
    buttonText: string;
    buttonColor?: string;
    onButtonClick?: () => void;
}

export const ActionCard: React.FC<ActionCardProps> = ({
    icon,
    iconBgColor,
    title,
    description,
    buttonText,
    buttonColor,
    onButtonClick,
}: ActionCardProps) => {

    return (
        <Card variant="borderless">
            <Space orientation="vertical" size="middle" style={{ width: '100%'}}>
                <Avatar
                    size={48}
                    icon={icon}
                    style={{ backgroundColor: iconBgColor }}
                />

                <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
                    <Title level={4} style={{ margin: 0 }}>
                        {title}
                    </Title>

                    <Text type="secondary">{description}</Text>
                </Space>

                <Button
                    type="primary"
                    block
                    size="large"
                    onClick={onButtonClick}
                    style={{ backgroundColor: buttonColor, borderColor: buttonColor }}
                >
                    {buttonText}
                </Button>
            </Space>
        </Card>
    );
}
