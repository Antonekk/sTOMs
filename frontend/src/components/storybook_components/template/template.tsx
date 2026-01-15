import React from 'react';
import {Layout, Menu } from 'antd';
import type { ItemType } from 'antd/es/menu/interface';

const { Header, Content, Footer } = Layout;


interface TemplateProps {
    menu_items?: ItemType[] | undefined;
    children?: React.ReactNode;
};

export default function Template({
  menu_items,
  children,
}: TemplateProps) {

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', columnGap: "25px"}}>
        <img src="/sTOMs_logo.svg" alt="sTOMs Logo"/>
        <Menu
          theme="dark"
          mode="horizontal"
          defaultSelectedKeys={['2']}
          items={menu_items}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      <Content style={{ padding: '24px 12px' }}>
        
          {children}

      </Content>
      <Footer style={{ textAlign: 'center' }}>
        sTOMs ©{new Date().getFullYear()} Created by Antoni Strasz
      </Footer>
    </Layout>
  );
};
