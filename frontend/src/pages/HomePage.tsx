import { useNavigate } from 'react-router-dom'
import { Card, Row, Col, Typography, Space } from 'antd'
import {
  TeamOutlined,
  DollarOutlined,
  SettingOutlined,
  GlobalOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons'

const { Title, Paragraph } = Typography

const roleCards = [
  {
    title: '前台员工',
    description: '查询旅游团、创建申请、录入参加者信息、管理支付',
    icon: <TeamOutlined style={{ fontSize: 48, color: '#1677ff' }} />,
    links: [
      { label: '查询旅游团', path: '/groups' },
      { label: '创建申请', path: '/apply' },
      { label: '查看帮助', path: '/help' }
    ]
  },
  {
    title: '催款员工',
    description: '管理催款单、查看财务流水、导出报表',
    icon: <DollarOutlined style={{ fontSize: 48, color: '#1677ff' }} />,
    links: [
      { label: '催款与报表', path: '/admin/tasks' },
      { label: '查看帮助', path: '/help' }
    ]
  },
  {
    title: '路线管理员',
    description: '管理旅游路线、管理旅游团、发布价格',
    icon: <SettingOutlined style={{ fontSize: 48, color: '#1a7e5a' }} />,
    links: [
      { label: '管理路线', path: '/admin/routes' },
      { label: '管理旅游团', path: '/admin/groups' }
    ]
  }
]

function HomePage() {
  const navigate = useNavigate()

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: 48, marginTop: 24 }}>
        <GlobalOutlined style={{ fontSize: 64, color: '#1677ff', marginBottom: 16 }} />
        <Title level={2}>欢迎使用旅游业务管理系统</Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          高效管理旅游团、申请单、支付与催款流程
        </Paragraph>
      </div>

      <Row gutter={[24, 24]}>
        {roleCards.map((role) => (
          <Col xs={24} sm={12} md={8} key={role.title}>
            <Card
              hoverable
              style={{ height: '100%', borderRadius: 8 }}
              styles={{ body: { display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', height: '100%' } }}
            >
              <div style={{ marginBottom: 16 }}>{role.icon}</div>
              <Title level={4}>{role.title}</Title>
              <Paragraph style={{ color: '#666', marginBottom: 16 }}>{role.description}</Paragraph>
              <Space direction="vertical" style={{ width: '100%' }}>
                {role.links.map((link) => (
                  <Card
                    key={link.path}
                    size="small"
                    hoverable
                    onClick={() => navigate(link.path)}
                    style={{ width: '100%', textAlign: 'center' }}
                  >
                    {link.label}
                  </Card>
                ))}
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24, marginBottom: 48 }}>
        <Col xs={24} sm={12}>
          <Card
            hoverable
            onClick={() => navigate('/help')}
            style={{ borderRadius: 8 }}
          >
            <Space align="center" style={{ width: '100%', justifyContent: 'center' }}>
              <QuestionCircleOutlined style={{ fontSize: 24, color: '#1677ff' }} />
              <span style={{ fontSize: 16 }}>使用帮助</span>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card
            hoverable
            onClick={() => navigate('/user/profile')}
            style={{ borderRadius: 8 }}
          >
            <Space align="center" style={{ width: '100%', justifyContent: 'center' }}>
              <TeamOutlined style={{ fontSize: 24, color: '#1677ff' }} />
              <span style={{ fontSize: 16 }}>个人中心</span>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default HomePage
