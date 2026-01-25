import React, { useEffect, useState } from "react";
import { Button, Flex, message, Space, Typography } from "antd";
import WeeklyScheduleEditor from "../components/storybook_components/weekly_scheduler/weekly_schedule_editor";
import type { WeeklyAvailabilityBlock } from "../components/storybook_components/weekly_scheduler/types";
import type { DayOfWeek, TimeBlock, WeeklyScheduleRequest, WeeklyScheduleResponse } from "../types/auth";
import { getWeeklySchedule, saveWeeklySchedule } from "../api/auth";
import Loading from "../components/storybook_components/loading/loading";

const { Title } = Typography;


// Handles transformation between WeeklySchedule response and component block type
const transformToBlocks = (schedule: WeeklyScheduleResponse): WeeklyAvailabilityBlock[] => {
    const blocks: WeeklyAvailabilityBlock[] = [];

    Object.entries(schedule).forEach(([day, timeBlocks]) => {
        timeBlocks.forEach((block) => {
            blocks.push({
                id: crypto.randomUUID(),
                dayOfWeek: parseInt(day, 10),
                startTime: block.start_time,
                endTime: block.end_time,
            });
        });
    });

    return blocks;
};


// Handles transformation between component block type and WeeklySchedule response
const transformToRequest = (blocks: WeeklyAvailabilityBlock[]): WeeklyScheduleRequest => {
    const weeklySchedule: Partial<Record<DayOfWeek, TimeBlock[]>> = {};

    blocks.forEach((block) => {
        const day = block.dayOfWeek.toString() as DayOfWeek;
        weeklySchedule[day] ??= [];
        weeklySchedule[day].push({
            start_time: block.startTime,
            end_time: block.endTime,
        });
    });

    return { weekly_schedule: weeklySchedule };
};

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
                const errorMessage = error instanceof Error ? error.message : String(error);
                void message.error(`Nie udało się wczytać harmonogramu: ${errorMessage}`);
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
            const errorMessage = error instanceof Error ? error.message : String(error);
            void message.error(`Nie udało się zapisać harmonogramu: ${errorMessage}`);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <Loading/>;
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24 }}>
            <Title level={2}>Harmonogram tygodniowy</Title>
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
