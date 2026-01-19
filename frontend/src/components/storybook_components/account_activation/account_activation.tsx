import React from 'react';
import { Button, Result } from 'antd';

export interface AccountActivationProps {
    success: boolean;
    title: string;
    subTitle: string;
    onClick: () => void;
}


const AccountActivation: React.FC<AccountActivationProps> = ({
    success,
    title,
    subTitle,
    onClick,
}) => (
  <Result
      status={success ? "success" : "error"}
      title={title}
      subTitle={subTitle}
      extra={[
        <Button type="primary" key="login" onClick={onClick}>
          {success ? "Zaloguj się" : "Zarejestruj się"}
        </Button>,
      ]}
    />
);

export default AccountActivation;