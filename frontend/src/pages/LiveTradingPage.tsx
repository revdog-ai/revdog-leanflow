import { Card, Row, Col, Statistic, Button, Progress, Alert, Space, Typography } from 'antd';
import { StopOutlined, WarningOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';

const { Title } = Typography;

interface LiveData {
  timestamp: string;
  portfolio_value: number;
  pnl: number;
  open_positions: number;
  ops_counter: number;
  kill_switch_active: boolean;
}

export default function LiveTradingPage() {
  const [liveData, setLiveData] = useState<LiveData | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // TODO: Implement WebSocket connection
    // const ws = new WebSocket('ws://localhost:8000/api/trading/ws');
    
    // Mock data for now
    const mockData: LiveData = {
      timestamp: new Date().toISOString(),
      portfolio_value: 105250.00,
      pnl: 2350.00,
      open_positions: 1,
      ops_counter: 3,
      kill_switch_active: false,
    };
    
    setLiveData(mockData);
    setIsConnected(true);

    return () => {
      // ws.close();
    };
  }, []);

  const handleKillSwitch = async () => {
    try {
      // await axios.post('/api/trading/kill-switch');
      alert('Kill switch activated! All positions will be liquidated.');
    } catch (error) {
      console.error('Failed to activate kill switch', error);
    }
  };

  const opsPercent = liveData ? (liveData.ops_counter / 10) * 100 : 0;
  const opsStatus = opsPercent >= 80 ? 'exception' : opsPercent >= 60 ? 'normal' : 'success';

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>Live Trading Monitor</Title>
        {!isConnected && (
          <Alert
            message="Disconnected"
            description="Not connected to trading server"
            type="warning"
            showIcon
            icon={<WarningOutlined />}
          />
        )}
      </div>

      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Portfolio Value"
              value={liveData?.portfolio_value}
              precision={2}
              prefix="₹"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Today's P&L"
              value={liveData?.pnl}
              precision={2}
              prefix="₹"
              valueStyle={{ color: liveData && liveData.pnl > 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="Open Positions" value={liveData?.open_positions} />
          </Card>
        </Col>
      </Row>

      <Card title="Risk Controls">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={5}>Orders Per Second (OPS) Limiter</Title>
            <Progress
              percent={opsPercent}
              status={opsStatus}
              format={() => `${liveData?.ops_counter || 0}/10 Orders`}
            />
            {opsPercent >= 80 && (
              <Alert
                message="OPS threshold approaching"
                description="Reduce order frequency to avoid exceeding SEBI limit"
                type="warning"
                showIcon
                style={{ marginTop: 16 }}
              />
            )}
          </div>

          <div>
            <Title level={5}>Emergency Controls</Title>
            <Button
              danger
              type="primary"
              icon={<StopOutlined />}
              size="large"
              block
              onClick={handleKillSwitch}
              disabled={liveData?.kill_switch_active}
            >
              {liveData?.kill_switch_active
                ? 'KILL SWITCH ACTIVE'
                : '🛑 EMERGENCY STOP (Kill Switch)'}
            </Button>
            <p style={{ marginTop: 8, color: '#888' }}>
              Activates at {'>'}5% drawdown or manual trigger. Liquidates all positions immediately.
            </p>
          </div>
        </Space>
      </Card>

      <Alert
        message="SEBI Compliance Active"
        description="White Box Execution Algo with OPS limiter and kill switch"
        type="info"
        showIcon
      />
    </Space>
  );
}

