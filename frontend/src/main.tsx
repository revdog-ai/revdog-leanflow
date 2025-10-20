import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider, theme } from 'antd';
import App from './App';
import { useThemeStore } from './stores/themeStore';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function Root() {
  const { isDarkMode } = useThemeStore();

  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider
          theme={{
            algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
            token: {
              colorPrimary: '#1890ff',
            },
          }}
        >
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ConfigProvider>
      </QueryClientProvider>
    </React.StrictMode>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(<Root />);

