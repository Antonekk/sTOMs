import React, { useEffect, useState } from "react";
import { Button, Flex, message, Space, Typography } from "antd";
import WeeklyScheduleEditor from "../components/storybook_components/weekly_scheduler/weekly_schedule_editor";
import type { WeeklyAvailabilityBlock } from "../components/storybook_components/weekly_scheduler/types";
import type { BaseScheduleRequest, BaseScheduleResponse } from "../types/therapistAvailability";
import { getWeeklySchedule, saveWeeklySchedule } from "../api/therapistAvailability";
import Loading from "../components/storybook_components/loading/loading";
import { getApiErrorMessage } from "../utils/apiError";

const { Title } = Typography;

const normalizeTime = (time: string) => time.slice(0, 5);

const transformToBlocks = (schedule: BaseScheduleResponse): WeeklyAvailabilityBlock[] =>
    schedule.blocks.map((block) => ({
        id: crypto.randomUUID(),
        dayOfWeek: block.day_of_week,
        startTime: normalizeTime(block.start_time),
        endTime: normalizeTime(block.end_time),
    }));

const transformToRequest = (blocks: WeeklyAvailabilityBlock[]): BaseScheduleRequest => ({
    blocks: blocks.map((block) => ({
        day_of_week: block.dayOfWeek,
        start_time: block.startTime,
        end_time: block.endTime,
    })),
});

const WeeklySchedule: React.FC = () => {
    const [blocks, setBlocks] = useState<WeeklyAvailabilityBlock[]>([]);
    const [savedBlocks, setSavedBlocks] = useState<WeeklyAvailabilityBlock[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        const fetchSchedule = async () => {
            try {
                const response = await getWeeklySchedule();
                const fetchedBlocks = transformToBlocks(response.data);
                setBlocks(fetchedBlocks);
                setSavedBlocks(fetchedBlocks);
            } catch (error) {
                void message.error(getApiErrorMessage(error, "Nie udało się wczytać harmonogramu."));
            } finally {
                setLoading(false);
            }
        };

        void fetchSchedule();
    }, []);

    const handleEdit = () => {
        setIsEditing(true);
    };

    const handleDiscard = () => {
        setBlocks(savedBlocks);
        setIsEditing(false);
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const requestData = transformToRequest(blocks);
            await saveWeeklySchedule(requestData);
            setSavedBlocks(blocks);
            setIsEditing(false);
            void message.success("Harmonogram został zapisany");
        } catch (error) {
            void message.error(getApiErrorMessage(error, "Nie udało się zapisać harmonogramu."));
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <Loading/>;
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24 }}>
            <Title level={2}>Grafik tygodniowy</Title>
            <WeeklyScheduleEditor
                value={blocks}
                onChange={setBlocks}
                editable={isEditing}
            />
            <Space>
                {isEditing ? (
                    <>
                        <Button
                            type="primary"
                            onClick={() => void handleSave()}
                            loading={saving}
                        >
                            Zapisz
                        </Button>
                        <Button onClick={handleDiscard} disabled={saving}>
                            Anuluj
                        </Button>
                    </>
                ) : (
                    <Button type="primary" onClick={handleEdit}>
                        Edytuj harmonogram
                    </Button>
                )}
            </Space>
        </Flex>
    );
};

export default WeeklySchedule;
