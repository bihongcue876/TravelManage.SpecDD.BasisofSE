import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu, Dropdown, Avatar, Space } from 'antd'
import {
  TeamOutlined,
  AppstoreOutlined,
  FileTextOutlined,
  SettingOutlined,
  HomeOutlined,
  QuestionCircleOutlined,
  UserOutlined
} from '@ant-design/icons'
import GroupList from './pages/GroupList'
import ApplyCreate from './pages/ApplyCreate'
import AppDetail from './pages/AppDetail'
import AdminGroups from './pages/AdminGroups'
import AdminRoutes from './pages/AdminRoutes'
import DailyTasks from './pages/DailyTasks'
import HomePage from './pages/HomePage'
import HelpPage from './pages/HelpPage'
import UserProfile from './pages/UserProfile'
import './App.css'

const { Header, Content } = Layout

function App() {
  const location = useLocation()
  const navigate = useNavigate()

  const menuItems = [
    { key: '/home', label: <Link to="/home">首页</Link>, icon: <HomeOutlined /> },
    { key: '/groups', label: <Link to="/groups">旅游团查询</Link>, icon: <TeamOutlined /> },
    { key: '/admin/groups', label: <Link to="/admin/groups">管理旅游团</Link>, icon: <AppstoreOutlined /> },
    { key: '/admin/routes', label: <Link to="/admin/routes">管理路线</Link>, icon: <SettingOutlined /> },
    { key: '/admin/tasks', label: <Link to="/admin/tasks">催款与报表</Link>, icon: <FileTextOutlined /> },
    { key: '/help', label: <Link to="/help">帮助</Link>, icon: <QuestionCircleOutlined /> }
  ]

  const userMenuItems = [
    { key: 'profile', label: '个人中心', icon: <UserOutlined /> },
    { key: 'home', label: '返回首页', icon: <HomeOutlined /> }
  ]

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'profile') navigate('/user/profile')
    if (key === 'home') navigate('/home')
  }

  const selectedKey = location.pathname === '/' ? '/home' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div
          style={{ color: 'white', fontSize: 20, fontWeight: 'bold', marginRight: 40, cursor: 'pointer' }}
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
            <span>admin</span>
          </Space>
        </Dropdown>
      </Header>
      <Content style={{ padding: 24, background: '#f5f5f5' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/groups" element={<GroupList />} />
          <Route path="/apply/:groupId" element={<ApplyCreate />} />
          <Route path="/applications/:id" element={<AppDetail />} />
          <Route path="/admin/groups" element={<AdminGroups />} />
          <Route path="/admin/routes" element={<AdminRoutes />} />
          <Route path="/admin/tasks" element={<DailyTasks />} />
          <Route path="/help" element={<HelpPage />} />
          <Route path="/user/profile" element={<UserProfile />} />
        </Routes>
      </Content>
    </Layout>
  )
}

export default App
