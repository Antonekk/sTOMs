import { createContext, useContext, useEffect, useState } from "react";
import { getConfig } from "../api/auth";
import type { AppConfig } from "../types/auth";
import { message } from "antd";

interface ConfigContextType {
    config: AppConfig | null;
    loading: boolean;
}

export const ConfigContext = createContext<ConfigContextType | null>(null);

export const ConfigProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [config, setConfig] = useState<AppConfig | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const { data } = await getConfig();
                setConfig(data);
            } catch {
                message.error("Pobranie konfiguracji nie powiodło się. Spróbuj ponownie później.");
            } finally {
                setLoading(false);
            }
        };

        void fetchConfig();
    }, []);

    return (
        <ConfigContext.Provider value={{ config, loading }}>
            {children}
        </ConfigContext.Provider>
    );
};

export const useConfig = () => {
    const context = useContext(ConfigContext);
    if (!context) {
        throw new Error("useConfig must be used within a ConfigProvider");
    }
    return context;
};
