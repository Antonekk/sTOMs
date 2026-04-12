import { Alert, Flex } from "antd";
import UserProfile from "../components/storybook_components/user_profile/user_profile";
import { useAuthentication } from "../auth/AuthProvider";

const Profile: React.FC = () => {
    const { user } = useAuthentication();

    if (!user) {
        return (
            <Flex justify="center" style={{ padding: 24 }}>
                <Alert
                    type="warning"
                    showIcon
                    title="Nie udało się wczytać danych profilu"
                />
            </Flex>
        );
    }

    return (
        <Flex justify="center" style={{ padding: 24 }}>
            <div style={{ width: "100%", maxWidth: 960 }}>
                <UserProfile user={user} />
            </div>
        </Flex>
    );
};

export default Profile;
