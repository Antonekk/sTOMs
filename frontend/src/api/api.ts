import axios, {
    type AxiosError,
    type AxiosResponse,
    type InternalAxiosRequestConfig,
} from "axios";
import { getAccessToken, getRefreshToken, clearTokens, setAccessToken } from "./token";
import { API_URL, AUTH_ENDPOINTS } from "./endpoints";
import { tokenRefresh } from "./auth";

const isRefreshRequest = (config: InternalAxiosRequestConfig) =>
    config.url?.includes(AUTH_ENDPOINTS.REFRESH) ?? false;

declare module "axios" {
    interface AxiosRequestConfig {
        _retry?: boolean;
    }
}


const api = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    },
    withCredentials: false,
});


api.interceptors.request.use(
    (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
        const token = getAccessToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        // Remove in prod
        console.log('Request:', {
            url: config.url,
            method: config.method,
            headers: config.headers,
            data: config.data as unknown,
        });
        return config;
    },
);

// Handles failed requests by refreshing jwt token
api.interceptors.response.use(
    (response: AxiosResponse): AxiosResponse => {
        console.log('Response:', response);
        return response;
    },
    async (error: AxiosError): Promise<AxiosResponse> => {
        const baseRequest = error.config;

        if (error.response?.status === 401 && baseRequest) {
            if (isRefreshRequest(baseRequest)) {
                clearTokens();
                return Promise.reject(error);
            }

            if (!baseRequest._retry) {
                baseRequest._retry = true;

                try {
                    const refresh = getRefreshToken();
                    if (!refresh) {
                        throw new Error("No refresh token available");
                    }
                    const { data } = await tokenRefresh({ refresh });

                    setAccessToken(data.access);
                    baseRequest.headers.Authorization = `Bearer ${data.access}`;
                    return await api(baseRequest);
                } catch {
                    clearTokens();
                    return Promise.reject(error);
                }
            }

            clearTokens();
        }

        //Remove in prod
        console.error('Response error:', error.response ?? error);
        return Promise.reject(error);
    },
);

export default api;