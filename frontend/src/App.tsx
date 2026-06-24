import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu, Dropdown, Avatar, Space, Spin, App as AntApp, ConfigProvider, Tag, Button } from 'antd'
import {
  TeamOutlined,
  AppstoreOutlined,
  FileTextOutlined,
  SettingOutlined,
  HomeOutlined,
  QuestionCircleOutlined,
  UserOutlined,
  LoginOutlined,
  BankOutlined,
  LockOutlined,
} from '@ant-design/icons'
import { useState, useEffect } from 'react'
import { useAuth, UserRole } from './auth'
import Login from './pages/Login'
import GroupList from './pages/GroupList'
import ApplyWizard from './pages/ApplyWizard'
import AppDetail from './pages/AppDetail'
import AdminGroups from './pages/AdminGroups'
import AdminRoutes from './pages/AdminRoutes'
import DailyTasks from './pages/DailyTasks'
import HomePage from './pages/HomePage'
import HelpPage from './pages/HelpPage'
import UserProfile from './pages/UserProfile'
import UserManagement from './pages/UserManagement'
import './App.css'

const { Header, Content } = Layout

const roleMenuMap: Record<UserRole, string[]> = {
  admin: ['/home', '/groups', '/admin/groups', '/admin/routes', '/admin/tasks', '/admin/users'],
  frontdesk: ['/home', '/groups'],
  finance: ['/home', '/admin/tasks'],
}

const roleNameMap: Record<string, string> = {
  admin: '系统管理员',
  frontdesk: '前台员工',
  finance: '财务人员',
}

const roleColorMap: Record<string, string> = {
  admin: '#0F5B5C',
  frontdesk: '#1677ff',
  finance: '#52c41a',
}

const allMenuItems = [
  { key: '/home', label: '首页', icon: <HomeOutlined /> },
  { key: '/groups', label: '旅游团查询', icon: <TeamOutlined /> },
  { key: '/admin/groups', label: '管理旅游团', icon: <AppstoreOutlined /> },
  { key: '/admin/routes', label: '管理路线', icon: <BankOutlined /> },
  { key: '/admin/tasks', label: '催款与报表', icon: <FileTextOutlined /> },
  { key: '/admin/users', label: '用户管理', icon: <SettingOutlined /> },
  { key: '/help', label: '帮助', icon: <QuestionCircleOutlined /> },
]

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth()

  const [, setLogoutSignal] = useState(0)
  useEffect(() => {
    const handler = () => setLogoutSignal(n => n + 1)
    window.addEventListener('auth:logout', handler)
    return () => window.removeEventListener('auth:logout', handler)
  }, [])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>
  }

  if (!isAuthenticated) {
    return <Login />
  }

  return <>{children}</>
}

function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout, hasRole } = useAuth()

  const allowedKeys = user ? roleMenuMap[user.role] || [] : []
  const menuItems = allMenuItems
    .filter(item => allowedKeys.includes(item.key))
    .map(item => ({ ...item, label: <Link to={item.key}>{item.label}</Link> }))

  const userMenuItems = [
    { key: 'profile', label: '个人中心', icon: <UserOutlined /> },
    { key: 'change-password', label: '修改密码', icon: <LockOutlined /> },
    { key: 'logout', label: '退出登录', icon: <LoginOutlined /> },
  ]

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'profile') navigate('/user/profile')
    if (key === 'change-password') navigate('/user/profile')
    if (key === 'logout') {
      logout()
      navigate('/login')
    }
  }

  const selectedKey = location.pathname === '/' ? '/home' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{
        background: '#fff',
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div
          style={{
            color: '#0F5B5C',
            fontSize: 18,
            fontWeight: 700,
            marginRight: 32,
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            letterSpacing: 1,
          }}
          onClick={() => navigate('/home')}
        >
          旅游业务管理系统
        </div>
        <Menu
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={menuItems}
          style={{ flex: 1, minWidth: 0, borderBottom: 'none' }}
        />
        <Space size={12} style={{ marginLeft: 'auto' }}>
          <Tag color={roleColorMap[user?.role || 'admin']} style={{ margin: 0, fontSize: 12 }}>
            {user ? roleNameMap[user.role] || user.role : ''}
          </Tag>
          <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenuClick }} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar size="small" icon={<UserOutlined />} style={{ backgroundColor: '#0F5B5C' }} />
              <span style={{ color: '#333', fontSize: 14 }}>{user?.name || user?.username}</span>
            </Space>
          </Dropdown>
          <Button
            type="text"
            icon={<LoginOutlined />}
            onClick={() => { logout(); navigate('/login') }}
            style={{ color: '#999' }}
          />
        </Space>
      </Header>
      <Content style={{ padding: 24, background: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/groups" element={
            hasRole('frontdesk', 'admin') ? <GroupList /> : <div style={{ padding: 48, textAlign: 'center' }}>无权限访问</div>
          } />
          <Route path="/apply/:groupId" element={<ApplyWizard />} />
          <Route path="/applications/:id" element={<AppDetail />} />
          <Route path="/admin/groups" element={
            hasRole('admin') ? <AdminGroups /> : <div style={{ padding: 48, textAlign: 'center' }}>无权限访问</div>
          } />
          <Route path="/admin/routes" element={
            hasRole('admin') ? <AdminRoutes /> : <div style={{ padding: 48, textAlign: 'center' }}>无权限访问</div>
          } />
          <Route path="/admin/tasks" element={
            hasRole('finance', 'admin') ? <DailyTasks /> : <div style={{ padding: 48, textAlign: 'center' }}>无权限访问</div>
          } />
          <Route path="/admin/users" element={
            hasRole('admin') ? <UserManagement /> : <div style={{ padding: 48, textAlign: 'center' }}>无权限访问</div>
          } />
          <Route path="/help" element={<HelpPage />} />
          <Route path="/user/profile" element={<UserProfile />} />
        </Routes>
      </Content>
    </Layout>
  )
}

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#0F5B5C',
          borderRadius: 8,
          colorBgContainer: '#ffffff',
          boxShadow: '0 1px 6px rgba(0,0,0,0.08)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif',
        },
        components: {
          Card: {
            boxShadowTertiary: '0 1px 6px rgba(0,0,0,0.06)',
          },
          Button: {
            borderRadius: 8,
          },
        },
      }}
    >
      <AntApp>
        <ProtectedRoute>
          <AppLayout />
        </ProtectedRoute>
      </AntApp>
    </ConfigProvider>
  )
}

export default App
