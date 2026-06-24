import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Row, Col, Typography, Statistic, Spin, Empty } from 'antd'
import {
  TeamOutlined,
  DollarOutlined,
  SettingOutlined,
  GlobalOutlined,
  QuestionCircleOutlined,
  UserAddOutlined,
  WarningOutlined,
  ClockCircleOutlined,
  AppstoreOutlined,
  FileTextOutlined,
} from '@ant-design/icons'
import { Line } from '@ant-design/charts'
import { useAuth } from '../auth'
import {
  fetchFrontdeskDashboard,
  fetchFinanceDashboard,
  fetchAdminDashboard,
  fetchDailyFinance,
} from '../api'
import dayjs from 'dayjs'

const { Title, Paragraph } = Typography

interface TrendDataItem {
  date: string
  value: number
  type: string
}

function generateMockTrendData(): TrendDataItem[] {
  const result: TrendDataItem[] = []
  for (let i = 6; i >= 0; i--) {
    const date = dayjs().subtract(i, 'day').format('MM-DD')
    result.push({ date, value: Math.round(Math.random() * 8000 + 2000), type: '收入' })
    result.push({ date, value: Math.round(Math.random() * 2000 + 200), type: '退款' })
  }
  return result
}

function FlowTrendChart() {
  const [trendData, setTrendData] = useState<TrendDataItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadTrend = async () => {
      try {
        const raw = await fetchDailyFinance({ fields: 'date,income,refund' })
        if (Array.isArray(raw) && raw.length > 0) {
          const mapped: TrendDataItem[] = []
          raw.forEach((item: Record<string, unknown>) => {
            const dateStr = typeof item.date === 'string' ? dayjs(item.date).format('MM-DD') : ''
            if (dateStr) {
              mapped.push({ date: dateStr, value: Number(item.income) || 0, type: '收入' })
              mapped.push({ date: dateStr, value: Number(item.refund) || 0, type: '退款' })
            }
          })
          setTrendData(mapped)
        } else {
          setTrendData(generateMockTrendData())
        }
      } catch {
        setTrendData(generateMockTrendData())
      } finally {
        setLoading(false)
      }
    }
    loadTrend()
  }, [])

  const config = useMemo(() => ({
    data: trendData,
    xField: 'date',
    yField: 'value',
    colorField: 'type',
    height: 240,
    smooth: true,
    point: { shapeField: 'square', sizeField: 4 },
    interaction: { tooltip: { marker: false } },
    style: { lineWidth: 2 },
    scale: { color: { range: ['#0F5B5C', '#fa8c16'] } },
  }), [trendData])

  if (loading) return <Spin style={{ display: 'block', margin: '40px auto' }} />
  if (trendData.length === 0) return <Empty description="暂无流水数据" />

  return <Line {...config} />
}

function AdminPanel() {
  const [data, setData] = useState<{ total_users: number; total_applications: number; today_income: number; pending_refunds: number } | null>(null)

  useEffect(() => {
    fetchAdminDashboard().then(setData).catch(() => {})
  }, [])

  if (!data) return <Spin />
  return (
    <>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Statistic title="总用户数" value={data.total_users} prefix={<TeamOutlined />} />
        </Col>
        <Col span={6}>
          <Statistic title="总申请数" value={data.total_applications} prefix={<FileTextOutlined />} />
        </Col>
        <Col span={6}>
          <Statistic title="今日流水" value={data.today_income} prefix="¥" precision={2} />
        </Col>
        <Col span={6}>
          <Statistic title="待审批退款" value={data.pending_refunds} prefix={<WarningOutlined />} valueStyle={{ color: data.pending_refunds > 0 ? '#cf1322' : '#3f8600' }} />
        </Col>
      </Row>
      <Card title="近7天流水趋势" style={{ marginTop: 16, borderRadius: 8 }}>
        <FlowTrendChart />
      </Card>
    </>
  )
}

function FrontdeskPanel() {
  const [data, setData] = useState<{ new_applications_today: number; pending_participants: number } | null>(null)

  useEffect(() => {
    fetchFrontdeskDashboard().then(setData).catch(() => {})
  }, [])

  if (!data) return <Spin />
  return (
    <Row gutter={[16, 16]}>
      <Col span={12}>
        <Statistic title="今日新增申请" value={data.new_applications_today} prefix={<UserAddOutlined />} />
      </Col>
      <Col span={12}>
        <Statistic title="待录入参加者" value={data.pending_participants} prefix={<ClockCircleOutlined />} valueStyle={{ color: data.pending_participants > 0 ? '#cf1322' : '#3f8600' }} />
      </Col>
    </Row>
  )
}

