import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Form, Input, InputNumber, Button, Card, message, Alert, Space, Descriptions } from 'antd'
import { fetchGroup, fetchPricingPreview, fetchBalanceDeadline, createApplication } from '../api'
import type { GroupDetail, PricingPreview, BalanceDeadline } from '../types'
import './ApplyCreate.css'

function ApplyCreate() {
  const { groupId } = useParams<{ groupId: string }>()
  const navigate = useNavigate()
  const [group, setGroup] = useState<GroupDetail | null>(null)
  const [pricing, setPricing] = useState<PricingPreview | null>(null)
  const [balanceDeadline, setBalanceDeadline] = useState<BalanceDeadline | null>(null)
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    const loadData = async () => {
      if (!groupId) return
      try {
        const groupData = await fetchGroup(parseInt(groupId))
        setGroup(groupData)
      } catch (error) {
        message.error((error as Error).message)
      }
    }
    loadData()
  }, [groupId])

  const handleValuesChange = async (changedValues: Record<string, unknown>) => {
    if (changedValues.adults !== undefined || changedValues.children !== undefined) {
      const values = form.getFieldsValue()
      const adults = values.adults || 1
      const children = values.children || 0
      if (groupId) {
        try {
          const [preview, deadline] = await Promise.all([
            fetchPricingPreview(parseInt(groupId), { adults, children }),
            fetchBalanceDeadline(parseInt(groupId)),
          ])
          setPricing(preview)
          setBalanceDeadline(deadline)
        } catch {
          // ignore
        }
      }
    }
  }

  const handleSubmit = async (values: Record<string, unknown>) => {
    if (!groupId) return
    setLoading(true)
    try {
      const application = await createApplication({
        group_id: parseInt(groupId),
        name: values.name as string,
        phone: values.phone as string,
        email: values.email as string | undefined,
        address: values.address as string | undefined,
        zip_code: values.zip_code as string | undefined,
        adults: values.adults as number,
        children: values.children as number
      })
      message.success('申请创建成功')
      navigate(`/applications/${application.id}`)
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  if (!group) return null

  return (
    <div className="apply-container">
      <Card title="创建申请">
        <Alert
          message="旅游团信息"
          description={
            <div>
              <p><strong>团代码：</strong>{group.code}</p>
              <p><strong>出发日期：</strong>{group.departure_date}</p>
              <p><strong>成人价：</strong>¥{group.adult_price} / <strong>儿童价：</strong>¥{group.child_price}</p>
            </div>
          }
          style={{ marginBottom: 24 }}
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          onValuesChange={handleValuesChange}
          initialValues={{ adults: 1, children: 0 }}
        >
          <Form.Item
            label="申请人姓名"
            name="name"
            rules={[{ required: true, message: '请输入申请人姓名' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="联系电话"
            name="phone"
            rules={[{ required: true, message: '请输入联系电话' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item label="Email" name="email">
            <Input />
          </Form.Item>

          <Form.Item label="联系地址" name="address">
            <Input.TextArea />
          </Form.Item>

          <Form.Item label="邮编" name="zip_code">
            <Input />
          </Form.Item>

          <Form.Item label="成人人数" name="adults">
            <InputNumber min={1} max={10} />
          </Form.Item>

          <Form.Item label="儿童人数" name="children">
            <InputNumber min={0} max={10} />
          </Form.Item>

          {pricing && (
            <Alert
              message="订金支付预览"
              description={
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="总费用">¥{pricing.total_price}</Descriptions.Item>
                  <Descriptions.Item label="订金比例">{pricing.deposit_rate}</Descriptions.Item>
                  <Descriptions.Item label="应付订金">¥{pricing.deposit}</Descriptions.Item>
                  <Descriptions.Item label="剩余尾款">¥{pricing.total_price - pricing.deposit}</Descriptions.Item>
                  {balanceDeadline && (
                    <Descriptions.Item label="尾款支付截止日">{balanceDeadline.balance_deadline}</Descriptions.Item>
                  )}
                </Descriptions>
              }
              type="info"
              style={{ marginBottom: 16 }}
            />
          )}

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                提交申请
              </Button>
              <Button onClick={() => navigate('/groups')}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default ApplyCreate
