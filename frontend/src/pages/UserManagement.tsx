import { useState, useEffect } from 'react'
import { Table, Button, Space, Modal, Form, Input, Select, Tag, App } from 'antd'
import { PlusOutlined, EditOutlined, StopOutlined, KeyOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { fetchUsers, createUser, updateUser, deactivateUser, resetPassword } from '../api'

const roleOptions = [
  { label: '系统管理员', value: 'admin' },
  { label: '前台员工', value: 'frontdesk' },
  { label: '财务人员', value: 'finance' },
]

const roleColorMap: Record<string, string> = {
  admin: 'red',
  frontdesk: 'blue',
  finance: 'green',
}

const roleNameMap: Record<string, string> = {
  admin: '系统管理员',
  frontdesk: '前台员工',
  finance: '财务人员',
}

function UserManagement() {
  const { message } = App.useApp()
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [resetModalVisible, setResetModalVisible] = useState(false)
  const [resetUserId, setResetUserId] = useState<number | null>(null)
  const [resetUserName, setResetUserName] = useState('')
  const [form] = Form.useForm()
  const [resetForm] = Form.useForm()

  const loadUsers = async () => {
    setLoading(true)
    try {
      const data = await fetchUsers()
      setUsers(data)
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadUsers() }, [])

  const handleAdd = () => {
    setEditingId(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: any) => {
    setEditingId(record.id)
    form.setFieldsValue(record)
    setModalVisible(true)
  }

  const handleDeactivate = async (id: number) => {
    try {
      await deactivateUser(id)
      message.success('用户已停用')
      loadUsers()
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleResetPassword = (record: any) => {
    setResetUserId(record.id)
    setResetUserName(record.name || record.username)
    resetForm.resetFields()
    setResetModalVisible(true)
  }

  const handleResetSubmit = async () => {
    try {
      const values = await resetForm.validateFields()
      if (!resetUserId) return
      await resetPassword(resetUserId, { new_password: values.new_password })
      message.success('密码重置成功')
      setResetModalVisible(false)
    } catch (error) {
      if ((error as any).errorFields) return
      message.error((error as Error).message)
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingId) {
        await updateUser(editingId, values)
        message.success('更新成功')
      } else {
        await createUser(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      loadUsers()
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const columns: ColumnsType<any> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '用户名', dataIndex: 'username' },
    { title: '姓名', dataIndex: 'name' },
    {
      title: '角色',
      dataIndex: 'role',
      render: (role: string) => <Tag color={roleColorMap[role]}>{roleNameMap[role] || role}</Tag>
    },
    { title: '邮箱', dataIndex: 'email', render: (v: string | null) => v || '-' },
    { title: '电话', dataIndex: 'phone', render: (v: string | null) => v || '-' },
    {
      title: '状态',
      dataIndex: 'is_active',
      render: (v: boolean) => v ? <Tag color="success">启用</Tag> : <Tag color="error">停用</Tag>
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: any) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button size="small" icon={<KeyOutlined />} onClick={() => handleResetPassword(record)}>
            重置密码
          </Button>
          {record.is_active && (
            <Button size="small" danger icon={<StopOutlined />} onClick={() => handleDeactivate(record.id)}>
              停用
            </Button>
          )}
        </Space>
      )
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>用户管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>新增用户</Button>
      </div>

      <Table
        dataSource={users}
        columns={columns}
        rowKey="id"
        loading={loading}
      />

      <Modal
        title={editingId ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={500}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="password"
            label="密码"
            rules={editingId ? [] : [{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder={editingId ? '留空则不修改密码' : ''} />
          </Form.Item>
          <Form.Item
            name="name"
            label="姓名"
            rules={[{ required: true, message: '请输入姓名' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select options={roleOptions} placeholder="请选择角色" />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="电话">
            <Input />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`重置密码 - ${resetUserName}`}
        open={resetModalVisible}
        onOk={handleResetSubmit}
        onCancel={() => setResetModalVisible(false)}
        width={420}
        okText="确认重置"
      >
        <Form form={resetForm} layout="vertical">
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 4, message: '密码至少4位' },
            ]}
          >
            <Input.Password placeholder="请输入新密码" />
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
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default UserManagement
