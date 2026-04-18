import { createContext, useContext, useEffect, useState } from "react";
import { clearTokens, getAccessToken, setTokens } from "../api/token";
import { login as loginAPI, getMe } from "../api/auth";
import type { User } from "../types/auth";
import type {Role, LoginData} from "../types/auth";



interface AuthenticatedContextType{
    user: User | null;
    loading: boolean;
    login: (login_params: LoginData) => Promise<void>;
    logout: () => void;
    refreshUser: () => Promise<void>;
    isAuthenticated: boolean;
    checkRole: (role: Role) => boolean;
}

export const AuthenticationContext = createContext<AuthenticatedContextType | null>(null);

export const AuthenticationProvider: React.FC< {children: React.ReactNode}> = ({children}) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    const populateUser = async () => {
        try{
            const token = getAccessToken();
            if (!token) {
                setLoading(false);
                return;
            }
            const res = await getMe();
            setUser(res.data);
        } catch{
            clearTokens();
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        populateUser().catch(console.error);
    }, []);

    const refreshUser = async () => {
        const token = getAccessToken();
        if (!token) {
            setUser(null);
            return;
        }
        const res = await getMe();
        setUser(res.data);
    };

    const login = async (login_params: LoginData) => {
        try{
            const {data} = await loginAPI(login_params);
            setTokens(data.access, data.refresh);
            await populateUser();
        } catch (err){
            clearTokens();
            setUser(null);
            throw err;
        }
    };

    const logout = () => {
        clearTokens();
        setUser(null);
    };

    const checkRole = (role: Role) => {
        return user?.role === role;
    }

    return (
        <AuthenticationContext.Provider 
            value={{
                user,
                loading,
                login,
                logout,
                refreshUser,
                isAuthenticated: !!user, 
                checkRole}}>
            {children}
        </AuthenticationContext.Provider>
    )

}

export const useAuthentication = () => {
    const context = useContext(AuthenticationContext);
    if (!context) {
        throw new Error("useAuthentication must be used within an AuthenticationProvider");
    }
    return context;
}




