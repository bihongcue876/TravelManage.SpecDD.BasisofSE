import { useState, useEffect } from 'react'
import { Table, Button, Space, Modal, Form, Input, InputNumber, DatePicker, message, Upload, Select, Tag } from 'antd'
import { PlusOutlined, EditOutlined, CheckOutlined, UploadOutlined, DownloadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { fetchGroups, createGroup, updateGroup, publishGroup, fetchRoutes, importGroupsExcel, downloadGroupTemplate } from '../api'
import type { Group, Route } from '../types'
import { formatDate } from '../utils'
import './AdminGroups.css'

function AdminGroups() {
  const [groups, setGroups] = useState<Group[]>([])
  const [routes, setRoutes] = useState<Route[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form] = Form.useForm()
  const [dateFormat] = useState('YYYY-MM-DD')

  const loadGroups = async () => {
    setLoading(true)
    try {
      const data = await fetchGroups()
      setGroups(data)
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const loadRoutes = async () => {
    try {
      const data = await fetchRoutes()
      setRoutes(data)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  useEffect(() => {
    loadGroups()
    loadRoutes()
  }, [])

  const handleAdd = () => {
    setEditingId(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: Group) => {
    setEditingId(record.id)
    form.setFieldsValue({
      ...record,
      departure_date: dayjs(record.departure_date, dateFormat),
      deadline: dayjs(record.deadline, dateFormat)
    })
    setModalVisible(true)
  }

  const handlePublish = async (id: number) => {
    try {
      await publishGroup(id)
      message.success('发布成功')
      loadGroups()
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      const data = {
        ...values,
        departure_date: values.departure_date.format(dateFormat),
        deadline: values.deadline.format(dateFormat)
      }
      if (editingId) {
        await updateGroup(editingId, data)
        message.success('更新成功')
      } else {
        await createGroup(data)
        message.success('创建成功')
      }
      setModalVisible(false)
      loadGroups()
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleImport = async (file: File) => {
    try {
      const result = await importGroupsExcel(file)
      if (result.errors && result.errors.length > 0) {
        message.warning(`导入 ${result.imported} 条，错误：${result.errors.join('; ')}`)
      } else {
        message.success(`导入成功，共 ${result.imported} 条旅游团`)
      }
      loadGroups()
    } catch (error) {
      message.error((error as Error).message)
    }
    return false
  }

  const handleDownloadTemplate = async () => {
    try {
      const blob = await downloadGroupTemplate()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'group_template.xlsx'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const columns: ColumnsType<Group> = [
    { title: '团代码', dataIndex: 'code' },
    { title: '路线', dataIndex: 'route_id', render: (id: number) => routes.find((r: Route) => r.id === id)?.name || id },
    { title: '截止日期', dataIndex: 'deadline', render: (v: string) => formatDate(v) },
    { title: '出发日期', dataIndex: 'departure_date', render: (v: string) => formatDate(v) },
    { title: '名额', dataIndex: 'max_pax', render: (_: number, record: Group) => {
      const avail = record.available ?? (record.max_pax - (record.occupied ?? 0))
      return <span><Tag color={avail > 0 ? 'green' : 'red'}>{avail}</Tag> / {record.max_pax}</span>
    }},
    { title: '成人价', dataIndex: 'adult_price', render: (v: number | null) => v !== null ? `¥${v}` : '-' },
    { title: '儿童价', dataIndex: 'child_price', render: (v: number | null) => v !== null ? `¥${v}` : '-' },
    {
      title: '状态',
      dataIndex: 'is_published',
      render: (v: boolean) => v ? '已发布' : '未发布'
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: Group) => (
        <Space>
          {!record.is_published && (
            <>
              <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
              <Button size="small" type="primary" icon={<CheckOutlined />} onClick={() => handlePublish(record.id)} />
            </>
          )}
        </Space>
      )
    }
  ]

  return (
    <div>
      <div className="page-header">
        <h2>旅游团管理</h2>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleDownloadTemplate}>
            下载模板
          </Button>
          <Upload
            beforeUpload={handleImport}
            showUploadList={false}
            accept=".xlsx,.xls"
          >
            <Button icon={<UploadOutlined />}>批量导入</Button>
          </Upload>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增团
          </Button>
        </Space>
      </div>

      <Table
        dataSource={groups}
        columns={columns}
        rowKey="id"
        loading={loading}
      />

      <Modal
        title={editingId ? '编辑旅游团' : '新增旅游团'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="route_id"
            label="路线"
            rules={[{ required: true, message: '请选择路线' }]}
          >
            <Select
              options={routes.map(r => ({ label: r.name, value: r.id }))}
              placeholder="请选择路线"
            />
          </Form.Item>
          <Form.Item
            name="code"
            label="团代码"
            rules={[{ required: true, message: '请输入团代码' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="deadline"
            label="截止日期"
            rules={[{ required: true, message: '请选择截止日期' }]}
          >
            <DatePicker format={dateFormat} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="departure_date"
            label="出发日期"
            rules={[{ required: true, message: '请选择出发日期' }]}
          >
            <DatePicker format={dateFormat} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="max_pax"
            label="名额"
            rules={[{ required: true, message: '请输入名额' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="adult_price" label="成人价">
            <InputNumber min={0} precision={2} prefix="¥" style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="child_price" label="儿童价">
            <InputNumber min={0} precision={2} prefix="¥" style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default AdminGroups
