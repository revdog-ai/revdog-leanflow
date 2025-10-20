import { Layout, Menu, Switch, Space, Typography } from 'antd';
import {
  DashboardOutlined,
  LineChartOutlined,
  SettingOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { useThemeStore } from './stores/themeStore';
import BacktestPage from './pages/BacktestPage';
import LiveTradingPage from './pages/LiveTradingPage';
import ConfigurationPage from './pages/ConfigurationPage';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useThemeStore();

  const menuItems = [
    {
      key: '/backtest',
      icon: <LineChartOutlined />,
      label: 'Backtest',
    },
    {
      key: '/live',
      icon: <DashboardOutlined />,
      label: 'Live Trading',
    },
    {
      key: '/config',
      icon: <SettingOutlined />,
      label: 'Configuration',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          RevDog LeanFlow
        </Title>
        <Space>
          <BulbOutlined style={{ color: 'white' }} />
          <Switch checked={isDarkMode} onChange={toggleTheme} />
        </Space>
      </Header>
      <Layout>
        <Sider width={200} theme={isDarkMode ? 'dark' : 'light'}>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <Routes>
              <Route path="/" element={<BacktestPage />} />
              <Route path="/backtest" element={<BacktestPage />} />
              <Route path="/live" element={<LiveTradingPage />} />
              <Route path="/config" element={<ConfigurationPage />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

