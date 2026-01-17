import axios, {
    type AxiosError,
    type AxiosResponse,
    type InternalAxiosRequestConfig,
} from "axios";
import { getAccessToken, getRefreshToken, clearTokens, setAccessToken } from "./token";
import { API_URL} from "./endpoints";
import { tokenRefresh } from "./auth";

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
            data: config.data,
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

        // Check for Unauthorized and set retry flag
        if (error.response?.status === 401 && baseRequest && !baseRequest._retry) {
            baseRequest._retry = true;

            try {
                const refresh = getRefreshToken();
                if (!refresh) {
                    throw new Error("No refresh token available");
                }
                const { data } = await tokenRefresh({refresh});

                setAccessToken(data.access);
                baseRequest.headers.Authorization = `Bearer ${data.access}`;
                return await api(baseRequest);
            } catch {
                clearTokens();
                window.location.href = "/login";
            }
        }

        //Remove in prod
        console.error('Response error:', error.response ?? error);
        return Promise.reject(error);
    },
);

export default api;