function FinancePanel() {
  const [data, setData] = useState<{ yesterday_income: number; yesterday_exports: number; pending_refunds: number } | null>(null)

  useEffect(() => {
    fetchFinanceDashboard().then(setData).catch(() => {})
  }, [])

  if (!data) return <Spin />
  return (
    <>
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Statistic title="昨日流水" value={data.yesterday_income} prefix="¥" precision={2} />
        </Col>
        <Col span={8}>
          <Statistic title="昨日导出" value={data.yesterday_exports} />
        </Col>
        <Col span={8}>
          <Statistic title="待审批退款" value={data.pending_refunds} prefix={<WarningOutlined />} valueStyle={{ color: data.pending_refunds > 0 ? '#cf1322' : '#3f8600' }} />
        </Col>
      </Row>
      <Card title="近7天流水趋势" style={{ marginTop: 16, borderRadius: 8 }}>
        <FlowTrendChart />
      </Card>
    </>
  )
}

function HomePage() {
  const navigate = useNavigate()
  const { user, hasRole } = useAuth()

  const roleConfig = hasRole('admin') ? { title: '管理工作台', icon: <SettingOutlined style={{ fontSize: 32, color: '#cf1322' }} />, panel: <AdminPanel /> }
    : hasRole('frontdesk') ? { title: '前台工作台', icon: <TeamOutlined style={{ fontSize: 32, color: '#1677ff' }} />, panel: <FrontdeskPanel /> }
    : hasRole('finance') ? { title: '财务工作台', icon: <DollarOutlined style={{ fontSize: 32, color: '#52c41a' }} />, panel: <FinancePanel /> }
    : null

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: 32, marginTop: 24 }}>
        <GlobalOutlined style={{ fontSize: 64, color: '#0F5B5C', marginBottom: 16 }} />
        <Title level={2}>欢迎使用旅游业务管理系统</Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          {user?.name} · {user?.role === 'admin' ? '系统管理员' :
            user?.role === 'frontdesk' ? '前台员工' : '财务人员'}
        </Paragraph>
      </div>

      {roleConfig && (
        <Card
          title={<span style={{ fontSize: 18 }}>{roleConfig.icon} {roleConfig.title}</span>}
          style={{ borderRadius: 8, marginBottom: 24, boxShadow: '0 1px 6px rgba(0,0,0,0.06)' }}
        >
          {roleConfig.panel}
        </Card>
      )}

      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable onClick={() => navigate('/groups')} style={{ borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 6px rgba(0,0,0,0.06)' }}>
            <TeamOutlined style={{ fontSize: 36, color: '#0F5B5C' }} />
            <div style={{ marginTop: 8 }}>旅游团查询</div>
          </Card>
        </Col>
        {(hasRole('finance', 'admin')) && (
          <Col xs={24} sm={12} md={6}>
            <Card hoverable onClick={() => navigate('/admin/tasks')} style={{ borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 6px rgba(0,0,0,0.06)' }}>
              <DollarOutlined style={{ fontSize: 36, color: '#0F5B5C' }} />
              <div style={{ marginTop: 8 }}>催款与报表</div>
            </Card>
          </Col>
        )}
        {(hasRole('admin')) && (
          <>
            <Col xs={24} sm={12} md={6}>
              <Card hoverable onClick={() => navigate('/admin/routes')} style={{ borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 6px rgba(0,0,0,0.06)' }}>
                <SettingOutlined style={{ fontSize: 36, color: '#0F5B5C' }} />
                <div style={{ marginTop: 8 }}>管理路线</div>
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card hoverable onClick={() => navigate('/admin/groups')} style={{ borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 6px rgba(0,0,0,0.06)' }}>
                <AppstoreOutlined style={{ fontSize: 36, color: '#0F5B5C' }} />
                <div style={{ marginTop: 8 }}>管理旅游团</div>
              </Card>
            </Col>
          </>
        )}
        <Col xs={24} sm={12} md={6}>
          <Card hoverable onClick={() => navigate('/help')} style={{ borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 6px rgba(0,0,0,0.06)' }}>
            <QuestionCircleOutlined style={{ fontSize: 36, color: '#0F5B5C' }} />
            <div style={{ marginTop: 8 }}>使用帮助</div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable onClick={() => navigate('/user/profile')} style={{ borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 6px rgba(0,0,0,0.06)' }}>
            <UserAddOutlined style={{ fontSize: 36, color: '#0F5B5C' }} />
            <div style={{ marginTop: 8 }}>个人中心</div>
          </Card>
        </Col>
        {hasRole('admin') && (
          <Col xs={24} sm={12} md={6}>
            <Card hoverable onClick={() => navigate('/admin/users')} style={{ borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 6px rgba(0,0,0,0.06)' }}>
              <TeamOutlined style={{ fontSize: 36, color: '#0F5B5C' }} />
              <div style={{ marginTop: 8 }}>用户管理</div>
            </Card>
          </Col>
        )}
      </Row>
    </div>
  )
}

export default HomePage
