import { useState, useEffect } from 'react'
import {
  Card, Table, DatePicker, Button, Space, Tabs, message, Tag, Select,
  Modal, Form, Upload, Checkbox, Row, Col, Statistic, Descriptions, Alert, Empty
} from 'antd'
import {
  DownloadOutlined, FileTextOutlined, DollarOutlined,
  MailOutlined, MessageOutlined, PrinterOutlined,
  UploadOutlined, BankOutlined, FilePdfOutlined, HistoryOutlined,
  CheckCircleOutlined, CloseCircleOutlined, InfoCircleOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import {
  fetchDailyReminders, fetchDailyFinance, exportDailyFinance,
  fetchFinanceReport, sendReminder,
  fetchTaskReminderLogs, importBankReconciliation,
  fetchBankReconciliation, fetchBankReconciliationItems,
  fetchBankReconciliationList, importBankReconciliationExcel,
  batchPrintPdf
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
      const downloadUrl = `/${result.file_path.replace(/\\/g, '/')}`
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = result.file_path.split(/[/\\]/).pop() || `finance_${selectedDate}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      message.success(`导出成功，共 ${result.record_count} 条记录`)
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

  useEffect(() => {
    if (activeTab === 'finance' && selectedDate) {
      loadFinance(selectedDate)
    }
  }, [activeTab, selectedDate])

  const handleBatchDownloadPdf = async (docType: string) => {
    if (selectedAppIds.length === 0) {
      message.warning('请先选择申请单')
      return
    }
    try {
      const blob = await batchPrintPdf({ application_ids: selectedAppIds, doc_type: docType })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const filename = docType === 'confirmation' ? '批量旅行确认书.pdf' : '批量余额缴款单.pdf'
      a.download = filename
      a.click()
      window.URL.revokeObjectURL(url)
      message.success(`已生成 ${selectedAppIds.length} 份文档`)
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
      loadBankReconciliations()
    } catch (error) {
      message.error((error as Error).message)
    }
    return false
  }

  const handleBankImportExcel = async (file: File) => {
    try {
      const result = await importBankReconciliationExcel(file)
      message.success(`导入成功：匹配 ${result.matched_count} 条，未匹配 ${result.unmatched_count} 条`)
      const detail = await fetchBankReconciliationItems(result.id)
      setReconItems(detail)
      setReconDetailVisible(true)
      loadBankReconciliations()
    } catch (error) {
      message.error((error as Error).message)
    }
    return false
  }

  const loadBankReconciliations = async () => {
    try {
      const data = await fetchBankReconciliationList()
      setBankReconciliations(data || [])
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    if (activeTab === 'bank_reconciliation') {
      loadBankReconciliations()
    }
  }, [activeTab])

  const handleViewReconDetail = async (reconId: number) => {
    try {
      const items = await fetchBankReconciliationItems(reconId)
      setReconItems(items)
      setReconDetailVisible(true)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const reminderColumns: ColumnsType<DailyReminderItem> = [
    { title: '申请人', dataIndex: 'name' },
    { title: '电话', dataIndex: 'phone' },
    { title: '团代码', dataIndex: 'tour_code' },
    { title: '出发日期', dataIndex: 'departure', render: (v: string) => formatDate(v) },
    { title: '应付总额', dataIndex: 'total', render: (v: number) => `¥${v}` },
    { title: '已付', dataIndex: 'paid', render: (v: number) => `¥${v}` },
    { title: '余额', dataIndex: 'balance', render: (v: number) => <span style={{ color: '#cf1322', fontWeight: 600 }}>¥{v}</span> },
    { title: '截止日期', dataIndex: 'balance_deadline', render: (v: string) => formatDate(v) },
    {
      title: '催款',
      key: 'action',
      render: (_: unknown, record: DailyReminderItem) => (
        <Space size="small">
          <Button size="small" icon={<MailOutlined />} onClick={() => handleSendReminder(record.app_id, 'email')} title="邮件催款" />
          <Button size="small" icon={<MessageOutlined />} onClick={() => handleSendReminder(record.app_id, 'sms')} title="短信催款" />
          <Button size="small" icon={<PrinterOutlined />} onClick={() => handleSendReminder(record.app_id, 'print')} title="打印催款" />
        </Space>
      )
    },
  ]

  const financeColumns: ColumnsType<Record<string, unknown>> = [
    { title: '支付ID', dataIndex: 'payment_id' },
    { title: '申请ID', dataIndex: 'application_id' },
    { title: '团代码', dataIndex: 'tour_code' },
    { title: '类型', dataIndex: 'type', render: (v: string) => v === 'deposit' ? <Tag color="blue">订金</Tag> : <Tag color="green">尾款</Tag> },
    { title: '金额', dataIndex: 'amount', render: (v: number) => `¥${v}` },
    { title: '时间', dataIndex: 'created_at', render: (v: string) => formatDateTime(v) },
  ]

  const reminderLogColumns: ColumnsType<ReminderLog> = [
    { title: '申请ID', dataIndex: 'application_id' },
    { title: '方式', dataIndex: 'reminder_type', render: (v: string) => {
      const map: Record<string, { icon: React.ReactNode; color: string }> = {
        email: { icon: <MailOutlined />, color: 'blue' },
        sms: { icon: <MessageOutlined />, color: 'green' },
        print: { icon: <PrinterOutlined />, color: 'orange' },
      }
      const item = map[v]
      return item ? <Tag color={item.color}>{item.icon} {v === 'email' ? '邮件' : v === 'sms' ? '短信' : '打印'}</Tag> : v
    }},
    { title: '内容', dataIndex: 'content', ellipsis: true },
    { title: '发送时间', dataIndex: 'sent_at', render: (v: string) => formatDateTime(v) },
  ]

  const reconItemColumns: ColumnsType<BankReconciliationItem> = [
    { title: '银行日期', dataIndex: 'bank_date', render: (v: string) => formatDate(v) },
    { title: '银行金额', dataIndex: 'bank_amount', render: (v: number) => `¥${v}` },
    { title: '银行参考号', dataIndex: 'bank_ref' },
    { title: '匹配支付ID', dataIndex: 'matched_payment_id', render: (v: number | null) => v ? <Tag color="blue">{v}</Tag> : '-' },
    { title: '状态', dataIndex: 'is_matched', render: (v: boolean) => v ? <Tag color="success" icon={<CheckCircleOutlined />}>已匹配</Tag> : <Tag color="error" icon={<CloseCircleOutlined />}>未匹配</Tag> },
  ]

  const reconColumns: ColumnsType<BankReconciliation> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '导入日期', dataIndex: 'import_date', render: (v: string) => formatDate(v) },
    { title: '文件名', dataIndex: 'file_name', ellipsis: true },
    { title: '总记录', dataIndex: 'total_records', width: 80 },
    { title: '已匹配', dataIndex: 'matched_count', width: 80, render: (v: number) => <Tag color="success">{v}</Tag> },
    { title: '未匹配', dataIndex: 'unmatched_count', width: 80, render: (v: number) => <Tag color={v > 0 ? 'error' : 'success'}>{v}</Tag> },
    { title: '导入时间', dataIndex: 'created_at', render: (v: string) => formatDateTime(v), width: 180 },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: unknown, record: BankReconciliation) => (
        <Button size="small" type="link" onClick={() => handleViewReconDetail(record.id)}>
          查看明细
        </Button>
      )
    },
  ]

  const selectedCount = selectedAppIds.length

  const tabItems = [
    {
      key: 'reminders',
      label: <span><FileTextOutlined /> 催款单</span>,
      children: (
        <div>
          <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
            <Col>
              <Space>
                <DatePicker
                  value={selectedDate ? dayjs(selectedDate) : null}
                  onChange={(date) => setSelectedDate(date?.format('YYYY-MM-DD'))}
                  format="YYYY-MM-DD"
                />
                <Button type="primary" onClick={() => selectedDate && loadReminders(selectedDate)}>
                  查询
                </Button>
              </Space>
            </Col>
            <Col>
              <Space>
                <Button
                  icon={<FilePdfOutlined />}
                  onClick={() => handleBatchDownloadPdf('payment_order')}
                  disabled={selectedCount === 0}
                >
                  批量下载缴款单
                </Button>
                <Button
                  icon={<FilePdfOutlined />}
                  onClick={() => handleBatchDownloadPdf('confirmation')}
                  disabled={selectedCount === 0}
                >
                  批量下载确认书
                </Button>
              </Space>
            </Col>
          </Row>
          {selectedCount > 0 && (
            <Alert
              message={`已选择 ${selectedCount} 条记录，可批量下载PDF文档`}
              type="info"
              showIcon
              style={{ marginBottom: 16, borderRadius: 8 }}
              closable
              onClose={() => setSelectedAppIds([])}
            />
          )}
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
          <Card
            title="导入对账单"
            style={{ marginBottom: 24, borderRadius: 8 }}
            styles={{ body: { padding: '16px 24px' } }}
          >
            <Row gutter={16}>
              <Col span={12}>
                <Upload
                  beforeUpload={(file) => { handleBankImportExcel(file); return false }}
                  showUploadList={false}
                  accept=".xlsx,.xls"
                >
                  <Button icon={<UploadOutlined />} block>导入 Excel 对账单</Button>
                </Upload>
                <div style={{ color: '#999', fontSize: 12, marginTop: 8 }}>
                  支持 .xlsx/.xls 格式，列顺序：日期、金额、参考号
                </div>
              </Col>
              <Col span={12}>
                <Upload
                  beforeUpload={(file) => { handleBankImport(file); return false }}
                  showUploadList={false}
                  accept=".json"
                >
                  <Button icon={<UploadOutlined />} block>导入 JSON 对账单</Button>
                </Upload>
                <div style={{ color: '#999', fontSize: 12, marginTop: 8 }}>
                  JSON 数组格式：[&#123;"date":"2026-06-01","amount":500,"reference":"REF001"&#125;]
                </div>
              </Col>
            </Row>
          </Card>

          <Card
            title={<span><HistoryOutlined /> 对账历史</span>}
            style={{ borderRadius: 8 }}
          >
            {bankReconciliations.length === 0 ? (
              <Empty description="暂无对账记录" />
            ) : (
              <Table
                dataSource={bankReconciliations}
                columns={reconColumns}
                rowKey="id"
                pagination={false}
                size="small"
              />
            )}
          </Card>
        </div>
      )
    },
  ]

  return (
    <div>
      <h2>催款与报表</h2>
      <Card style={{ borderRadius: 8 }}>
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
        {reconItems.length > 0 && (
          <Alert
            message={
              <span>
                <InfoCircleOutlined style={{ marginRight: 8 }} />
                共 {reconItems.length} 条记录，
                已匹配 <Tag color="success">{reconItems.filter(i => i.is_matched).length}</Tag> 条，
                未匹配 <Tag color="error">{reconItems.filter(i => !i.is_matched).length}</Tag> 条
              </span>
            }
            type="info"
            style={{ marginBottom: 16, borderRadius: 8 }}
          />
        )}
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
