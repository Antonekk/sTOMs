import React, { useEffect, useState } from "react";
import { Button, Flex, message, Space, Typography } from "antd";
import ScheduleOverrider from "../components/storybook_components/schedule_overrider/schedule_overrider";
import type { ScheduleOverride } from "../components/storybook_components/schedule_overrider/types";
import type { ScheduleOverrideResponse, ScheduleOverrideRequest } from "../types/therapistAvailability";
import {
    getScheduleOverrides,
    createScheduleOverride,
    deleteScheduleOverride,
} from "../api/therapistAvailability";
import Loading from "../components/storybook_components/loading/loading";

const { Title } = Typography;

const normalizeTime = (time: string) => time.slice(0, 5);

const transformToBlocks = (overrides: ScheduleOverrideResponse[]): ScheduleOverride[] =>
    overrides.map((override) => ({
        id: override.id,
        specificDate: override.specific_date,
        startTime: normalizeTime(override.start_time),
        endTime: normalizeTime(override.end_time),
        type: override.type,
    }));

const transformToRequest = (block: ScheduleOverride): ScheduleOverrideRequest => ({
    specific_date: block.specificDate,
    start_time: block.startTime,
    end_time: block.endTime,
    type: block.type,
});

const ScheduleOverrides: React.FC = () => {
    const [blocks, setBlocks] = useState<ScheduleOverride[]>([]);
    const [savedBlocks, setSavedBlocks] = useState<ScheduleOverride[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        const fetchOverrides = async () => {
            try {
                const response = await getScheduleOverrides();
                const fetchedBlocks = transformToBlocks(response.data);
                setBlocks(fetchedBlocks);
                setSavedBlocks(fetchedBlocks);
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                void message.error(`Nie udało się wczytać wyjątków: ${errorMessage}`);
            } finally {
                setLoading(false);
            }
        };

        void fetchOverrides();
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
            const savedIds = new Set(savedBlocks.map((b) => b.id));
            const currentIds = new Set(blocks.map((b) => b.id));

            const toDelete = savedBlocks.filter((b) => !currentIds.has(b.id));
            for (const block of toDelete) {
                await deleteScheduleOverride(block.id);
            }

            const toCreate = blocks.filter((b) => !savedIds.has(b.id));
            const createdBlocks: ScheduleOverride[] = [];
            for (const block of toCreate) {
                const response = await createScheduleOverride(transformToRequest(block));
                createdBlocks.push({
                    id: response.data.id,
                    specificDate: response.data.specific_date,
                    startTime: normalizeTime(response.data.start_time),
                    endTime: normalizeTime(response.data.end_time),
                    type: response.data.type,
                });
            }

            const updatedBlocks = blocks.map((block) => {
                const created = createdBlocks.find(
                    (c) =>
                        c.specificDate === block.specificDate &&
                        c.startTime === block.startTime &&
                        c.endTime === block.endTime &&
                        c.type === block.type
                );
                return created ?? block;
            });

            setBlocks(updatedBlocks);
            setSavedBlocks(updatedBlocks);
            setIsEditing(false);
            void message.success("Wyjątki zostały zapisane");
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            void message.error(`Nie udało się zapisać wyjątków: ${errorMessage}`);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <Loading />;
    }

    return (
        <Flex vertical gap={16} style={{ padding: 24 }}>
            <Title level={2}>Wyjątki w harmonogramie</Title>
            <ScheduleOverrider
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
                        Edytuj wyjątki
                    </Button>
                )}
            </Space>
        </Flex>
    );
};

export default ScheduleOverrides;
