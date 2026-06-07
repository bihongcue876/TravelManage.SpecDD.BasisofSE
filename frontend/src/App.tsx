import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu, Dropdown, Avatar, Space, Spin, App as AntApp } from 'antd'
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
} from '@ant-design/icons'
import { useState, useEffect } from 'react'
import { useAuth, UserRole } from './auth'
import Login from './pages/Login'
import GroupList from './pages/GroupList'
import ApplyCreate from './pages/ApplyCreate'
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

// 菜单权限配置：角色可访问的菜单 key
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

  // 监听 auth:logout 事件，当 axios 拦截器清除 token 时强制重渲染
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

  // 根据角色过滤可见菜单
  const allowedKeys = user ? roleMenuMap[user.role] || [] : []
  const menuItems = allMenuItems
    .filter(item => allowedKeys.includes(item.key))
    .map(item => ({ ...item, label: <Link to={item.key}>{item.label}</Link> }))

  const userMenuItems = [
    { key: 'profile', label: '个人中心', icon: <UserOutlined /> },
    { key: 'logout', label: '退出登录', icon: <LoginOutlined /> },
  ]

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'profile') navigate('/user/profile')
    if (key === 'logout') {
      logout()
      navigate('/login')
    }
  }

  const selectedKey = location.pathname === '/' ? '/home' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div
          style={{ color: 'white', fontSize: 20, fontWeight: 'bold', marginRight: 40, cursor: 'pointer', whiteSpace: 'nowrap' }}
          onClick={() => navigate('/home')}
        >
          旅游业务管理系统
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={menuItems}
          style={{ flex: 1, minWidth: 0 }}
        />
        <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenuClick }} placement="bottomRight">
          <Space style={{ cursor: 'pointer', color: 'white' }}>
            <Avatar size="small" icon={<UserOutlined />} style={{ backgroundColor: '#87d068' }} />
            <span>{user?.name || user?.username}</span>
            <span style={{ fontSize: 12, opacity: 0.7 }}>
              {user ? roleNameMap[user.role] || user.role : ''}
            </span>
          </Space>
        </Dropdown>
      </Header>
      <Content style={{ padding: 24, background: '#f5f5f5' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/groups" element={
            hasRole('frontdesk', 'admin') ? <GroupList /> : <div style={{ padding: 48, textAlign: 'center' }}>无权限访问</div>
          } />
          <Route path="/apply/:groupId" element={<ApplyCreate />} />
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
    <AntApp>
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    </AntApp>
  )
}

export default App
