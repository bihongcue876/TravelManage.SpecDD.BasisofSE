import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, Typography, Space, Tag } from 'antd'
import { UserOutlined, LockOutlined, GlobalOutlined } from '@ant-design/icons'
import { useAuth } from '../auth'
import { App as AntApp } from 'antd'

const { Title, Text } = Typography

const presetAccounts = [
  { username: 'admin', password: 'admin123', role: '管理员', color: 'red' },
  { username: 'frontdesk', password: '123456', role: '前台', color: 'blue' },
  { username: 'finance', password: '123456', role: '财务', color: 'green' },
]

function Login() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()
  const { message } = AntApp.useApp()

  if (isAuthenticated) {
    navigate('/home', { replace: true })
  }

  const handleSubmit = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      await login(values.username, values.password)
      message.success('登录成功')
      navigate('/home', { replace: true })
    } catch (err: any) {
      message.error(err.message || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  const handlePresetClick = (account: typeof presetAccounts[0]) => {
    form.setFieldsValue({ username: account.username, password: account.password })
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #0F5B5C 0%, #1a8a8b 100%)',
      }}
    >
      <Card style={{ width: 440, borderRadius: 8, boxShadow: '0 4px 24px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <GlobalOutlined style={{ fontSize: 48, color: '#0F5B5C', marginBottom: 16 }} />
          <Title level={3} style={{ marginBottom: 4 }}>旅游业务管理系统</Title>
          <Text type="secondary">请登录您的账户</Text>
        </div>

        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
          initialValues={{ username: '', password: '' }}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登 录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ marginTop: 8 }}>
          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
            快捷登录（点击自动填充）
          </Text>
          <Space wrap>
            {presetAccounts.map(account => (
              <Tag
                key={account.username}
                color={account.color}
                style={{ cursor: 'pointer', fontSize: 13, padding: '4px 12px' }}
                onClick={() => handlePresetClick(account)}
              >
                {account.role}: {account.username}
              </Tag>
            ))}
          </Space>
        </div>
      </Card>
    </div>
  )
}

export default Login
