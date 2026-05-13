import { useState, useEffect } from 'react'
import { Table, Button, Space, Modal, Form, Input, message } from 'antd'
import { PlusOutlined, EditOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { fetchRoutes, createRoute, updateRoute } from '../api'
import type { Route } from '../types'
import './AdminRoutes.css'

function AdminRoutes() {
  const [routes, setRoutes] = useState<Route[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form] = Form.useForm()

  const loadRoutes = async () => {
    setLoading(true)
    try {
      const data = await fetchRoutes()
      setRoutes(data)
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRoutes()
  }, [])

  const handleAdd = () => {
    setEditingId(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: Route) => {
    setEditingId(record.id)
    form.setFieldsValue(record)
    setModalVisible(true)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingId) {
        await updateRoute(editingId, values)
        message.success('更新成功')
      } else {
        await createRoute(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      loadRoutes()
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const columns: ColumnsType<Route> = [
    { title: 'ID', dataIndex: 'id' },
    { title: '路线名称', dataIndex: 'name' },
    { title: '描述', dataIndex: 'descr', ellipsis: true },
    {
      title: '状态',
      dataIndex: 'is_active',
      render: (v: boolean) => v ? '启用' : '停用'
    },
    { title: '创建时间', dataIndex: 'created_at' },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: Route) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
        </Space>
      )
    }
  ]

  return (
    <div>
      <div className="page-header">
        <h2>路线管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增路线
        </Button>
      </div>

      <Table
        dataSource={routes}
        columns={columns}
        rowKey="id"
        loading={loading}
      />

      <Modal
        title={editingId ? '编辑路线' : '新增路线'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="路线名称"
            rules={[{ required: true, message: '请输入路线名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="descr" label="描述">
            <Input.TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default AdminRoutes
