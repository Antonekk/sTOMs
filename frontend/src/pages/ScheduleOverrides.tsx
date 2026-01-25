import React, { useEffect, useState } from "react";
import { Button, Flex, message, Space, Typography } from "antd";
import ScheduleOverrider from "../components/storybook_components/schedule_overrider/schedule_overrider";
import type { ScheduleOverride } from "../components/storybook_components/schedule_overrider/types";
import type { ScheduleOverrideResponse, ScheduleOverrideRequest } from "../types/auth";
import { getScheduleOverrides, createScheduleOverride, deleteScheduleOverride } from "../api/auth";
import Loading from "../components/storybook_components/loading/loading";

const { Title } = Typography;

const transformToBlocks = (overrides: ScheduleOverrideResponse[]): ScheduleOverride[] => {
    return overrides.map((override) => ({
        id: override.id,
        specificDate: override.specific_date,
        startTime: override.start_time,
        endTime: override.end_time,
        type: override.availability_type,
    }));
};

const transformToRequest = (block: ScheduleOverride): ScheduleOverrideRequest => ({
    specific_date: block.specificDate,
    start_time: block.startTime,
    end_time: block.endTime,
    availability_type: block.type,
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

            // Delete removed overrides
            const toDelete = savedBlocks.filter((b) => !currentIds.has(b.id));
            for (const block of toDelete) {
                await deleteScheduleOverride(block.id);
            }

            // Create new overrides
            const toCreate = blocks.filter((b) => !savedIds.has(b.id));
            const createdBlocks: ScheduleOverride[] = [];
            for (const block of toCreate) {
                const response = await createScheduleOverride(transformToRequest(block));
                createdBlocks.push({
                    id: response.data.id,
                    specificDate: response.data.specific_date,
                    startTime: response.data.start_time,
                    endTime: response.data.end_time,
                    type: response.data.availability_type,
                });
            }

            // Update local state with server IDs
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
