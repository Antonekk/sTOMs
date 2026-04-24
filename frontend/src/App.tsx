import { ConfigProvider } from "antd";
import AppRouter from "./router/Router";
import { AuthenticationProvider } from "./auth/AuthProvider";
import { AppConfigProvider } from "./config/ConfigProvider";
import { NotificationsProvider } from "./notifications/NotificationsProvider";



const App: React.FC = () => {
  return (
    <ConfigProvider>
        <AuthenticationProvider>
          <NotificationsProvider>
            <AppConfigProvider>
              <AppRouter />
            </AppConfigProvider>
          </NotificationsProvider>
        </AuthenticationProvider>
    </ConfigProvider>
  );
}

export default App;
