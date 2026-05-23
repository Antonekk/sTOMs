import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import { useState, useEffect } from "react";
import {ACCESS_TOKEN, REFRESH_TOKEN} from "../constants";
import api from "../api/api"
import { AUTH_ENDPOINTS } from "../api/endpoints"
import Loading from "../components/loading/loading";

interface ProtectedRouteProps {
    children: React.ReactNode;
}

interface JwtPayload {
  exp: number;
  access: string;
}

// This component is used for rendering protected routes. If it is unable to authenticate, ProtectedRoute redirects to login page
const ProtectedRoute : React.FC<ProtectedRouteProps> = ({ children }) => {
    const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);

    // Authenticate
    useEffect(() => {
        auth().catch(() => {
            setIsAuthorized(false);
        });
    }, []);


    // Refresh token logic
    const refreshToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        try{
            const res = await api.post<JwtPayload>(AUTH_ENDPOINTS.REFRESH, {refresh: refreshToken});

            if(res.status === 200){
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                setIsAuthorized(true);
            } else {
                setIsAuthorized(false);
            }
        } catch(err){
            console.log(err);
            setIsAuthorized(false);
        }
    }

    // Authentication logic
    const auth = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false);
            return;
        }

        const decoded = jwtDecode<JwtPayload>(token);
        const tokenExpirationDate = decoded.exp;
        const now = Date.now() / 1000;

        if (tokenExpirationDate < now) {
            await refreshToken();
        } else {
            setIsAuthorized(true);
        }
    }

    // Render loading screen if authentication is in process
    if(isAuthorized === null){
        return <Loading />
    }

    // Render children if authentication is successful else navigate to login page
    return isAuthorized ? children : <Navigate to="/login" />;
};

export default ProtectedRoute;