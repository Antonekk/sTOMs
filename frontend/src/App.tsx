import { ConfigProvider } from "antd";
import AppRouter from "./router/Router";
import { AuthenticationProvider } from "./auth/AuthProvider";
import { AppConfigProvider } from "./config/ConfigProvider";



const App: React.FC = () => {
  return (
    <ConfigProvider>
        <AuthenticationProvider>
          <AppConfigProvider>
            <AppRouter />
          </AppConfigProvider>
        </AuthenticationProvider>
    </ConfigProvider>
  );
}

export default App;
