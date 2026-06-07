import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, message, Typography } from 'antd'
import { UserOutlined, LockOutlined, GlobalOutlined } from '@ant-design/icons'
import { useAuth } from '../auth'

const { Title, Text } = Typography

function Login() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  // 已登录则直接跳转首页
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

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card style={{ width: 440, borderRadius: 8, boxShadow: '0 4px 24px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <GlobalOutlined style={{ fontSize: 48, color: '#1677ff', marginBottom: 16 }} />
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

        <div style={{ textAlign: 'center', color: '#999', fontSize: 12 }}>
          <Text type="secondary">点击上方预设用户可自动填充账号密码</Text>
        </div>
      </Card>
    </div>
  )
}

export default Login
