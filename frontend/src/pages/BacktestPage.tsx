import { Card, Row, Col, Statistic, Table, Typography, Button, Space } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { Line } from '@ant-design/charts';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const { Title } = Typography;

interface BacktestResult {
  run_id: string;
  sharpe_ratio: number;
  total_return: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  equity_curve: { date: string; value: number }[];
  trades: any[];
}

export default function BacktestPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['backtest-results'],
    queryFn: async () => {
      const response = await axios.get('/api/backtest/results/bt_123456');
      return response.data.data as BacktestResult;
    },
  });

  const equityConfig = {
    data: data?.equity_curve || [],
    xField: 'date',
    yField: 'value',
    smooth: true,
    point: {
      size: 3,
      shape: 'circle',
    },
    tooltip: {
      formatter: (datum: any) => {
        return {
          name: 'Portfolio Value',
          value: `₹${datum.value.toLocaleString('en-IN')}`,
        };
      },
    },
    yAxis: {
      label: {
        formatter: (v: string) => `₹${(+v / 1000).toFixed(0)}K`,
      },
    },
  };

  const tradeColumns = [
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
    },
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `₹${price.toFixed(2)}`,
    },
    {
      title: 'P&L',
      dataIndex: 'pnl',
      key: 'pnl',
      render: (pnl: number) => (
        <span style={{ color: pnl > 0 ? '#3f8600' : '#cf1322' }}>
          ₹{pnl.toFixed(2)}
        </span>
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>Backtest Results</Title>
        <Button type="primary" icon={<PlayCircleOutlined />} size="large">
          Run New Backtest
        </Button>
      </div>

      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Sharpe Ratio"
              value={data?.sharpe_ratio}
              precision={2}
              valueStyle={{ color: '#3f8600' }}
              prefix={<ArrowUpOutlined />}
              suffix=""
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Return"
              value={data ? data.total_return * 100 : 0}
              precision={2}
              valueStyle={{ color: '#3f8600' }}
              suffix="%"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Max Drawdown"
              value={data ? Math.abs(data.max_drawdown * 100) : 0}
              precision={2}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ArrowDownOutlined />}
              suffix="%"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Win Rate"
              value={data ? data.win_rate * 100 : 0}
              precision={0}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Card title="Equity Curve" loading={isLoading}>
        <Line {...equityConfig} />
      </Card>

      <Card title="Trade Log" loading={isLoading}>
        <Table
          dataSource={data?.trades}
          columns={tradeColumns}
          pagination={{ pageSize: 10 }}
          scroll={{ x: true }}
        />
      </Card>
    </Space>
  );
}

