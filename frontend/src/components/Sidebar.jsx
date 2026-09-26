import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  ClipboardList,
  FileText,
  PlusCircle,
  Settings,
  HelpCircle,
  LogOut,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useIntake } from '../context/IntakeContext';

export const Sidebar = () => {
  const navigate = useNavigate();
  const { createNewSession, clearChat, sessionId, structuredState, loading } = useIntake();
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);

  const handleNewDocument = async () => {
    if (window.confirm('Start a new intake session? Your current progress is saved in MongoDB.')) {
      const newId = await createNewSession();
      navigate('/app');
    }
  };

  const handleClearChat = async () => {
    if (window.confirm('Reset conversation history for this session? Your structured data remains.')) {
      await clearChat();
    }
  };

  const navItems = [
    {
      to: '/app',
      label: 'Conversation',
      icon: MessageSquare,
      description: 'AI Interview',
    },
    {
      to: '/review',
      label: 'Your Information',
      icon: ClipboardList,
      description: 'Review & Edit State',
    },
    {
      to: '/document',
      label: 'Document Preview',
      icon: FileText,
      description: 'Formal Wishes Draft',
    },
  ];

  return (
    <>
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 select-none shrink-0 h-full">
        {/* Top Header / App Brand */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">Document Intake</h2>
              <p className="text-[11px] text-blue-400 font-medium">Assistant AI</p>
            </div>
          </div>
        </div>

        {/* New Document CTA Button */}
        <div className="p-4">
          <button
            onClick={handleNewDocument}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-semibold shadow-md shadow-blue-600/30 transition-all duration-200 active:scale-[0.98]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Document</span>
          </button>
        </div>

        {/* Primary Navigation Links */}
        <nav className="flex-1 px-3 py-2 space-y-1.5 overflow-y-auto">
          <div className="px-3 pb-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Intake Workspace
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white font-semibold shadow-xs shadow-blue-500/20'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <div className="flex flex-col text-left">
                  <span>{item.label}</span>
                  <span className="text-[10px] text-slate-400">{item.description}</span>
                </div>
              </NavLink>
            );
          })}

          <div className="pt-4 px-3 pb-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Actions & Tools
          </div>

          <button
            onClick={handleClearChat}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <RotateCcw className="w-4 h-4 text-slate-400" />
            <span>Reset Conversation</span>
          </button>

          <button
            onClick={() => setShowSettingsModal(true)}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <Settings className="w-4 h-4 text-slate-400" />
            <span>Settings</span>
          </button>

          <button
            onClick={() => setShowHelpModal(true)}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <HelpCircle className="w-4 h-4 text-slate-400" />
            <span>Help & Guidelines</span>
          </button>
        </nav>

        {/* Active Session Card at Bottom */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold text-slate-300">Active Session</span>
            <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-blue-300">
              {sessionId ? `#${sessionId}` : 'None'}
            </span>
          </div>
          <p className="text-xs text-slate-400 truncate">
            {structuredState.full_name ? `Client: ${structuredState.full_name}` : 'Awaiting name...'}
          </p>
          <div className="mt-2 text-[10px] text-emerald-400 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>MongoDB Synced</span>
          </div>
        </div>
      </aside>

      {/* Help Modal */}
      {showHelpModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center">
                <HelpCircle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">How to Use the Assistant</h3>
                <p className="text-xs text-slate-500">Conversational intake guidance</p>
              </div>
            </div>
            <div className="space-y-3 text-sm text-slate-600">
              <p>• <strong>Talk Naturally:</strong> You can answer questions one-by-one or share multiple details in one sentence.</p>
              <p>• <strong>Make Corrections:</strong> Say "Actually, Sarah is my executor instead of James" or use the Edit buttons directly.</p>
              <p>• <strong>Clarifications:</strong> If an answer is ambiguous, click the quick action buttons that appear under the chat.</p>
              <p>• <strong>Live Previews:</strong> Watch your structured data update live on the right and view the draft document anytime.</p>
            </div>
            <button
              onClick={() => setShowHelpModal(false)}
              className="mt-6 w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium text-sm transition-colors"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center">
                <Settings className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">Application Settings</h3>
                <p className="text-xs text-slate-500">Local environment configuration</p>
              </div>
            </div>
            <div className="space-y-3 text-xs text-slate-600 bg-slate-50 p-4 rounded-xl border border-slate-200 font-mono">
              <p>Database: MongoDB (localhost:27017)</p>
              <p>DB Name: document_intake_assistant</p>
              <p>LLM Service: Mock / OpenAI compatible</p>
              <p>API Endpoint: http://localhost:8000</p>
            </div>
            <button
              onClick={() => setShowSettingsModal(false)}
              className="mt-6 w-full py-2.5 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-medium text-sm transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Sidebar;
