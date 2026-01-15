import { useState, useEffect } from 'react';
import './HealthDashboard.css';

interface ServiceHealth {
  name: string;
  endpoint: string;
  status: 'ok' | 'ko' | 'loading';
  responseTime?: number;
}

const HealthDashboard = () => {
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  
  const [services, setServices] = useState<ServiceHealth[]>([
    { name: 'Auth Service', endpoint: `${backendUrl}/auth/health`, status: 'loading' },
    { name: 'Chatbot Service', endpoint: `${backendUrl}/chatbot/health`, status: 'loading' },
    { name: 'Chatbot Evaluate', endpoint: `${backendUrl}/chatbot-evaluate/health`, status: 'loading' },
    { name: 'Chatbot Index', endpoint: `${backendUrl}/chatbot-index/health`, status: 'loading' },
  ]);

  const checkHealth = async (service: ServiceHealth): Promise<ServiceHealth> => {
    const startTime = performance.now();
    try {
      const response = await fetch(service.endpoint, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });
      const endTime = performance.now();
      
      return {
        ...service,
        status: response.ok ? 'ok' : 'ko',
        responseTime: Math.round(endTime - startTime),
      };
    } catch (error) {
      return {
        ...service,
        status: 'ko',
        responseTime: undefined,
      };
    }
  };

  const checkAllServices = async () => {
    setServices(prev => prev.map(s => ({ ...s, status: 'loading' as const })));
    
    const results = await Promise.all(services.map(checkHealth));
    setServices(results);
  };

  const checkSingleService = async (index: number) => {
    setServices(prev => prev.map((s, i) => i === index ? { ...s, status: 'loading' as const } : s));
    
    const result = await checkHealth(services[index]);
    setServices(prev => prev.map((s, i) => i === index ? result : s));
  };

  useEffect(() => {
    checkAllServices();
  }, []);

  return (
    <div className="health-dashboard">
      <h1>Service Health Dashboard</h1>
      
      <button onClick={checkAllServices} className="refresh-button">
        Refresh All
      </button>

      <div className="services-grid">
        {services.map((service, index) => (
          <div key={index} className={`service-card ${service.status}`}>
            <h3>{service.name}</h3>
            <div className="status-indicator">
              {service.status === 'loading' && <span className="loading">⟳ Checking...</span>}
              {service.status === 'ok' && <span className="ok">✓ OK</span>}
              {service.status === 'ko' && <span className="ko">✗ KO</span>}
            </div>
            {service.responseTime !== undefined && (
              <p className="response-time">{service.responseTime}ms</p>
            )}
            <p className="endpoint">{service.endpoint}</p>
            <button onClick={() => checkSingleService(index)} className="check-button">
              Check
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HealthDashboard;
