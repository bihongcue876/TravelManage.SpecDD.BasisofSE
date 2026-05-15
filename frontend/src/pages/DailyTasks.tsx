import { useState } from 'react'
import { Card, Table, DatePicker, Button, Space, Tabs, message, Tag } from 'antd'
import { DownloadOutlined, FileTextOutlined, DollarOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { fetchDailyReminders, fetchDailyFinance, exportDailyFinance } from '../api'
import type { DailyReminderItem } from '../types'
import './DailyTasks.css'

function DailyTasks() {
  const [loading, setLoading] = useState(false)
  const [selectedDate, setSelectedDate] = useState<string | undefined>(dayjs().format('YYYY-MM-DD'))
  const [reminders, setReminders] = useState<DailyReminderItem[]>([])
  const [financeData, setFinanceData] = useState<Record<string, unknown>[]>([])

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
      const result = await exportDailyFinance({ target_date: selectedDate })
      message.success(`导出成功，共 ${result.record_count} 条记录`)
    } catch (error) {
      message.error((error as Error).message)
    }
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
    { title: '截止日期', dataIndex: 'balance_deadline' }
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
    { title: '时间', dataIndex: 'created_at' }
  ]

  const tabItems = [
    {
      key: 'reminders',
      label: (
        <span>
          <FileTextOutlined />
          催款单
        </span>
      ),
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
          </Space>
          <Table
            dataSource={reminders}
            columns={reminderColumns}
            rowKey="app_id"
            loading={loading}
            pagination={false}
          />
        </div>
      )
    },
    {
      key: 'finance',
      label: (
        <span>
          <DollarOutlined />
          财务流水
        </span>
      ),
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
            <Button icon={<DownloadOutlined />} onClick={handleExport}>
              导出
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
    }
  ]

  return (
    <div>
      <h2>催款与报表</h2>
      <Card>
        <Tabs items={tabItems} />
      </Card>
    </div>
  )
}

export default DailyTasks
