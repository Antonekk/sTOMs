import { ConfigProvider } from "antd";
import AppRouter from "./router/Router";
import { AuthenticationProvider } from "./auth/AuthProvider";



const App: React.FC = () => {
  return (
    <ConfigProvider>
        <AuthenticationProvider>
          <AppRouter />
        </AuthenticationProvider>
    </ConfigProvider>
  );
}

export default App;
