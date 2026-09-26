import React from 'react';
import Sidebar from '../components/Sidebar';
import ProgressSteps from '../components/ProgressSteps';
import ChatInterface from '../components/Chat/ChatInterface';
import InformationPanel from '../components/InformationPanel/InformationPanel';
import { useIntake } from '../context/IntakeContext';

export const ApplicationPage = () => {
  const { activeStep } = useIntake();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 font-sans">
      {/* Left Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        {/* Top Progress Steps Header */}
        <ProgressSteps activeStep={activeStep} />

        {/* Split Conversational & State Panel */}
        <div className="flex-1 flex flex-col lg:flex-row h-[calc(100vh-65px)] overflow-hidden">
          {/* Main / Left: Chat Conversation */}
          <ChatInterface />

          {/* Right: Live Structured Information & Document Preview */}
          <InformationPanel />
        </div>
      </div>
    </div>
  );
};

export default ApplicationPage;
