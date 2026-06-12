import { useState } from 'react'
import { Card, Descriptions, Avatar, Tag, Divider, Typography, Form, Input, Button, message } from 'antd'
import { UserOutlined, TeamOutlined, DollarOutlined, SettingOutlined, LockOutlined } from '@ant-design/icons'
import { useAuth } from '../auth'
import { changePassword } from '../api'

const { Title, Paragraph } = Typography

const roleInfo: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  admin: { label: '系统管理员', icon: <SettingOutlined />, color: 'red' },
  frontdesk: { label: '前台员工', icon: <TeamOutlined />, color: 'blue' },
  finance: { label: '财务人员', icon: <DollarOutlined />, color: 'green' },
}

function UserProfile() {
  const { user } = useAuth()
  const [passwordForm] = Form.useForm()
  const [changingPassword, setChangingPassword] = useState(false)

  if (!user) return null

  const currentRole = roleInfo[user.role]

  const handleChangePassword = async (values: { old_password: string; new_password: string; confirm_password: string }) => {
    setChangingPassword(true)
    try {
      await changePassword({ old_password: values.old_password, new_password: values.new_password })
      message.success('密码修改成功，下次登录时请使用新密码')
      passwordForm.resetFields()
    } catch (err: any) {
      message.error(err.message || '修改失败')
    } finally {
      setChangingPassword(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: 32, marginTop: 24 }}>
        <Avatar size={80} icon={<UserOutlined />} style={{ backgroundColor: '#0958d9', marginBottom: 16 }} />
        <Title level={3}>{user.name}</Title>
        <Paragraph style={{ color: '#666' }}>
          {user.username} · <Tag color={currentRole?.color}>{currentRole?.label || user.role}</Tag>
        </Paragraph>
      </div>

      <Card title="个人信息" style={{ marginBottom: 24 }}>
        <Descriptions column={{ xs: 1, sm: 2 }}>
          <Descriptions.Item label="姓名">{user.name}</Descriptions.Item>
          <Descriptions.Item label="用户名">{user.username}</Descriptions.Item>
          <Descriptions.Item label="角色">
            <Tag color={currentRole?.color}>{currentRole?.label || user.role}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="邮箱">{user.email || '-'}</Descriptions.Item>
          <Descriptions.Item label="电话">{user.phone || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="角色功能说明">
        <Paragraph style={{ color: '#666', marginBottom: 16 }}>
          您的当前角色为 <Tag color={currentRole?.color}>{currentRole?.label}</Tag>，可使用的功能如下：
        </Paragraph>
        <Divider />
        <div>
          {Object.entries(roleInfo).map(([key, r]) => (
            <div key={key} style={{ marginBottom: 8 }}>
              <Tag color={key === user.role ? r.color : 'default'} style={{ marginRight: 8 }}>
                {r.icon} {r.label}
              </Tag>
              <span style={{ color: '#666' }}>
                {key === 'admin' && '所有模块访问：管理路线/旅游团/用户、审批退款、催款报表、财务导出'}
                {key === 'frontdesk' && '查询旅游团、创建申请、录入参加者、管理支付'}
                {key === 'finance' && '查看催款清单、财务流水、导出报表、审批退款'}
              </span>
            </div>
          ))}
        </div>
      </Card>

      <Card title="修改密码" style={{ marginTop: 16 }}>
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={handleChangePassword}
        >
          <Form.Item
            name="old_password"
            label="原密码"
            rules={[{ required: true, message: '请输入原密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="请输入原密码" />
          </Form.Item>
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 4, message: '新密码至少4位' },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="请输入新密码" />
          </Form.Item>
          <Form.Item
            name="confirm_password"
            label="确认新密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'))
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="请再次输入新密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={changingPassword}>
              修改密码
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default UserProfile
