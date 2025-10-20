import { Card, Form, InputNumber, Button, Space, Typography, message, Divider } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { useState } from 'react';
import axios from 'axios';

const { Title, Paragraph } = Typography;

interface StrategyConfig {
  vwap_window: number;
  twap_slices: number;
  order_size: number;
  drawdown_threshold: number;
  ops_limit: number;
}

export default function ConfigurationPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSave = async (values: StrategyConfig) => {
    setLoading(true);
    try {
      await axios.post('/api/strategy/config', values);
      message.success('Configuration saved successfully');
    } catch (error) {
      message.error('Failed to save configuration');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    form.setFieldsValue({
      vwap_window: 100,
      twap_slices: 10,
      order_size: 10,
      drawdown_threshold: 0.05,
      ops_limit: 10,
    });
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={2}>Strategy Configuration</Title>

      <Card title="VWAP/TWAP Parameters">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={{
            vwap_window: 100,
            twap_slices: 10,
            order_size: 10,
            drawdown_threshold: 0.05,
            ops_limit: 10,
          }}
        >
          <Form.Item
            label="VWAP Window Size"
            name="vwap_window"
            rules={[
              { required: true },
              { type: 'number', min: 10, max: 500, message: 'Must be between 10 and 500' },
            ]}
            tooltip="Number of bars to calculate VWAP. Higher = smoother, Lower = more responsive"
          >
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="TWAP Slices"
            name="twap_slices"
            rules={[
              { required: true },
              { type: 'number', min: 5, max: 20, message: 'Must be between 5 and 20' },
            ]}
            tooltip="Number of time slices to divide order execution. More slices = better price averaging"
          >
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="Order Size"
            name="order_size"
            rules={[{ required: true }, { type: 'number', min: 1, message: 'Must be at least 1' }]}
            tooltip="Number of shares per order"
          >
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>

          <Divider />

          <Title level={4}>Risk Management (SEBI Compliance)</Title>
          <Paragraph type="secondary">
            These settings ensure compliance with SEBI White Box Execution Algo guidelines
          </Paragraph>

          <Form.Item
            label="Drawdown Threshold (%)"
            name="drawdown_threshold"
            rules={[
              { required: true },
              { type: 'number', min: 0.01, max: 0.2, message: 'Must be between 1% and 20%' },
            ]}
            tooltip="Kill switch activates when drawdown exceeds this threshold. SEBI recommends 5%"
          >
            <InputNumber
              style={{ width: '100%' }}
              formatter={(value) => `${(Number(value) * 100).toFixed(0)}%`}
              parser={(value) => Number(value?.replace('%', '')) / 100}
              step={0.01}
            />
          </Form.Item>

          <Form.Item
            label="Orders Per Second Limit"
            name="ops_limit"
            rules={[
              { required: true },
              { type: 'number', min: 1, max: 10, message: 'SEBI limit is max 10' },
            ]}
            tooltip="Maximum orders per second. SEBI regulation requires ≤10"
          >
            <InputNumber style={{ width: '100%' }} max={10} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
                Save Configuration
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                Reset to Defaults
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card title="Configuration Info">
        <Paragraph>
          <strong>VWAP (Volume Weighted Average Price)</strong>: Executes orders when price crosses
          VWAP threshold. Used for large orders to minimize market impact.
        </Paragraph>
        <Paragraph>
          <strong>TWAP (Time Weighted Average Price)</strong>: Spreads order execution evenly over
          time. Useful for illiquid securities to avoid slippage.
        </Paragraph>
        <Paragraph type="warning">
          <strong>Important</strong>: Changing these parameters affects strategy performance and
          risk profile. Always backtest before live trading.
        </Paragraph>
      </Card>
    </Space>
  );
}

