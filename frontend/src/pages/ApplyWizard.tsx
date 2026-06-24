import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Steps, Button, Card, InputNumber, Input, Select, Descriptions, message, Alert, Space, Spin } from 'antd'
import { fetchGroup, fetchPricingPreview, fetchBalanceDeadline, createApplication } from '../api'
import type { GroupDetail, PricingPreview, BalanceDeadline, PaymentMethod } from '../types'
import { calculateDeposit } from '../utils/FeeCalculator'
import './ApplyCreate.css'

interface WizardFormData {
  adults: number
  children: number
  name: string
  phone: string
  payment_method: PaymentMethod | undefined
  amount: number
}

const paymentMethodOptions = [
  { label: '现金', value: 'cash' },
  { label: '银行转账', value: 'bank_transfer' },
  { label: '微信', value: 'wechat' },
  { label: '支付宝', value: 'alipay' },
]

function ApplyWizard() {
  const { groupId } = useParams<{ groupId: string }>()
  const navigate = useNavigate()
  const [group, setGroup] = useState<GroupDetail | null>(null)
  const [pricing, setPricing] = useState<PricingPreview | null>(null)
  const [balanceDeadline, setBalanceDeadline] = useState<BalanceDeadline | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState<WizardFormData>({
    adults: 1,
    children: 0,
    name: '',
    phone: '',
    payment_method: undefined,
    amount: 0,
  })

  useEffect(() => {
    if (!groupId) return
    fetchGroup(parseInt(groupId)).then(setGroup).catch(() => {
      message.error('加载旅游团信息失败')
    })
  }, [groupId])

  const updateFormData = (patch: Partial<WizardFormData>) => {
    setFormData(prev => ({ ...prev, ...patch }))
  }

  const handlePricingPreview = async (adults: number, children: number) => {
    if (!groupId) return
    try {
      const [preview, deadline] = await Promise.all([
        fetchPricingPreview(parseInt(groupId), { adults, children }),
        fetchBalanceDeadline(parseInt(groupId)),
      ])
      setPricing(preview)
      setBalanceDeadline(deadline)
      updateFormData({ amount: preview.deposit })
    } catch {
      // ignore
    }
  }

  const handleAdultsChange = (val: number | null) => {
    const adults = val ?? 1
    updateFormData({ adults })
    handlePricingPreview(adults, formData.children)
  }

  const handleChildrenChange = (val: number | null) => {
    const children = val ?? 0
    updateFormData({ children })
    handlePricingPreview(formData.adults, children)
  }

  const localDepositPreview = group
    ? calculateDeposit(group.departure_date, (group.adult_price ?? 0) * formData.adults + (group.child_price ?? 0) * formData.children)
    : null

  const canGoNext = (): boolean => {
    if (currentStep === 0) return formData.adults >= 1
    if (currentStep === 1) {
      if (!formData.name.trim()) return false
      if (!/^1\d{10}$/.test(formData.phone)) return false
      if (pricing && formData.amount < pricing.deposit) return false
    }
    return true
  }

  const handleNext = () => {
    if (currentStep === 0 && formData.adults < 1) {
      message.warning('请至少选择1位成人')
      return
    }
    if (currentStep === 1) {
      if (!formData.name.trim()) {
        message.warning('请输入责任人姓名')
        return
      }
      if (!/^1\d{10}$/.test(formData.phone)) {
        message.warning('请输入正确的11位手机号')
        return
      }
      if (pricing && formData.amount < pricing.deposit) {
        message.warning('支付金额不能低于应付订金')
        return
      }
    }
    setCurrentStep(prev => Math.min(prev + 1, 2))
  }

  const handlePrev = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0))
  }

  const handleStepClick = (step: number) => {
    if (step < currentStep) {
      setCurrentStep(step)
    }
  }

  const handleSubmit = async () => {
    if (!groupId) return
    setSubmitting(true)
    try {
      const application = await createApplication({
        group_id: parseInt(groupId),
        name: formData.name,
        phone: formData.phone,
        adults: formData.adults,
        children: formData.children,
      })
      message.success('申请创建成功')
      navigate(`/applications/${application.id}`)
    } catch (error) {
      message.error((error as Error).message || '提交失败，请检查网络后重试')
    } finally {
      setSubmitting(false)
    }
  }

  if (!group) {
    return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>
  }

  const stepContent = [
    <div key="step1">
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
      <div style={{ display: 'flex', gap: 24, marginBottom: 24 }}>
        <div>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>成人人数</div>
          <InputNumber min={1} max={10} value={formData.adults} onChange={handleAdultsChange} style={{ width: 120 }} />
        </div>
        <div>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>儿童人数</div>
          <InputNumber min={0} max={10} value={formData.children} onChange={handleChildrenChange} style={{ width: 120 }} />
        </div>
      </div>
      {(pricing || localDepositPreview) && (
        <Card size="small" title="订金预览" style={{ marginBottom: 16, borderRadius: 8 }}>
          <Descriptions column={1} size="small">
            <Descriptions.Item label="总费用">¥{pricing?.total_price ?? (localDepositPreview?.deposit ?? 0)}</Descriptions.Item>
            <Descriptions.Item label="订金比例">{pricing?.deposit_rate ?? localDepositPreview?.rateLabel}</Descriptions.Item>
            <Descriptions.Item label="应付订金">¥{pricing?.deposit ?? localDepositPreview?.deposit}</Descriptions.Item>
            {balanceDeadline && (
              <Descriptions.Item label="尾款截止日">{balanceDeadline.balance_deadline}</Descriptions.Item>
            )}
          </Descriptions>
        </Card>
      )}
    </div>,

    <div key="step2">
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8, fontWeight: 500 }}>责任人姓名 <span style={{ color: '#ff4d4f' }}>*</span></div>
        <Input
          value={formData.name}
          onChange={e => updateFormData({ name: e.target.value })}
          placeholder="请输入责任人姓名"
          status={formData.name.trim() === '' ? '' : undefined}
        />
      </div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8, fontWeight: 500 }}>联系电话 <span style={{ color: '#ff4d4f' }}>*</span></div>
        <Input
          value={formData.phone}
          onChange={e => updateFormData({ phone: e.target.value })}
          placeholder="请输入11位手机号"
          maxLength={11}
        />
      </div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8, fontWeight: 500 }}>支付方式</div>
        <Select
          value={formData.payment_method}
          onChange={val => updateFormData({ payment_method: val as PaymentMethod })}
          options={paymentMethodOptions}
          placeholder="请选择支付方式"
          allowClear
          style={{ width: '100%' }}
        />
      </div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8, fontWeight: 500 }}>支付金额 <span style={{ color: '#ff4d4f' }}>*</span></div>
        <InputNumber
          value={formData.amount}
          onChange={val => updateFormData({ amount: val ?? 0 })}
          min={0}
          style={{ width: '100%' }}
          addonAfter="元"
        />
        {pricing && formData.amount < pricing.deposit && (
          <div style={{ color: '#ff4d4f', fontSize: 12, marginTop: 4 }}>
            支付金额不能低于应付订金 ¥{pricing.deposit}
          </div>
        )}
      </div>
    </div>,

    <div key="step3">
      <Card size="small" title="确认申请信息" style={{ borderRadius: 8 }}>
        <Descriptions column={2} size="small">
          <Descriptions.Item label="团代码">{group.code}</Descriptions.Item>
          <Descriptions.Item label="出发日期">{group.departure_date}</Descriptions.Item>
          <Descriptions.Item label="成人人数">{formData.adults}</Descriptions.Item>
          <Descriptions.Item label="儿童人数">{formData.children}</Descriptions.Item>
          <Descriptions.Item label="责任人姓名">{formData.name}</Descriptions.Item>
          <Descriptions.Item label="联系电话">{formData.phone}</Descriptions.Item>
          <Descriptions.Item label="支付方式">
            {paymentMethodOptions.find(o => o.value === formData.payment_method)?.label ?? '-'}
          </Descriptions.Item>
          <Descriptions.Item label="支付金额">¥{formData.amount}</Descriptions.Item>
          {pricing && (
            <>
              <Descriptions.Item label="总费用">¥{pricing.total_price}</Descriptions.Item>
              <Descriptions.Item label="应付订金">¥{pricing.deposit}</Descriptions.Item>
            </>
          )}
          {balanceDeadline && (
            <Descriptions.Item label="尾款截止日" span={2}>{balanceDeadline.balance_deadline}</Descriptions.Item>
          )}
        </Descriptions>
      </Card>
    </div>,
  ]

  return (
    <div className="apply-container">
      <Card title="申请参加旅游团" style={{ borderRadius: 8 }}>
        <Steps
          current={currentStep}
          onChange={handleStepClick}
          style={{ marginBottom: 32 }}
          items={[
            { title: '选择人数与确认订金' },
            { title: '填写责任人信息与支付' },
            { title: '确认提交' },
          ]}
        />

        {stepContent[currentStep]}

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 24 }}>
          <Button onClick={() => navigate('/groups')}>
            取消
          </Button>
          <Space>
            {currentStep > 0 && (
              <Button onClick={handlePrev}>
                上一步
              </Button>
            )}
            {currentStep < 2 ? (
              <Button type="primary" onClick={handleNext} disabled={!canGoNext()}>
                下一步
              </Button>
            ) : (
              <Button type="primary" onClick={handleSubmit} loading={submitting}>
                提交申请
              </Button>
            )}
          </Space>
        </div>
      </Card>
    </div>
  )
}

export default ApplyWizard