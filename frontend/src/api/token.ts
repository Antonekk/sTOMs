import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";

export const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN);
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN);

export const setTokens = (access: string, refresh: string) => {
  localStorage.setItem(ACCESS_TOKEN, access);
  localStorage.setItem(REFRESH_TOKEN, refresh);
};

export const setAccessToken = (access: string) => {
  localStorage.setItem(ACCESS_TOKEN, access)
}
export const setRefreshToken = (refresh: string) => {
  localStorage.setItem(REFRESH_TOKEN, refresh)
}

export const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN);
  localStorage.removeItem(REFRESH_TOKEN);
};