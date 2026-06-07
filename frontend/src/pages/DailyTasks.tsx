import { useState, useEffect } from 'react'
import {
  Card, Table, DatePicker, Button, Space, Tabs, message, Tag, Select,
  Modal, Form, Upload, Checkbox, Row, Col, Statistic
} from 'antd'
import {
  DownloadOutlined, FileTextOutlined, DollarOutlined,
  MailOutlined, MessageOutlined, PrinterOutlined,
  UploadOutlined, BankOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import {
  fetchDailyReminders, fetchDailyFinance, exportDailyFinance,
  fetchFinanceReport, batchPrintDocuments, sendReminder,
  fetchTaskReminderLogs, importBankReconciliation,
  fetchBankReconciliation, fetchBankReconciliationItems
} from '../api'
import type {
  DailyReminderItem, FinanceReport, ReminderLog,
  BankReconciliation, BankReconciliationItem
} from '../types'
import { formatDate, formatDateTime } from '../utils'
import './DailyTasks.css'

function DailyTasks() {
  const [loading, setLoading] = useState(false)
  const [selectedDate, setSelectedDate] = useState<string | undefined>(dayjs().format('YYYY-MM-DD'))
  const [reminders, setReminders] = useState<DailyReminderItem[]>([])
  const [financeData, setFinanceData] = useState<Record<string, unknown>[]>([])
  const [selectedAppIds, setSelectedAppIds] = useState<number[]>([])
  const [financeReport, setFinanceReport] = useState<FinanceReport | null>(null)
  const [reminderLogs, setReminderLogs] = useState<ReminderLog[]>([])
  const [bankReconciliations, setBankReconciliations] = useState<BankReconciliation[]>([])
  const [reconItems, setReconItems] = useState<BankReconciliationItem[]>([])
  const [reconDetailVisible, setReconDetailVisible] = useState(false)
  const [exportModalVisible, setExportModalVisible] = useState(false)
  const [reportModalVisible, setReportModalVisible] = useState(false)
  const [activeTab, setActiveTab] = useState('reminders')
  const [form] = Form.useForm()

  const loadReminders = async (date: string) => {
    setLoading(true)
    try {
      const data = await fetchDailyReminders({ date })
      setReminders(data.items || [])
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const loadFinance = async (date: string) => {
    setLoading(true)
    try {
      const data = await fetchDailyFinance({ date })
      setFinanceData(data || [])
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    if (!selectedDate) return
    try {
      const values = form.getFieldsValue()
      const result = await exportDailyFinance({
        target_date: selectedDate,
        format: values.format || 'csv',
        fields: values.fields,
      })
      // 自动下载导出的文件
      const downloadUrl = `/${result.file_path.replace(/\\/g, '/')}`
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = result.file_path.split(/[/\\]/).pop() || `finance_${selectedDate}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      message.success(`导出成功，共 ${result.record_count} 条记录，已开始下载`)
      setExportModalVisible(false)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleFinanceReport = async () => {
    const values = form.getFieldsValue()
    try {
      const report = await fetchFinanceReport({
        period: values.period || 'daily',
        start_date: values.start_date?.format('YYYY-MM-DD') || dayjs().format('YYYY-MM-DD'),
        end_date: values.end_date?.format('YYYY-MM-DD') || dayjs().format('YYYY-MM-DD'),
      })
      setFinanceReport(report)
      setReportModalVisible(true)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  // 切到财务流水 tab 或切换日期时自动加载
  useEffect(() => {
    if (activeTab === 'finance' && selectedDate) {
      loadFinance(selectedDate)
    }
  }, [activeTab, selectedDate])

  const handleBatchPrint = async (docType: string) => {
    if (selectedAppIds.length === 0) {
      message.warning('请先选择申请单')
      return
    }
    try {
      const result = await batchPrintDocuments({ application_ids: selectedAppIds, doc_type: docType })
      message.success(`已生成 ${result.total_count} 份文档`)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleSendReminder = async (appId: number, type: string) => {
    try {
      await sendReminder({ application_id: appId, reminder_type: type })
      message.success('催款通知已发送')
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const loadReminderLogs = async () => {
    try {
      const logs = await fetchTaskReminderLogs()
      setReminderLogs(logs || [])
    } catch {
      // ignore
    }
  }

  const handleBankImport = async (file: File) => {
    try {
      const result = await importBankReconciliation(file)
      message.success(`导入成功：匹配 ${result.matched_count} 条，未匹配 ${result.unmatched_count} 条`)
      const detail = await fetchBankReconciliationItems(result.id)
      setReconItems(detail)
      setReconDetailVisible(true)
    } catch (error) {
      message.error((error as Error).message)
    }
    return false
  }

  const reminderColumns: ColumnsType<DailyReminderItem> = [
    { title: '申请人', dataIndex: 'name' },
    { title: '电话', dataIndex: 'phone' },
    { title: '团代码', dataIndex: 'tour_code' },
    { title: '出发日期', dataIndex: 'departure' },
    {
      title: '应付总额',
      dataIndex: 'total',
      render: (v: number) => `¥${v}`
    },
    {
      title: '已付',
      dataIndex: 'paid',
      render: (v: number) => `¥${v}`
    },
    {
      title: '余额',
      dataIndex: 'balance',
      render: (v: number) => `¥${v}`
    },
    { title: '截止日期', dataIndex: 'balance_deadline' },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: DailyReminderItem) => (
        <Space size="small">
          <Button size="small" icon={<MailOutlined />} onClick={() => handleSendReminder(record.app_id, 'email')} />
          <Button size="small" icon={<MessageOutlined />} onClick={() => handleSendReminder(record.app_id, 'sms')} />
          <Button size="small" icon={<PrinterOutlined />} onClick={() => handleSendReminder(record.app_id, 'print')} />
        </Space>
      )
    },
  ]

  const financeColumns: ColumnsType<Record<string, unknown>> = [
    { title: '支付ID', dataIndex: 'payment_id' },
    { title: '申请ID', dataIndex: 'application_id' },
    { title: '团代码', dataIndex: 'tour_code' },
    {
      title: '类型',
      dataIndex: 'type',
      render: (v: string) => v === 'deposit' ? <Tag color="blue">订金</Tag> : <Tag color="green">尾款</Tag>
    },
    {
      title: '金额',
      dataIndex: 'amount',
      render: (v: number) => `¥${v}`
    },
    { title: '时间', dataIndex: 'created_at', render: (v: string) => formatDateTime(v) },
  ]

  const reminderLogColumns: ColumnsType<ReminderLog> = [
    { title: '申请ID', dataIndex: 'application_id' },
    {
      title: '方式',
      dataIndex: 'reminder_type',
      render: (v: string) => {
        const map: Record<string, { icon: React.ReactNode; color: string }> = {
          email: { icon: <MailOutlined />, color: 'blue' },
          sms: { icon: <MessageOutlined />, color: 'green' },
          print: { icon: <PrinterOutlined />, color: 'orange' },
        }
        const item = map[v]
        return item ? <Tag color={item.color}>{item.icon} {v === 'email' ? '邮件' : v === 'sms' ? '短信' : '打印'}</Tag> : v
      }
    },
    { title: '内容', dataIndex: 'content', ellipsis: true },
    { title: '发送时间', dataIndex: 'sent_at', render: (v: string) => formatDateTime(v) },
  ]

  const reconItemColumns: ColumnsType<BankReconciliationItem> = [
    { title: '银行日期', dataIndex: 'bank_date', render: (v: string) => formatDate(v) },
    { title: '银行金额', dataIndex: 'bank_amount', render: (v: number) => `¥${v}` },
    { title: '银行参考号', dataIndex: 'bank_ref' },
    { title: '匹配支付ID', dataIndex: 'matched_payment_id', render: (v: number | null) => v || '-' },
    {
      title: '状态',
      dataIndex: 'is_matched',
      render: (v: boolean) => v ? <Tag color="success">已匹配</Tag> : <Tag color="error">未匹配</Tag>
    },
  ]

  const tabItems = [
    {
      key: 'reminders',
      label: <span><FileTextOutlined /> 催款单</span>,
      children: (
        <div>
          <Space style={{ marginBottom: 16 }}>
            <DatePicker
              value={selectedDate ? dayjs(selectedDate) : null}
              onChange={(date) => setSelectedDate(date?.format('YYYY-MM-DD'))}
              format="YYYY-MM-DD"
            />
            <Button type="primary" onClick={() => selectedDate && loadReminders(selectedDate)}>
              查询
            </Button>
            <Button onClick={() => handleBatchPrint('payment_order')} disabled={selectedAppIds.length === 0}>
              批量打印交款单
            </Button>
            <Button onClick={() => handleBatchPrint('confirmation')} disabled={selectedAppIds.length === 0}>
              批量打印确认书
            </Button>
          </Space>
          <Table
            dataSource={reminders}
            columns={reminderColumns}
            rowKey="app_id"
            loading={loading}
            pagination={false}
            rowSelection={{
              selectedRowKeys: selectedAppIds,
              onChange: (keys) => setSelectedAppIds(keys as number[]),
            }}
          />
        </div>
      )
    },
    {
      key: 'finance',
      label: <span><DollarOutlined /> 财务流水</span>,
      children: (
        <div>
          <Space style={{ marginBottom: 16 }}>
            <DatePicker
              value={selectedDate ? dayjs(selectedDate) : null}
              onChange={(date) => setSelectedDate(date?.format('YYYY-MM-DD'))}
              format="YYYY-MM-DD"
            />
            <Button type="primary" onClick={() => selectedDate && loadFinance(selectedDate)}>
              查询
            </Button>
            <Button icon={<DownloadOutlined />} onClick={() => setExportModalVisible(true)}>
              导出
            </Button>
            <Button onClick={handleFinanceReport}>
              财务报表
            </Button>
          </Space>
          <Table
            dataSource={financeData}
            columns={financeColumns}
            rowKey="payment_id"
            loading={loading}
            pagination={false}
          />
        </div>
      )
    },
    {
      key: 'reminder_logs',
      label: <span><MessageOutlined /> 催款记录</span>,
      children: (
        <div>
          <Button onClick={loadReminderLogs} style={{ marginBottom: 16 }}>刷新催款记录</Button>
          <Table
            dataSource={reminderLogs}
            columns={reminderLogColumns}
            rowKey="id"
            pagination={false}
            size="small"
          />
        </div>
      )
    },
    {
      key: 'bank_reconciliation',
      label: <span><BankOutlined /> 银行对账</span>,
      children: (
        <div>
          <Space style={{ marginBottom: 16 }}>
            <Upload
              beforeUpload={(file) => { handleBankImport(file); return false }}
              showUploadList={false}
              accept=".json"
            >
              <Button icon={<UploadOutlined />}>导入银行对账单</Button>
            </Upload>
          </Space>
          <p style={{ color: '#999' }}>请上传JSON格式的银行对账单文件</p>
        </div>
      )
    },
  ]

  return (
    <div>
      <h2>催款与报表</h2>
      <Card>
        <Tabs items={tabItems} onChange={(key) => setActiveTab(key)} />
      </Card>

      <Modal
        title="导出财务数据"
        open={exportModalVisible}
        onOk={handleExport}
        onCancel={() => setExportModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="导出格式" name="format" initialValue="csv">
            <Select options={[
              { label: 'CSV', value: 'csv' },
              { label: 'Excel (UTF-8 CSV)', value: 'excel' },
              { label: 'JSON', value: 'json' },
            ]} />
          </Form.Item>
          <Form.Item label="自定义导出字段">
            <Checkbox.Group
              options={[
                { label: '支付ID', value: 'payment_id' },
                { label: '申请ID', value: 'application_id' },
                { label: '团代码', value: 'tour_code' },
                { label: '类型', value: 'type' },
                { label: '金额', value: 'amount' },
                { label: '支付方式', value: 'payment_method' },
                { label: '时间', value: 'created_at' },
              ]}
              onChange={(values) => form.setFieldValue('fields', values)}
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="财务对账报表"
        open={reportModalVisible}
        onCancel={() => setReportModalVisible(false)}
        footer={null}
        width={600}
      >
        {financeReport && (
          <Row gutter={16}>
            <Col span={12}>
              <Statistic title="订金总额" value={financeReport.total_deposits} prefix="¥" />
            </Col>
            <Col span={12}>
              <Statistic title="尾款总额" value={financeReport.total_balances} prefix="¥" />
            </Col>
            <Col span={12}>
              <Statistic title="退款总额" value={financeReport.total_refunds} prefix="¥" />
            </Col>
            <Col span={12}>
              <Statistic title="净收入" value={financeReport.net_income} prefix="¥" />
            </Col>
          </Row>
        )}
      </Modal>

      <Modal
        title="银行对账明细"
        open={reconDetailVisible}
        onCancel={() => setReconDetailVisible(false)}
        width={800}
        footer={null}
      >
        <Table
          dataSource={reconItems}
          columns={reconItemColumns}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Modal>
    </div>
  )
}

export default DailyTasks
