import { Card, Steps, Collapse, Typography, Tag, Row, Col } from 'antd'
import {
  SearchOutlined,
  FormOutlined,
  DollarOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  FileTextOutlined
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography

const businessSteps = [
  {
    title: '查询旅游团',
    description: '选择出发日期范围，查询可申请的公开旅游团',
    icon: <SearchOutlined />
  },
  {
    title: '创建申请',
    description: '填写申请人信息和出行人数，系统自动计算订金',
    icon: <FormOutlined />
  },
  {
    title: '支付订金',
    description: '按系统计算的订金金额完成支付，锁定团位',
    icon: <DollarOutlined />
  },
  {
    title: '录入参加者',
    description: '录入所有参加者信息，至少指定一位负责人',
    icon: <TeamOutlined />
  },
  {
    title: '支付尾款',
    description: '在尾款截止日期前完成尾款支付，确认行程',
    icon: <CheckCircleOutlined />
  }
]

const faqItems = [
  {
    key: '1',
    label: '订金如何计算？',
    children: (
      <div>
        <Paragraph>订金比例根据申请日期与出发日期的间隔确定：</Paragraph>
        <ul>
          <li><Tag color="blue">≥ 60 天</Tag>订金为总价的 <Text strong>10%</Text></li>
          <li><Tag color="cyan">30 ~ 59 天</Tag>订金为总价的 <Text strong>20%</Text></li>
          <li><Tag color="red">&lt; 30 天</Tag>订金为总价的 <Text strong>100%</Text>（需全额支付）</li>
        </ul>
      </div>
    )
  },
  {
    key: '2',
    label: '取消申请的手续费规则是什么？',
    children: (
      <div>
        <Paragraph>取消手续费根据取消日期与出发日期的间隔确定：</Paragraph>
        <ul>
          <li><Tag color="green">≥ 30 天</Tag>免手续费，全额退款</li>
          <li><Tag color="blue">10 ~ 29 天</Tag>扣除已付总额的 <Text strong>20%</Text> 作为手续费</li>
          <li><Tag color="orange">1 ~ 9 天</Tag>扣除已付总额的 <Text strong>50%</Text> 作为手续费</li>
          <li><Tag color="red">出发当天或已出发</Tag>扣除已付总额的 <Text strong>100%</Text>，不予退款</li>
        </ul>
      </div>
    )
  },
  {
    key: '3',
    label: '尾款支付期限是什么时候？',
    children: (
      <Paragraph>
        尾款支付期限取以下两个日期中较晚的一个：
        <br />
        • 出发日前 30 天
        <br />
        • 交款单发送日起 10 天后
      </Paragraph>
    )
  },
  {
    key: '4',
    label: '申请状态有哪些？各代表什么含义？',
    children: (
      <div>
        <ul>
          <li><Tag color="default">draft（草稿）</Tag>已创建申请，尚未支付订金</li>
          <li><Tag color="blue">deposit_paid（订金已付）</Tag>订金已支付，等待录入参加者信息</li>
          <li><Tag color="green">confirmed（已确认）</Tag>信息已录入且尾款已付清</li>
          <li><Tag color="red">cancelled（已取消）</Tag>申请已取消</li>
        </ul>
      </div>
    )
  },
  {
    key: '5',
    label: '录入参加者有什么要求？',
    children: (
      <div>
        <Paragraph>录入参加者时需满足以下条件：</Paragraph>
        <ul>
          <li>参加者总人数必须与申请时填写的大人+小孩数量一致</li>
          <li>至少指定一位参加者为负责人（is_leader = true）</li>
          <li>已取消的申请无法录入参加者</li>
        </ul>
      </div>
    )
  },
  {
    key: '6',
    label: '催款单是如何生成的？',
    children: (
      <Paragraph>
        系统每天凌晨自动检查前一天信息录入完成的申请，如果该申请尚未付清尾款，
        则会生成催款记录。催款员工可在"催款与报表"页面查看并打印催款单和交款单。
      </Paragraph>
    )
  },
  {
    key: '7',
    label: '旅游团价格发布后还能修改吗？',
    children: (
      <Paragraph>
        旅游团价格一经发布（is_published = true）即被锁定，不可再修改。
        请在确认价格无误后再进行发布操作。
      </Paragraph>
    )
  },
  {
    key: '8',
    label: '名额是如何控制的？',
    children: (
      <Paragraph>
        每个旅游团有最大人数限额（max_pax）。支付订金时会检查当前已报名人数，
        确保不会超过限额。如果团位已满，系统将拒绝新的申请。
      </Paragraph>
    )
  }
]

function HelpPage() {
  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>
        <FileTextOutlined style={{ marginRight: 8 }} />
        使用帮助
      </Title>
      <Paragraph style={{ textAlign: 'center', color: '#666', marginBottom: 40 }}>
        了解系统的主要业务流程和常见问题
      </Paragraph>

      <Card title="主要业务流程" style={{ marginBottom: 24 }}>
        <Steps
          direction="vertical"
          current={-1}
          items={businessSteps.map((step) => ({
            title: step.title,
            description: step.description,
            icon: step.icon
          }))}
        />
      </Card>

      <Row gutter={[24, 24]}>
        <Col xs={24} md={12}>
          <Card
            title={<><CheckCircleOutlined style={{ marginRight: 8 }} />申请流程</>}
            size="small"
            style={{ height: '100%' }}
          >
            <Steps
              direction="vertical"
              current={-1}
              size="small"
              items={[
                { title: '查询旅游团', description: '按日期筛选可申请的团' },
                { title: '创建申请', description: '填写信息，系统计算订金' },
                { title: '支付订金', description: '支付订金锁定团位' },
                { title: '录入参加者', description: '录入所有出行人信息' },
                { title: '支付尾款', description: '付清尾款确认行程' }
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card
            title={<><CloseCircleOutlined style={{ marginRight: 8 }} />取消流程</>}
            size="small"
            style={{ height: '100%' }}
          >
            <Steps
              direction="vertical"
              current={-1}
              size="small"
              items={[
                { title: '提交取消申请', description: '在申请详情页点击取消' },
                { title: '计算退款', description: '系统自动计算手续费和退款金额' },
                { title: '确认取消', description: '确认后申请状态变为已取消' },
                { title: '退款处理', description: '退款金额按规则自动计算' }
              ]}
            />
          </Card>
        </Col>
      </Row>

      <Card title="常见问题" style={{ marginTop: 24, marginBottom: 48 }}>
        <Collapse accordion items={faqItems} />
      </Card>
    </div>
  )
}

export default HelpPage
