import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { IntakeProvider } from './context/IntakeContext';
import LandingPage from './pages/LandingPage';
import ApplicationPage from './pages/ApplicationPage';
import ReviewPage from './pages/ReviewPage';
import DocumentPage from './pages/DocumentPage';

function App() {
  return (
    <Router>
      <IntakeProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app" element={<ApplicationPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/document" element={<DocumentPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </IntakeProvider>
    </Router>
  );
}

export default App;
