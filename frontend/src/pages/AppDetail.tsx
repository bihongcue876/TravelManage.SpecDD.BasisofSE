import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Steps, Button, Table, Modal, Form, InputNumber, Input, message, Alert, Space, Popconfirm } from 'antd'
import { fetchApplication, payDeposit, payBalance, addParticipants, cancelApplication, getCancelPreview } from '../api'
import type { ApplicationDetail, CancelPreview, ParticipantCreate } from '../types'
import './AppDetail.css'

const stateMap: Record<string, { text: string; color: string }> = {
  draft: { text: '草稿', color: 'default' },
  deposit_paid: { text: '订金已付', color: 'processing' },
  confirmed: { text: '已确认', color: 'success' },
  cancelled: { text: '已取消', color: 'error' }
}

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

  useEffect(() => {
    loadApplication()
  }, [id])

  const handlePayDeposit = () => {
    setPayType('deposit')
    setPayModalVisible(true)
  }

  const handlePayBalance = () => {
    setPayType('balance')
    setPayModalVisible(true)
  }

  const handlePaySubmit = async () => {
    if (!id) return
    setLoading(true)
    try {
      const values = await form.validateFields()
      const amount = parseFloat(values.amount)
      if (payType === 'deposit') {
        await payDeposit(parseInt(id), { amount })
        message.success('订金支付成功')
      } else {
        await payBalance(parseInt(id), { amount })
        message.success('尾款支付成功')
      }
      setPayModalVisible(false)
      form.resetFields()
      loadApplication()
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
      await cancelApplication(parseInt(id))
      message.success('申请已取消')
      setCancelModalVisible(false)
      loadApplication()
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  if (!application) return null

  const currentStep = application.state === 'draft' ? 0 :
    application.state === 'deposit_paid' && !application.info_completed ? 1 :
    application.state === 'deposit_paid' && application.info_completed &&
    application.paid_balance < application.total_price - application.paid_deposit ? 2 :
    application.state === 'confirmed' ? 3 : 0

  const balance = application.total_price - application.paid_deposit - application.paid_balance

  const participantColumns = [
    { title: '姓名', dataIndex: 'name', key: 'name' },
    { title: '性别', dataIndex: 'gender', key: 'gender' },
    { title: '电话', dataIndex: 'phone', key: 'phone' },
    { title: '责任人', dataIndex: 'is_leader', key: 'is_leader', render: (v: boolean) => v ? '是' : '否' }
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
      </Card>

      <Card title="申请信息" style={{ marginBottom: 16 }}>
        <Alert
          message={`状态：${stateMap[application.state]?.text || application.state}`}
          type={stateMap[application.state]?.color === 'success' ? 'success' : 'info'}
          style={{ marginBottom: 16 }}
        />
        <p><strong>团代码：</strong>{application.group?.code}</p>
        <p><strong>出发日期：</strong>{application.group?.departure_date}</p>
        <p><strong>申请人：</strong>{application.name}</p>
        <p><strong>电话：</strong>{application.phone}</p>
        <p><strong>人数：</strong>成人 {application.adults} / 儿童 {application.children}</p>
        <p><strong>总费用：</strong>¥{application.total_price}</p>
        <p><strong>应付订金：</strong>¥{application.deposit}</p>
        <p><strong>已付订金：</strong>¥{application.paid_deposit}</p>
        <p><strong>已付尾款：</strong>¥{application.paid_balance}</p>
        <p><strong>余额：</strong>¥{balance}</p>
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
          <Button type="primary" onClick={handleAddParticipants}>
            录入参加者信息
          </Button>
        </Card>
      )}

      {application.info_completed && balance > 0 && (
        <Card title="操作">
          <Button type="primary" onClick={handlePayBalance}>
            支付尾款
          </Button>
        </Card>
      )}

      {application.state !== 'cancelled' && (
        <Card title="售后操作" style={{ marginTop: 16 }}>
          <Popconfirm
            title="确定要取消此申请吗？"
            onConfirm={handleCancelPreview}
          >
            <Button danger>取消申请</Button>
          </Popconfirm>
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
        title="支付"
        open={payModalVisible}
        onOk={handlePaySubmit}
        onCancel={() => setPayModalVisible(false)}
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
                          <Input placeholder="性别" />
                        </Form.Item>
                        <Form.Item name={[name, 'phone']}>
                          <Input placeholder="电话" />
                        </Form.Item>
                        <Form.Item name={[name, 'is_leader']} valuePropName="checked">
                          <input type="checkbox" />
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
          </div>
        )}
      </Modal>
    </div>
  )
}

export default AppDetail
