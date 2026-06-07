import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Table, Button, Space, DatePicker, Card, Row, Col, message } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { fetchGroups } from '../api'
import type { Group } from '../types'
import { formatDate } from '../utils'
import './GroupList.css'

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
    } catch (error) {
      message.error((error as Error).message)
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

  const columns: ColumnsType<Group> = [
    { title: '团代码', dataIndex: 'code', key: 'code' },
    { title: '截止日期', dataIndex: 'deadline', key: 'deadline', render: (v: string) => formatDate(v) },
    { title: '出发日期', dataIndex: 'departure_date', key: 'departure_date', render: (v: string) => formatDate(v) },
    {
      title: '成人价',
      dataIndex: 'adult_price',
      key: 'adult_price',
      render: (v: number | null) => v !== null ? `¥${v}` : '-'
    },
    {
      title: '儿童价',
      dataIndex: 'child_price',
      key: 'child_price',
      render: (v: number | null) => v !== null ? `¥${v}` : '-'
    },
    { title: '名额', dataIndex: 'max_pax', key: 'max_pax' },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: Group) => (
        <Button type="primary" onClick={() => navigate(`/apply/${record.id}`)}>
          申请
        </Button>
      )
    }
  ]

  return (
    <div>
      <Card title="查询旅游团" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <RangePicker onChange={handleDateChange} style={{ width: '100%' }} />
          </Col>
          <Col>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} onClick={loadGroups}>
                查询
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      <Card title="可选旅游团">
        <Table
          dataSource={groups}
          columns={columns}
          rowKey="id"
          loading={loading}
        />
      </Card>
    </div>
  )
}

export default GroupList
