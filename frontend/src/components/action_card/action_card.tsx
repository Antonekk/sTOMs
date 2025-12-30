import {Card} from 'antd';
import {ScheduleFilled} from '@ant-design/icons';


interface ActionCardProps {
    title:  string,
    description: string,
    button_text?: string,
    button_CTA?: string,
};


export default function ActionCard({
    title,
    description,
    button_text,
    button_CTA,
}: ActionCardProps){
    return (
        <Card
            title={title}
        >
            <ScheduleFilled />
        </Card>)
}
