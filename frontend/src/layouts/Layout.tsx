import { Outlet, useNavigate } from "react-router-dom";
import { useAuthentication } from "../auth/AuthProvider";
import Template from "../components/storybook_components/template/template";


const Layout = () => {
    const { user, isAuthenticated, logout } = useAuthentication();
    const navigate = useNavigate();

    return (
        <Template
            isAuthenticated={isAuthenticated}
            userName={user?.first_name}
            role={user?.role}
            onLogoutClick={() => {
                logout();
                void navigate("/login");
            }}
            onNavigate={(path) => { void navigate(path); }}
        >
            <Outlet />
        </Template>
    )

}

export default Layout;


