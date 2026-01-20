import React, { type ReactNode } from 'react';
import {Layout, Menu } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = Layout;


interface TemplateProps {
  isAuthenticated: boolean;
  userName?: string;
  role?: "CLIENT" | "THERAPIST";
  onLogoutClick?: () => void;
  onNavigate: (path: string) => void;
  children: ReactNode;
};

const Template: React.FC<TemplateProps> = ({
  isAuthenticated,
  userName,
  role,
  onLogoutClick,
  onNavigate,
  children,
}) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', columnGap: "25px", width: "100%"}}>
        <img src="/sTOMs_logo.svg" alt="sTOMs Logo"/>
        <Menu
          theme="dark"
          mode="horizontal"
          style={{ flex: 1 }}
        >
          {isAuthenticated && 
            <Menu.Item key="panel" onClick={() => {onNavigate("/")}} >
              Panel  
            </Menu.Item>
          }
          {isAuthenticated && role === "CLIENT" && 
            <Menu.Item key="rezerwacje" onClick={() => {onNavigate("/rezerwacje")}} >
              Rezerwacje
            </Menu.Item>
          }
          {isAuthenticated && role === "CLIENT" && 
            <Menu.Item key="wizyty" onClick={() => {onNavigate("/wizyty")}} >
              Wizyty
            </Menu.Item>
          }
          {isAuthenticated && role === "CLIENT" && 
            <Menu.Item key="zadania" onClick={() => {onNavigate("/zadania_domowe")}} >
              Zadania domowe
            </Menu.Item>
          }
          {isAuthenticated && role === "THERAPIST" &&
            <Menu.Item key="staly_grafik" onClick={() => {onNavigate("/staly_grafik")}} >
              Grafik
            </Menu.Item>
          }
          {isAuthenticated && (
            <Menu.SubMenu
              key="profile"
              icon={<UserOutlined />}
              title={userName ?? "Użytkownik"}
              style={{ marginLeft: 'auto' }}
            >
              <Menu.Item key="profil" onClick={() => { onNavigate("/profil"); }}>
                Profil
              </Menu.Item>
              <Menu.Item key="wyloguj" onClick={onLogoutClick}>
                Wyloguj
              </Menu.Item>
            </Menu.SubMenu>
          )}
        </Menu>

      </Header>
      <Content style={{ padding: '24px 12px'}}>
        {children}
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        sTOMs ©{new Date().getFullYear()} Antoni Strasz
      </Footer>
    </Layout>
  );
};

export default Template;