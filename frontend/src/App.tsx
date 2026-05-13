import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import { TeamOutlined, AppstoreOutlined, FileTextOutlined, SettingOutlined } from '@ant-design/icons'
import GroupList from './pages/GroupList'
import ApplyCreate from './pages/ApplyCreate'
import AppDetail from './pages/AppDetail'
import AdminGroups from './pages/AdminGroups'
import AdminRoutes from './pages/AdminRoutes'
import DailyTasks from './pages/DailyTasks'
import './App.css'

const { Header, Content } = Layout

function App() {
  const location = useLocation()

  const menuItems = [
    { key: '/', label: <Link to="/">旅游团查询</Link>, icon: <TeamOutlined /> },
    { key: '/admin/groups', label: <Link to="/admin/groups">管理旅游团</Link>, icon: <AppstoreOutlined /> },
    { key: '/admin/routes', label: <Link to="/admin/routes">管理路线</Link>, icon: <SettingOutlined /> },
    { key: '/admin/tasks', label: <Link to="/admin/tasks">催款与报表</Link>, icon: <FileTextOutlined /> }
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontSize: 20, fontWeight: 'bold', marginRight: 40 }}>
          旅游业务管理系统
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ flex: 1 }}
        />
      </Header>
      <Content style={{ padding: 24 }}>
        <Routes>
          <Route path="/" element={<GroupList />} />
          <Route path="/apply/:groupId" element={<ApplyCreate />} />
          <Route path="/applications/:id" element={<AppDetail />} />
          <Route path="/admin/groups" element={<AdminGroups />} />
          <Route path="/admin/routes" element={<AdminRoutes />} />
          <Route path="/admin/tasks" element={<DailyTasks />} />
        </Routes>
      </Content>
    </Layout>
  )
}

export default App
