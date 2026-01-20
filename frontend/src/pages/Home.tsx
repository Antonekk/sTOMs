import { useNavigate } from 'react-router-dom';
import WelcomeScreen from '../components/storybook_components/welcome_screen/welcome_screen';

const Home: React.FC = () => {
    const navigate = useNavigate();

    return (
        <WelcomeScreen
            primaryButtonText="Zaloguj się"
            secondaryButtonText="Zarejestruj się"
            onPrimaryClick={() => { void navigate('/login'); }}
            onSecondaryClick={() => { void navigate('/rejestracja'); }}
        />
    );
};

export default Home;