import React from 'react';
import { Bot, User, AlertCircle, CheckCircle } from 'lucide-react';

export const MessageBubble = ({ message }) => {
  const isAssistant = message.role === 'assistant';
  const isClarification = message.metadata?.needs_clarification;
  const isCorrection = message.metadata?.is_correction;

  const formattedTime = message.created_at
    ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <div className={`flex gap-3 my-4 ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      {/* Assistant Avatar */}
      {isAssistant && (
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shrink-0 shadow-xs mt-1">
          <Bot className="w-4 h-4" />
        </div>
      )}

      {/* Bubble Content */}
      <div className={`max-w-[85%] sm:max-w-[75%] flex flex-col ${isAssistant ? 'items-start' : 'items-end'}`}>
        {/* Badges for special system states */}
        {isClarification && (
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 mb-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-[11px] font-semibold">
            <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
            <span>Clarification Needed</span>
          </div>
        )}

        {isCorrection && (
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 mb-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-semibold">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
            <span>Correction Noted</span>
          </div>
        )}

        <div
          className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
            isAssistant
              ? 'bg-white text-slate-800 border border-slate-200/90 shadow-card rounded-tl-sm'
              : 'bg-blue-600 text-white font-normal shadow-md shadow-blue-600/20 rounded-tr-sm'
          }`}
        >
          {message.content}
        </div>

        {/* Timestamp */}
        {formattedTime && (
          <span className="text-[10px] text-slate-400 mt-1 px-1">
            {formattedTime}
          </span>
        )}
      </div>

      {/* User Avatar */}
      {!isAssistant && (
        <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center text-slate-200 shrink-0 shadow-xs mt-1">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
