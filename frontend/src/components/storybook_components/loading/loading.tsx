import React from 'react';
import { LoadingOutlined } from '@ant-design/icons';
import { Spin } from 'antd';

const Loading: React.FC = () => {
    return (
        <Spin size="large"indicator={<LoadingOutlined spin />} fullscreen />
    )
}

export default Loading;
