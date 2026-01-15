import React from 'react';
import styles from './styles.module.css';
import { Card, Flex, Input, Typography } from 'antd';


const { Title, Text } = Typography;


export interface EmailConfirmationProps {
    title_size?: number;
    title: string;
    description?: string;
    onChange : (value: string) => void;
}

export const EmailConfirmation: React.FC<EmailConfirmationProps> = ({
    title,
    description,
    onChange
}: EmailConfirmationProps) => {
    return (
        <Flex className={styles.container} justify='center' align='center' >
            <Card className={styles.card} >
                <Flex vertical gap={0} align='center' >
                    <Title className={styles.title_text} level={4}>
                        {title}
                    </Title>

                    <Text className={styles.description} type="secondary">
                        {description}
                    </Text>


                    <Input.OTP 
                        length={6}
                        autoFocus
                        formatter={(str) => str.replace(/\D/g, '')} 
                        size="large" 
                        onChange={onChange} 
                    />
                </Flex>
                
            </Card>
        </Flex>
    );
};