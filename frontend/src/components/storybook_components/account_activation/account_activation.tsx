import React from 'react';
import { Button, Result } from 'antd';

export interface AccountActivationProps {
    success: boolean;
    title: string;
    subTitle: string;
    onClick: () => void;
    buttonLabel?: string;
}


const AccountActivation: React.FC<AccountActivationProps> = ({
    success,
    title,
    subTitle,
    onClick,
    buttonLabel,
}) => (
  <Result
      status={success ? "success" : "error"}
      title={title}
      subTitle={subTitle}
      extra={[
        <Button type="primary" key="login" onClick={onClick}>
          {buttonLabel ?? (success ? "Zaloguj się" : "Zarejestruj się")}
        </Button>,
      ]}
    />
);

export default AccountActivation;