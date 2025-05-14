import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import TokenAnalysis from './pages/TokenAnalysis';
import RiskAssessment from './pages/RiskAssessment';

const { Header, Content, Footer } = Layout;

const App: React.FC = () => {
  return (
    <Router>
      <Layout className="app-layout">
        <Header>
          <Navbar />
        </Header>
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<TokenAnalysis />} />
            <Route path="/risk" element={<RiskAssessment />} />
          </Routes>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          LOOK.AI ©2025 Created by LOOK.AI Team
        </Footer>
      </Layout>
    </Router>
  );
};

export default App;