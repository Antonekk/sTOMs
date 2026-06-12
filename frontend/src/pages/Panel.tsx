import {
    BellOutlined,
    CalendarOutlined,
    ExceptionOutlined,
    FormOutlined,
    ScheduleOutlined,
    SettingOutlined,
    UnorderedListOutlined,
    UserOutlined,
} from "@ant-design/icons"
import { Col, Flex, Row, Typography } from "antd"
import { useNavigate } from "react-router-dom"
import { ADMIN_URL } from "../api/endpoints"
import ActionCard from "../components/action_card/action_card"
import { useAuthentication } from "../auth/AuthProvider"

const { Title, Text } = Typography

const panelStyle = { padding: 24, maxWidth: 960, margin: "0 auto" } as const

const Panel: React.FC = () => {
    const navigate = useNavigate()
    const { user } = useAuthentication()

    const greeting = user?.first_name ? `Witaj, ${user.first_name}!` : "Witaj w panelu"

    const header = (
        <Flex vertical gap={4}>
            <Title level={2} style={{ margin: 0 }}>{greeting}</Title>
            <Text type="secondary">Wybierz akcję, aby kontynuować.</Text>
        </Flex>
    )

    if (user?.role === "CLIENT") {
        return (
            <Flex vertical gap={24} style={panelStyle}>
                {header}
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
                            icon={<UnorderedListOutlined />}
                            iconBgColor="#722ed1"
                            title="Moje rezerwacje"
                            description="Przeglądaj aktywne i zakończone serie rezerwacji, anuluj zaplanowane terminy."
                            buttonText="Zobacz rezerwacje"
                            onButtonClick={() => { void navigate("/rezerwacje"); }}
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
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<UserOutlined />}
                            iconBgColor="#fa8c16"
                            title="Profil i pacjenci"
                            description="Edytuj dane konta oraz zarządzaj profilami pacjentów przypisanych do konta."
                            buttonText="Otwórz profil"
                            onButtonClick={() => { void navigate("/profil"); }}
                        />
                    </Col>
                </Row>
            </Flex>
        )
    }

    if (user?.role === "THERAPIST") {
        return (
            <Flex vertical gap={24} style={panelStyle}>
                {header}
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
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<ScheduleOutlined />}
                            iconBgColor="#52c41a"
                            title="Grafik tygodniowy"
                            description="Ustal stałe godziny dostępności na poszczególne dni tygodnia."
                            buttonText="Edytuj grafik"
                            onButtonClick={() => { void navigate("/staly_grafik"); }}
                        />
                    </Col>
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<ExceptionOutlined />}
                            iconBgColor="#fa8c16"
                            title="Wyjątki w harmonogramie"
                            description="Dodaj urlopy, dni wolne lub zmiany godzin poza stałym grafikiem."
                            buttonText="Zarządzaj wyjątkami"
                            onButtonClick={() => { void navigate("/wyjatki"); }}
                        />
                    </Col>
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<BellOutlined />}
                            iconBgColor="#13c2c2"
                            title="Powiadomienia"
                            description="Sprawdź przypomnienia o zajęciach i inne komunikaty systemowe."
                            buttonText="Zobacz powiadomienia"
                            onButtonClick={() => { void navigate("/powiadomienia"); }}
                        />
                    </Col>
                </Row>
            </Flex>
        )
    }

    if (user?.role === "ADMIN") {
        return (
            <Flex vertical gap={24} style={panelStyle}>
                {header}
                <Row gutter={[16, 16]}>
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<SettingOutlined />}
                            iconBgColor="#cf1322"
                            title="Panel administracyjny"
                            description="Zarządzaj użytkownikami, gabinetami, rezerwacjami i innymi zasobami systemu."
                            buttonText="Otwórz panel admina"
                            onButtonClick={() => { window.location.href = ADMIN_URL; }}
                        />
                    </Col>
                    <Col xs={24} md={12}>
                        <ActionCard
                            icon={<UserOutlined />}
                            iconBgColor="#1677ff"
                            title="Profil"
                            description="Przeglądaj dane swojego konta administratora."
                            buttonText="Otwórz profil"
                            onButtonClick={() => { void navigate("/profil"); }}
                        />
                    </Col>
                </Row>
            </Flex>
        )
    }

    return null
}

export default Panel
