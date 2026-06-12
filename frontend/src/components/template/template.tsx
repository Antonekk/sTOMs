import React, { type ReactNode } from 'react';
import {Badge, Layout, Menu } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { ADMIN_URL } from '../../api/endpoints';
import type { Role } from '../../types/auth';

const { Header, Content, Footer } = Layout;


interface TemplateProps {
  isAuthenticated: boolean;
  userName?: string;
  role?: Role;
  unreadNotificationCount?: number;
  onLogoutClick?: () => void;
  onNavigate: (path: string) => void;
  children: ReactNode;
};

const Template: React.FC<TemplateProps> = ({
  isAuthenticated,
  userName,
  role,
  unreadNotificationCount = 0,
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
            <Menu.Item key="panel" onClick={() => {onNavigate("/panel")}} >
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
          {isAuthenticated && role === "THERAPIST" &&
            <Menu.Item key="wizyty" onClick={() => {onNavigate("/wizyty")}} >
              Zajęcia
            </Menu.Item>
          }
          {isAuthenticated && role === "THERAPIST" &&
            <Menu.Item key="staly_grafik" onClick={() => {onNavigate("/staly_grafik")}} >
              Grafik
            </Menu.Item>
          }
          {isAuthenticated && role === "THERAPIST" &&
            <Menu.Item key="wyjatki" onClick={() => {onNavigate("/wyjatki")}} >
              Wyjątki
            </Menu.Item>
          }
          {isAuthenticated && role === "ADMIN" &&
            <Menu.Item key="admin" onClick={() => { window.location.href = ADMIN_URL; }}>
              Panel admina
            </Menu.Item>
          }
          {!isAuthenticated && (
            <>
              <Menu.Item key="login" onClick={() => { onNavigate("/login"); }} style={{ marginLeft: 'auto' }}>
                Zaloguj się
              </Menu.Item>
              <Menu.Item key="register" onClick={() => { onNavigate("/rejestracja"); }}>
                Zarejestruj się
              </Menu.Item>
            </>
          )}
          {isAuthenticated && (
            <Menu.SubMenu
              key="profile"
              icon={(
                <Badge dot={unreadNotificationCount > 0} offset={[-2, 2]}>
                  <UserOutlined />
                </Badge>
              )}
              title={userName ?? "Użytkownik"}
              style={{ marginLeft: 'auto' }}
            >
              <Menu.Item key="powiadomienia" onClick={() => { onNavigate("/powiadomienia"); }}>
                Powiadomienia
              </Menu.Item>
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