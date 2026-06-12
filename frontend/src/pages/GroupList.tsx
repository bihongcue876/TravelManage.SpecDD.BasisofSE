import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Space, DatePicker, Card, Row, Col, Tag, Spin, Empty } from 'antd'
import { SearchOutlined, CalendarOutlined, TeamOutlined, DollarOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { fetchGroups } from '../api'
import type { Group } from '../types'
import { formatDate } from '../utils'

const { RangePicker } = DatePicker

function GroupList() {
  const navigate = useNavigate()
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState<{
    departureFrom?: string
    departureTo?: string
  }>({})

  const loadGroups = async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { status: 'published' }
      if (filters.departureFrom) params.departure_from = filters.departureFrom
      if (filters.departureTo) params.departure_to = filters.departureTo
      const data = await fetchGroups(params)
      setGroups(data)
    } catch {
      // error handled by interceptor
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadGroups()
  }, [])

  const handleDateChange = (dates: [dayjs.Dayjs | null, dayjs.Dayjs | null] | null) => {
    if (dates && dates[0] && dates[1]) {
      setFilters({
        departureFrom: dates[0].format('YYYY-MM-DD'),
        departureTo: dates[1].format('YYYY-MM-DD')
      })
    } else {
      setFilters({})
    }
  }

  return (
    <div>
      <Card
        style={{ marginBottom: 24, borderRadius: 8 }}
        styles={{ body: { padding: '16px 24px' } }}
      >
        <Row justify="space-between" align="middle">
          <Col>
            <Space size={16}>
              <RangePicker onChange={handleDateChange} style={{ width: 280 }} placeholder={['出发开始', '出发结束']} />
              <Button type="primary" icon={<SearchOutlined />} onClick={loadGroups}>
                查询
              </Button>
            </Space>
          </Col>
          <Col>
            <span style={{ color: '#999', fontSize: 13 }}>共 {groups.length} 个旅游团</span>
          </Col>
        </Row>
      </Card>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>
      ) : groups.length === 0 ? (
        <Empty description="暂无可选旅游团" />
      ) : (
        <Row gutter={[20, 20]}>
          {groups.map(group => {
            const avail = group.available ?? (group.max_pax - (group.occupied ?? 0))
            return (
              <Col xs={24} sm={12} lg={8} xl={6} key={group.id}>
                <Card
                  hoverable
                  style={{ borderRadius: 8, height: '100%', display: 'flex', flexDirection: 'column' }}
                  styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column' } }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <Tag color="#0958d9" style={{ fontSize: 13, padding: '2px 10px' }}>{group.code}</Tag>
                      <Tag color={avail > 0 ? 'success' : 'error'}>
                        余 {avail} 席
                      </Tag>
                    </div>

                    <div style={{ marginBottom: 8, color: '#666', fontSize: 13 }}>
                      <CalendarOutlined style={{ marginRight: 6, color: '#0958d9' }} />
                      {formatDate(group.departure_date)} 出发
                    </div>

                    <div style={{ marginBottom: 8, color: '#999', fontSize: 12 }}>
                      截止报名：{formatDate(group.deadline)}
                    </div>

                    <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
                      <div>
                        <DollarOutlined style={{ color: '#0958d9', marginRight: 4 }} />
                        <span style={{ fontSize: 12, color: '#999' }}>成人</span>
                        <span style={{ fontSize: 16, fontWeight: 600, color: '#0958d9', marginLeft: 4 }}>
                          {group.adult_price !== null ? `¥${group.adult_price}` : '-'}
                        </span>
                      </div>
                      <div>
                        <span style={{ fontSize: 12, color: '#999' }}>儿童</span>
                        <span style={{ fontSize: 16, fontWeight: 600, color: '#0958d9', marginLeft: 4 }}>
                          {group.child_price !== null ? `¥${group.child_price}` : '-'}
                        </span>
                      </div>
                    </div>

                    <div style={{ color: '#999', fontSize: 12 }}>
                      <TeamOutlined style={{ marginRight: 4 }} />
                      总名额 {group.max_pax} · 已报名 {group.occupied ?? 0}
                    </div>
                  </div>

                  <Button
                    type="primary"
                    block
                    disabled={avail <= 0}
                    onClick={() => navigate(`/apply/${group.id}`)}
                    style={{ marginTop: 16, borderRadius: 8 }}
                  >
                    {avail > 0 ? '立即申请' : '名额已满'}
                  </Button>
                </Card>
              </Col>
            )
          })}
        </Row>
      )}
    </div>
  )
}

export default GroupList
