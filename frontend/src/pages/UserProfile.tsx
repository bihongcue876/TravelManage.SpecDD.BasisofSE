import { useState } from 'react'
import { Card, Descriptions, Select, Typography, Avatar, Tag, Divider } from 'antd'
import { UserOutlined, TeamOutlined, DollarOutlined, SettingOutlined } from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography

const roleOptions = [
  { value: 'frontdesk', label: '前台员工', icon: <TeamOutlined /> },
  { value: 'collector', label: '催款员工', icon: <DollarOutlined /> },
  { value: 'admin', label: '路线管理员', icon: <SettingOutlined /> }
]

const demoEmployee = {
  name: '张前台',
  phone: '13800138000',
  email: 'zhang@travel.com',
  department: '业务部',
  role: 'frontdesk'
}

function UserProfile() {
  const [role, setRole] = useState(demoEmployee.role)

  const currentRole = roleOptions.find((r) => r.value === role)

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: 32, marginTop: 24 }}>
        <Avatar size={80} icon={<UserOutlined />} style={{ backgroundColor: '#1677ff', marginBottom: 16 }} />
        <Title level={3}>{demoEmployee.name}</Title>
        <Paragraph style={{ color: '#666' }}>
          {demoEmployee.department} · {currentRole?.label}
        </Paragraph>
      </div>

      <Card title="个人信息" style={{ marginBottom: 24 }}>
        <Descriptions column={{ xs: 1, sm: 2 }}>
          <Descriptions.Item label="姓名">{demoEmployee.name}</Descriptions.Item>
          <Descriptions.Item label="部门">{demoEmployee.department}</Descriptions.Item>
          <Descriptions.Item label="电话">{demoEmployee.phone}</Descriptions.Item>
          <Descriptions.Item label="邮箱">{demoEmployee.email}</Descriptions.Item>
          <Descriptions.Item label="当前角色">
            <Tag color="blue">{currentRole?.label}</Tag>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="角色切换（演示功能）">
        <Paragraph style={{ color: '#666', marginBottom: 16 }}>
          切换角色后可体验不同角色的功能权限。当前为演示模式，角色切换仅影响页面导航展示。
        </Paragraph>
        <Select
          value={role}
          onChange={setRole}
          style={{ width: 200 }}
          options={roleOptions}
        />
        <Divider />
        <div>
          <Paragraph style={{ marginBottom: 8 }}><Text strong>各角色功能说明：</Text></Paragraph>
          {roleOptions.map((r) => (
            <div key={r.value} style={{ marginBottom: 8 }}>
              <Tag
                color={role === r.value ? 'blue' : 'default'}
                style={{ marginRight: 8 }}
              >
                {r.icon} {r.label}
              </Tag>
              <span style={{ color: '#666' }}>
                {r.value === 'frontdesk' && '查询旅游团、创建申请、录入参加者、管理支付'}
                {r.value === 'collector' && '查看催款清单、财务流水、导出报表'}
                {r.value === 'admin' && '管理路线、管理旅游团、发布价格'}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

export default UserProfile
