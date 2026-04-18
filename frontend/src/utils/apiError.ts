import axios from "axios";

export const getApiErrorMessage = (
    err: unknown,
    fallback: string,
): string => {
    if (axios.isAxiosError(err) && err.response?.data) {
        const data = err.response.data as Record<string, unknown>;
        if (typeof data.detail === "string") {
            return data.detail;
        }
        const firstValue = Object.values(data)[0];
        if (Array.isArray(firstValue)) {
            return String(firstValue[0]);
        }
        if (firstValue !== undefined) {
            return String(firstValue);
        }
    }
    return fallback;
};
