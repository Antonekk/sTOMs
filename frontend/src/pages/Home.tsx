import { CalendarOutlined, FormOutlined } from "@ant-design/icons"
import { Col, Flex, Row } from "antd"
import { useNavigate } from "react-router-dom"
import ActionCard from "../components/action_card/action_card"
import WelcomeScreen from "../components/welcome_screen/welcome_screen"
import { useAuthentication } from "../auth/AuthProvider"

const Home: React.FC = () => {
    const navigate = useNavigate()
    const { isAuthenticated, user } = useAuthentication()

    if (!isAuthenticated) {
        return (
            <WelcomeScreen
                primaryButtonText="Zaloguj się"
                secondaryButtonText="Zarejestruj się"
                onPrimaryClick={() => { void navigate("/login"); }}
                onSecondaryClick={() => { void navigate("/rejestracja"); }}
            />
        )
    }

    if (user?.role === "CLIENT") {
        return (
            <Flex vertical gap={24} style={{ padding: 24, maxWidth: 960, margin: "0 auto" }}>
                <Row gutter={[16, 16]}>
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<FormOutlined />}
                            iconBgColor="#1677ff"
                            title="Nowa rezerwacja"
                            description="Zarezerwuj termin jednorazowy lub cykliczny dla wybranego pacjenta."
                            buttonText="Rezerwuj"
                            onButtonClick={() => { void navigate("/rezerwacje/nowa"); }}
                        />
                    </Col>
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<CalendarOutlined />}
                            iconBgColor="#52c41a"
                            title="Moje wizyty"
                            description="Przeglądaj nadchodzące i historyczne wizyty, anuluj zaplanowane terminy."
                            buttonText="Zobacz wizyty"
                            onButtonClick={() => { void navigate("/wizyty"); }}
                        />
                    </Col>
                </Row>
            </Flex>
        )
    }

    if (user?.role === "THERAPIST") {
        return (
            <Flex vertical gap={24} style={{ padding: 24, maxWidth: 960, margin: "0 auto" }}>
                <Row gutter={[16, 16]}>
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<CalendarOutlined />}
                            iconBgColor="#1677ff"
                            title="Moje zajęcia"
                            description="Lista wizyt, zmiana statusu i notatki terapeuty."
                            buttonText="Otwórz zajęcia"
                            onButtonClick={() => { void navigate("/wizyty"); }}
                        />
                    </Col>
                </Row>
            </Flex>
        )
    }

    return (
        <WelcomeScreen
            primaryButtonText="Panel"
            secondaryButtonText="Profil"
            onPrimaryClick={() => { void navigate("/panel"); }}
            onSecondaryClick={() => { void navigate("/profil"); }}
        />
    )
}

export default Home
