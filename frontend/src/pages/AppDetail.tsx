import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card, Steps, Button, Table, Modal, Form, InputNumber, Input, Select,
  message, Alert, Space, Popconfirm, Upload, Descriptions, Tag, Tabs,
  Timeline, Statistic, Row, Col
} from 'antd'
import {
  UploadOutlined, DollarOutlined, FileTextOutlined,
  WarningOutlined, ClockCircleOutlined
} from '@ant-design/icons'
import type { UploadFile } from 'antd'
import { Checkbox } from 'antd'
import {
  fetchApplication, payDeposit, payBalance, addParticipants,
  cancelApplication, getCancelPreview, fetchRemainingBalance,
  fetchPaymentLogs, fetchRefunds, approveRefund, fetchReminderLogs,
  generateOrderNo, partialCancelApplication, checkDuplicateParticipants
} from '../api'
import type {
  ApplicationDetail, CancelPreview, ParticipantCreate,
  RemainingBalance, PaymentLogDetail, RefundDetail, ReminderLog,
  DuplicateParticipantWarning
} from '../types'
import { formatDateTime } from '../utils'
import './AppDetail.css'

const stateMap: Record<string, { text: string; color: string }> = {
  draft: { text: '草稿', color: 'default' },
  deposit_paid: { text: '订金已付', color: 'processing' },
  confirmed: { text: '已确认', color: 'success' },
  cancelled: { text: '已取消', color: 'error' }
}

const paymentMethodOptions = [
  { label: '现金', value: 'cash' },
  { label: '银行转账', value: 'bank_transfer' },
  { label: '微信', value: 'wechat' },
  { label: '支付宝', value: 'alipay' },
]

const refundChannelOptions = [
  { label: '原路返回', value: 'original' },
  { label: '现金', value: 'cash' },
  { label: '银行转账', value: 'bank_transfer' },
]

function AppDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [application, setApplication] = useState<ApplicationDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [payModalVisible, setPayModalVisible] = useState(false)
  const [payType, setPayType] = useState<'deposit' | 'balance'>('deposit')
  const [participantModalVisible, setParticipantModalVisible] = useState(false)
  const [cancelModalVisible, setCancelModalVisible] = useState(false)
  const [cancelPreview, setCancelPreview] = useState<CancelPreview | null>(null)
  const [remainingBalance, setRemainingBalance] = useState<RemainingBalance | null>(null)
  const [paymentLogs, setPaymentLogs] = useState<PaymentLogDetail[]>([])
  const [refunds, setRefunds] = useState<RefundDetail[]>([])
  const [reminderLogs, setReminderLogs] = useState<ReminderLog[]>([])
  const [duplicateWarnings, setDuplicateWarnings] = useState<DuplicateParticipantWarning[]>([])
  const [partialCancelVisible, setPartialCancelVisible] = useState(false)
  const [selectedParticipantIds, setSelectedParticipantIds] = useState<number[]>([])
  const [voucherFiles, setVoucherFiles] = useState<UploadFile[]>([])
  const [form] = Form.useForm()

  const loadApplication = async () => {
    if (!id) return
    try {
      const data = await fetchApplication(parseInt(id))
      setApplication(data)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const loadEnhancedData = async () => {
    if (!id) return
    const appId = parseInt(id)
    try {
      const [rb, logs, refundList, reminders] = await Promise.all([
        fetchRemainingBalance(appId).catch(() => null),
        fetchPaymentLogs(appId).catch(() => []),
        fetchRefunds(appId).catch(() => []),
        fetchReminderLogs(appId).catch(() => []),
      ])
      setRemainingBalance(rb)
      setPaymentLogs(logs)
      setRefunds(refundList)
      setReminderLogs(reminders)
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    loadApplication()
    loadEnhancedData()
  }, [id])

  const handlePayDeposit = () => {
    setPayType('deposit')
    setPayModalVisible(true)
    form.resetFields()
  }

  const handlePayBalance = () => {
    setPayType('balance')
    setPayModalVisible(true)
    form.resetFields()
  }

  const handlePaySubmit = async () => {
    if (!id) return
    setLoading(true)
    try {
      const values = await form.validateFields()
      const amount = parseFloat(values.amount)
      const paymentMethod = values.payment_method
      const data: { amount: number; payment_method?: string } = { amount }
      if (paymentMethod) data.payment_method = paymentMethod

      if (payType === 'deposit') {
        await payDeposit(parseInt(id), data)
        message.success('订金支付成功')
      } else {
        await payBalance(parseInt(id), data)
        message.success('尾款支付成功')
      }
      setPayModalVisible(false)
      form.resetFields()
      setVoucherFiles([])
      loadApplication()
      loadEnhancedData()
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddParticipants = () => {
    if (!application) return
    const participants: ParticipantCreate[] = []
    for (let i = 0; i < application.adults; i++) {
      participants.push({ name: '', is_leader: i === 0 })
    }
    for (let i = 0; i < application.children; i++) {
      participants.push({ name: '', is_leader: false })
    }
    form.setFieldsValue({ participants })
    setParticipantModalVisible(true)
  }

  const handleParticipantsSubmit = async () => {
    if (!id) return
    setLoading(true)
    try {
      const values = form.getFieldsValue()
      await addParticipants(parseInt(id), { participants: values.participants })
      message.success('参加者信息录入成功')
      setParticipantModalVisible(false)
      form.resetFields()
      loadApplication()
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleCancelPreview = async () => {
    if (!id) return
    try {
      const preview = await getCancelPreview(parseInt(id))
      setCancelPreview(preview)
      setCancelModalVisible(true)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleCancelConfirm = async () => {
    if (!id) return
    setLoading(true)
    try {
      const channel = form.getFieldValue('cancel_channel')
      await cancelApplication(parseInt(id), undefined, channel)
      message.success('申请已取消')
      setCancelModalVisible(false)
      loadApplication()
      loadEnhancedData()
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handlePartialCancel = async () => {
    if (!id || selectedParticipantIds.length === 0) return
    setLoading(true)
    try {
      await partialCancelApplication(parseInt(id), {
        participant_ids: selectedParticipantIds,
        channel: form.getFieldValue('partial_cancel_channel'),
      })
      message.success('部分取消成功')
      setPartialCancelVisible(false)
      setSelectedParticipantIds([])
      loadApplication()
      loadEnhancedData()
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleApproveRefund = async (refundId: number, approved: boolean) => {
    setLoading(true)
    try {
      await approveRefund(refundId, { approved, approved_by: 'admin' })
      message.success(approved ? '退款已批准' : '退款已拒绝')
      loadEnhancedData()
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateOrderNo = async () => {
    if (!id) return
    try {
      const order = await generateOrderNo(parseInt(id))
      message.success(`交款单编号已生成：${order.order_no}`)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleDuplicateCheck = async (phone?: string) => {
    if (!id || !phone) return
    try {
      const warnings = await checkDuplicateParticipants(parseInt(id), { phone })
      setDuplicateWarnings(warnings)
    } catch {
      // ignore
    }
  }

  if (!application) return null

  const currentStep = application.state === 'draft' ? 1 :
    application.state === 'deposit_paid' && !application.info_completed ? 2 :
    application.state === 'deposit_paid' && application.info_completed &&
    application.paid_balance < application.total_price - application.paid_deposit ? 3 :
    application.state === 'deposit_paid' && application.info_completed &&
    application.paid_balance >= application.total_price - application.paid_deposit ? 4 :
    application.state === 'confirmed' ? 4 : 1

  const balance = application.total_price - application.paid_deposit - application.paid_balance

  const participantColumns = [
    { title: '姓名', dataIndex: 'name', key: 'name' },
    { title: '性别', dataIndex: 'gender', key: 'gender', render: (v: string) => ({ M: '男', F: '女' })[v] || '-' },
    { title: '电话', dataIndex: 'phone', key: 'phone' },
    { title: '责任人', dataIndex: 'is_leader', key: 'is_leader', render: (v: boolean) => v ? '是' : '否' },
  ]

  const paymentLogColumns = [
    { title: '类型', dataIndex: 'type', key: 'type', render: (v: string) => v === 'deposit' ? '订金' : '尾款' },
    { title: '金额', dataIndex: 'amount', key: 'amount', render: (v: number) => `¥${v}` },
    { title: '支付方式', dataIndex: 'payment_method', key: 'payment_method', render: (v: string | null) => {
      const map: Record<string, string> = { cash: '现金', bank_transfer: '银行转账', wechat: '微信', alipay: '支付宝' }
      return v ? map[v] || v : '-'
    }},
    { title: '时间', dataIndex: 'created_at', key: 'created_at', render: (v: string) => formatDateTime(v) },
  ]

  const refundColumns = [
    { title: '手续费', dataIndex: 'cancel_fee', key: 'cancel_fee', render: (v: number) => `¥${v}` },
    { title: '退款金额', dataIndex: 'refund_amount', key: 'refund_amount', render: (v: number) => `¥${v}` },
    { title: '退款渠道', dataIndex: 'channel', key: 'channel', render: (v: string | null) => {
      const map: Record<string, string> = { original: '原路返回', cash: '现金', bank_transfer: '银行转账' }
      return v ? map[v] || v : '-'
    }},
    { title: '状态', dataIndex: 'status', key: 'status', render: (v: string) => {
      const colorMap: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'error', completed: 'default' }
      const textMap: Record<string, string> = { pending: '待审批', approved: '已批准', rejected: '已拒绝', completed: '已完成' }
      return <Tag color={colorMap[v]}>{textMap[v] || v}</Tag>
    }},
    { title: '操作', key: 'action', render: (_: unknown, record: RefundDetail) => (
      record.status === 'pending' ? (
        <Space>
          <Button size="small" type="primary" onClick={() => handleApproveRefund(record.id, true)}>批准</Button>
          <Button size="small" danger onClick={() => handleApproveRefund(record.id, false)}>拒绝</Button>
        </Space>
      ) : null
    )},
  ]

  const tabItems = [
    {
      key: 'info',
      label: '申请信息',
      children: (
        <div>
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="团代码">{application.group?.code}</Descriptions.Item>
            <Descriptions.Item label="出发日期">{application.group?.departure_date}</Descriptions.Item>
            <Descriptions.Item label="申请人">{application.name}</Descriptions.Item>
            <Descriptions.Item label="电话">{application.phone}</Descriptions.Item>
            <Descriptions.Item label="人数">成人 {application.adults} / 儿童 {application.children}</Descriptions.Item>
            <Descriptions.Item label="总费用">¥{application.total_price}</Descriptions.Item>
            <Descriptions.Item label="应付订金">¥{application.deposit}</Descriptions.Item>
            <Descriptions.Item label="已付订金">¥{application.paid_deposit}</Descriptions.Item>
            <Descriptions.Item label="已付尾款">¥{application.paid_balance}</Descriptions.Item>
            <Descriptions.Item label="余额">¥{balance}</Descriptions.Item>
          </Descriptions>
          {remainingBalance && (
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={8}>
                <Statistic title="剩余应付" value={remainingBalance.remaining} prefix="¥" />
              </Col>
              <Col span={8}>
                <Statistic title="支付截止日" value={remainingBalance.balance_deadline} />
              </Col>
              <Col span={8}>
                <Statistic
                  title="距截止日"
                  value={remainingBalance.days_until_deadline}
                  suffix="天"
                  valueStyle={{ color: remainingBalance.days_until_deadline <= 3 ? '#cf1322' : '#3f8600' }}
                />
              </Col>
            </Row>
          )}
        </div>
      )
    },
    {
      key: 'payments',
      label: '支付记录',
      children: (
        <Table
          dataSource={paymentLogs}
          columns={paymentLogColumns}
          rowKey="id"
          pagination={false}
          size="small"
        />
      )
    },
    {
      key: 'refunds',
      label: '退款记录',
      children: (
        <Table
          dataSource={refunds}
          columns={refundColumns}
          rowKey="id"
          pagination={false}
          size="small"
        />
      )
    },
    {
      key: 'reminders',
      label: '催款记录',
      children: (
        <Timeline
          items={reminderLogs.map(log => ({
            color: log.success ? 'green' : 'red',
            children: (
              <div>
                <Tag>{log.reminder_type === 'email' ? '邮件' : log.reminder_type === 'sms' ? '短信' : '打印'}</Tag>
                <span>{log.content}</span>
                <div style={{ fontSize: 12, color: '#999' }}>{log.sent_at}</div>
              </div>
            )
          }))}
        />
      )
    },
  ]

  return (
    <div className="detail-container">
      <Card title="申请详情" style={{ marginBottom: 16 }}>
        <Steps
          current={currentStep}
          items={[
            { title: '创建申请' },
            { title: '支付订金' },
            { title: '录入参加者' },
            { title: '支付尾款' },
            { title: '完成' }
          ]}
        />
        <Alert
          message={`状态：${stateMap[application.state]?.text || application.state}`}
          type={stateMap[application.state]?.color === 'success' ? 'success' : 'info'}
          style={{ marginTop: 16 }}
        />
      </Card>

      {duplicateWarnings.length > 0 && (
        <Alert
          message="重复报名提醒"
          description={
            <ul>
              {duplicateWarnings.map((w, i) => (
                <li key={i}><WarningOutlined /> {w.message}</li>
              ))}
            </ul>
          }
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Card style={{ marginBottom: 16 }}>
        <Tabs items={tabItems} />
      </Card>

      {application.state === 'draft' && (
        <Card title="操作">
          <Button type="primary" onClick={handlePayDeposit}>
            支付订金
          </Button>
        </Card>
      )}

      {application.state === 'deposit_paid' && !application.info_completed && (
        <Card title="操作">
          <Space>
            <Button type="primary" onClick={handleAddParticipants}>
              录入参加者信息
            </Button>
          </Space>
        </Card>
      )}

      {application.info_completed && balance > 0 && application.state !== 'cancelled' && (
        <Card title="操作">
          <Space>
            <Button type="primary" onClick={handlePayBalance}>
              支付尾款
            </Button>
            <Button onClick={handleGenerateOrderNo}>
              生成交款单编号
            </Button>
          </Space>
        </Card>
      )}

      {application.state !== 'cancelled' && (
        <Card title="售后操作" style={{ marginTop: 16 }}>
          <Space>
            <Popconfirm
              title="确定要取消此申请吗？"
              onConfirm={handleCancelPreview}
            >
              <Button danger>取消申请</Button>
            </Popconfirm>
            {application.participants && application.participants.length > 1 && (
              <Button danger onClick={() => setPartialCancelVisible(true)}>
                部分取消
              </Button>
            )}
          </Space>
        </Card>
      )}

      <Card title="参加者信息" style={{ marginTop: 16 }}>
        <Table
          dataSource={application.participants || []}
          columns={participantColumns}
          rowKey="id"
          pagination={false}
        />
      </Card>

      <Modal
        title={payType === 'deposit' ? '支付订金' : '支付尾款'}
        open={payModalVisible}
        onOk={handlePaySubmit}
        onCancel={() => { setPayModalVisible(false); setVoucherFiles([]) }}
        confirmLoading={loading}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="支付金额"
            name="amount"
            rules={[{ required: true, message: '请输入支付金额' }]}
          >
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>
          <Form.Item label="支付方式" name="payment_method">
            <Select options={paymentMethodOptions} placeholder="请选择支付方式" allowClear />
          </Form.Item>
          <Form.Item label="支付凭证">
            <Upload
              fileList={voucherFiles}
              onChange={({ fileList }) => setVoucherFiles(fileList)}
              beforeUpload={() => false}
            >
              <Button icon={<UploadOutlined />}>上传凭证</Button>
            </Upload>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="录入参加者信息"
        open={participantModalVisible}
        onOk={handleParticipantsSubmit}
        onCancel={() => setParticipantModalVisible(false)}
        confirmLoading={loading}
        width={800}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="参加者列表">
            <Form.List name="participants">
              {(fields: { key: number; name: number }[]) => (
                <>
                  {fields.map(({ key, name }: { key: number; name: number }) => (
                    <Card key={key} size="small" style={{ marginBottom: 8 }}>
                      <Space>
                        <Form.Item
                          name={[name, 'name']}
                          rules={[{ required: true, message: '请输入姓名' }]}
                        >
                          <Input placeholder="姓名" />
                        </Form.Item>
                        <Form.Item name={[name, 'gender']}>
                          <Select placeholder="性别" allowClear style={{ width: 80 }} options={[
                            { label: '男', value: 'M' },
                            { label: '女', value: 'F' },
                          ]} />
                        </Form.Item>
                        <Form.Item name={[name, 'phone']}>
                          <Input placeholder="电话" onBlur={(e) => handleDuplicateCheck(e.target.value)} />
                        </Form.Item>
                        <Form.Item name={[name, 'is_leader']} valuePropName="checked">
                          <Checkbox>责任人</Checkbox>
                        </Form.Item>
                      </Space>
                    </Card>
                  ))}
                </>
              )}
            </Form.List>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="取消申请确认"
        open={cancelModalVisible}
        onOk={handleCancelConfirm}
        onCancel={() => setCancelModalVisible(false)}
        confirmLoading={loading}
      >
        {cancelPreview && (
          <div>
            <p><strong>已支付总额：</strong>¥{cancelPreview.total_paid}</p>
            <p><strong>取消手续费：</strong>¥{cancelPreview.cancel_fee}</p>
            <p><strong>退款金额：</strong>¥{cancelPreview.refund_amount}</p>
            {cancelPreview.refund_amount >= 5000 && (
              <Alert message="退款金额≥5000元，需主管审批" type="warning" showIcon style={{ marginTop: 8 }} />
            )}
            <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
              <Form.Item label="退款渠道" name="cancel_channel">
                <Select options={refundChannelOptions} placeholder="请选择退款渠道" />
              </Form.Item>
            </Form>
          </div>
        )}
      </Modal>

      <Modal
        title="部分取消"
        open={partialCancelVisible}
        onOk={handlePartialCancel}
        onCancel={() => setPartialCancelVisible(false)}
        confirmLoading={loading}
      >
        <p>选择要取消的参加者（责任人不可直接取消）：</p>
        <Table
          dataSource={(application.participants || []).filter(p => !p.is_leader)}
          columns={[
            { title: '姓名', dataIndex: 'name' },
            { title: '电话', dataIndex: 'phone' },
          ]}
          rowSelection={{
            selectedRowKeys: selectedParticipantIds,
            onChange: (keys) => setSelectedParticipantIds(keys as number[]),
          }}
          rowKey="id"
          pagination={false}
          size="small"
        />
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item label="退款渠道" name="partial_cancel_channel">
            <Select options={refundChannelOptions} placeholder="请选择退款渠道" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default AppDetail
