import { Button, Space, Typography } from 'antd';
import type React from 'react';

const { Title } = Typography;

interface WelcomeScreenProps {
    primaryButtonText: string;
    secondaryButtonText: string;
    onPrimaryClick: () => void;
    onSecondaryClick: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
    primaryButtonText,
    secondaryButtonText,
    onPrimaryClick,
    onSecondaryClick,
}: WelcomeScreenProps) => {
    return (
        <Space
            orientation="vertical"
            size="large"
            style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
            }}
        >
            <Title level={1}>Witamy w sTOMs</Title>
            <Space size="middle">
                <Button type="primary" size="large" onClick={onPrimaryClick}>
                    {primaryButtonText}
                </Button>
                <Button size="large" onClick={onSecondaryClick}>
                    {secondaryButtonText}
                </Button>
            </Space>
        </Space>
    );
};


export default WelcomeScreen;

