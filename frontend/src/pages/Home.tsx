import { Navigate, useNavigate } from "react-router-dom"
import WelcomeScreen from "../components/welcome_screen/welcome_screen"
import { useAuthentication } from "../auth/AuthProvider"

const Home: React.FC = () => {
    const navigate = useNavigate()
    const { isAuthenticated } = useAuthentication()

    if (isAuthenticated) {
        return <Navigate to="/panel" replace />
    }

    return (
        <WelcomeScreen
            primaryButtonText="Zaloguj się"
            secondaryButtonText="Zarejestruj się"
            onPrimaryClick={() => { void navigate("/login"); }}
            onSecondaryClick={() => { void navigate("/rejestracja"); }}
        />
    )
}

export default Home
