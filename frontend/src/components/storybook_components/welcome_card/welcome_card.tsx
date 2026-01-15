import { Card, Space, Typography, Avatar } from 'antd';
import type React from 'react';
import { type ReactNode } from 'react';

const { Title, Text } = Typography;

interface WelcomeCardProps {
    icon: ReactNode;
    iconBgColor?: string;
    title: string;
    subtitle?: string;
    description?: string;
}

export const WelcomeCard: React.FC<WelcomeCardProps> = ({
    icon,
    iconBgColor,
    title,
    subtitle,
    description,
}: WelcomeCardProps) => {
    return (
        <Card variant="borderless">
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>

                    <Avatar
                        size={48}
                        icon={icon}
                        style={{ backgroundColor: iconBgColor }}
                    />
                
                <Space orientation='vertical' size="small">
                    <Title level={4} style={{ margin: 0 }}>
                        {title}
                    </Title>

                    {subtitle && (
                        <Text strong>{subtitle}</Text>
                    )}

                    {description && (
                        <Text type="secondary">{description}</Text>
                    )}
                </Space>

                
                
            </Space>
        </Card>
    );
};
