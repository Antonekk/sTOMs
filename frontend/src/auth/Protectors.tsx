import { Navigate } from "react-router-dom";
import { useAuthentication } from "./AuthProvider";
import type { Role } from "../types/auth";
import AuthLoading from "../components/storybook_components/auth_loading/auth_loading";


// Protect routes for authenticated users
export const AuthenticatedRoute = ({ children }: { children: React.ReactNode }) => {
    const { loading, isAuthenticated } = useAuthentication();

    if(loading){
        return <AuthLoading></AuthLoading>
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    return children;
};


// Protect routes for non authenticated users
export const NonAuthenticatedRoute = ({ children }: { children: React.ReactNode }) => {
    const { loading, isAuthenticated } = useAuthentication();

    if(loading){
        return <AuthLoading></AuthLoading>
    }

    return !isAuthenticated ? children : <Navigate to="/panel" replace />;
};

// Protect routes for specific roles
export const RoleRoute = ({ children, role }: { children: React.ReactNode, role: Role }) => {
    const { loading, isAuthenticated, checkRole } = useAuthentication();

    if(loading){
        return <AuthLoading></AuthLoading>
    }

    if (!checkRole(role) && !isAuthenticated) {
        return <Navigate to="/login" />;
    }

    return children;
};