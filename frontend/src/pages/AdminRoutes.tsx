import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Space, Modal, Form, Input, message, Upload, Switch, Popconfirm, Alert } from 'antd'
import { PlusOutlined, EditOutlined, UploadOutlined, DownloadOutlined, StopOutlined, CheckCircleOutlined, CheckOutlined, CloseOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { fetchRoutes, searchRoutes, createRoute, updateRoute, deactivateRoute, deleteRouteForce, batchUpdateRoutes, importRoutesExcel, downloadRouteTemplate } from '../api'
import type { Route } from '../types'
import { formatDateTime } from '../utils'
import './AdminRoutes.css'

function AdminRoutes() {
  const [routes, setRoutes] = useState<Route[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [searchText, setSearchText] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [batchLoading, setBatchLoading] = useState(false)
  const [form] = Form.useForm()

  const loadRoutes = useCallback(async (q = '') => {
    setLoading(true)
    try {
      const data = q ? await searchRoutes(q) : await fetchRoutes()
      setRoutes(data)
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadRoutes()
  }, [loadRoutes])

  const handleSearch = (value: string) => {
    setSearchText(value)
    setSelectedRowKeys([])
    loadRoutes(value)
  }

  const handleAdd = () => {
    setEditingId(null)
    form.resetFields()
    form.setFieldsValue({ is_active: true })
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
      loadRoutes(searchText)
    } catch (error) {
      if ((error as Error).name !== 'ValidateFieldsError') {
        message.error((error as Error).message)
      }
    }
  }

  const handleToggleActive = async (record: Route) => {
    try {
      if (record.is_active) {
        await deactivateRoute(record.id)
        message.success('路线已停用')
      } else {
        await updateRoute(record.id, { is_active: true })
        message.success('路线已启用')
      }
      loadRoutes(searchText)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleDelete = async (record: Route) => {
    try {
      await deleteRouteForce(record.id)
      message.success('路线已删除')
      loadRoutes(searchText)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleBatchUpdate = async (is_active: boolean) => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要操作的路线')
      return
    }
    setBatchLoading(true)
    try {
      const ids = selectedRowKeys.map(Number)
      const result = await batchUpdateRoutes(ids, is_active)
      message.success(`已${is_active ? '启用' : '停用'} ${result.updated} 条路线`)
      setSelectedRowKeys([])
      loadRoutes(searchText)
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setBatchLoading(false)
    }
  }

  const handleImport = async (file: File) => {
    try {
      const result = await importRoutesExcel(file)
      message.success(`导入成功，共 ${result.imported} 条路线`)
      loadRoutes(searchText)
    } catch (error) {
      message.error((error as Error).message)
    }
    return false
  }

  const handleDownloadTemplate = async () => {
    try {
      const blob = await downloadRouteTemplate()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'route_template.xlsx'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const columns: ColumnsType<Route> = [
    { title: '编号', dataIndex: 'code', width: 150 },
    { title: '路线名称', dataIndex: 'name', width: 200 },
    { title: '描述', dataIndex: 'descr', ellipsis: true },
    {
      title: '状态',
      dataIndex: 'is_active',
      width: 80,
      align: 'center',
      render: (v: boolean) => v
        ? <span style={{ color: '#52c41a' }}><CheckCircleOutlined /> 启用</span>
        : <span style={{ color: '#ff4d4f' }}><StopOutlined /> 停用</span>
    },
    { title: '创建时间', dataIndex: 'created_at', width: 180, render: (v: string) => formatDateTime(v) },
    {
      title: '操作',
      key: 'action',
      width: 220,
      render: (_: unknown, record: Route) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title={`确认${record.is_active ? '停用' : '启用'}此路线？`}
            onConfirm={() => handleToggleActive(record)}
          >
            <Button size="small" danger={record.is_active}>
              {record.is_active ? '停用' : '启用'}
            </Button>
          </Popconfirm>
          <Popconfirm
            title="确认永久删除此路线？"
            description="仅当路线无关联旅游团时可删除"
            onConfirm={() => handleDelete(record)}
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: (newKeys: React.Key[]) => setSelectedRowKeys(newKeys),
  }

  const selectedCount = selectedRowKeys.length

  return (
    <div>
      <div className="page-header">
        <h2>路线管理</h2>
        <Space>
          <Input.Search
            placeholder="搜索路线名称/编号/描述"
            allowClear
            onSearch={handleSearch}
            onChange={e => !e.target.value && handleSearch('')}
            style={{ width: 280 }}
          />
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
            新增路线
          </Button>
        </Space>
      </div>

      {selectedCount > 0 && (
        <Alert
          type="info"
          showIcon={false}
          message={
            <Space>
              <span>已选择 <strong>{selectedCount}</strong> 条路线</span>
              <Button
                size="small"
                type="primary"
                ghost
                icon={<CheckOutlined />}
                loading={batchLoading}
                onClick={() => handleBatchUpdate(true)}
              >
                批量启用
              </Button>
              <Button
                size="small"
                danger
                ghost
                icon={<CloseOutlined />}
                loading={batchLoading}
                onClick={() => handleBatchUpdate(false)}
              >
                批量停用
              </Button>
              <Button
                size="small"
                onClick={() => setSelectedRowKeys([])}
              >
                取消选择
              </Button>
            </Space>
          }
          style={{ marginBottom: 16, padding: '8px 12px' }}
        />
      )}

      <Table
        dataSource={routes}
        columns={columns}
        rowKey="id"
        loading={loading}
        rowSelection={rowSelection}
        pagination={{ pageSize: 20 }}
      />

      <Modal
        title={editingId ? '编辑路线' : '新增路线'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={520}
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
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="is_active" label="状态" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default AdminRoutes
