import React, { useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RotateCcw, Sparkles, Home } from 'lucide-react';
import MessageBubble from './MessageBubble';
import QuickReplies from './QuickReplies';
import ChatInput from './ChatInput';
import { useIntake } from '../../context/IntakeContext';

export const ChatInterface = () => {
  const navigate = useNavigate();
  const { messages, sendMessage, sendingMessage, clearChat, navigateHome } = useIntake();
  const scrollRef = useRef(null);

  // Auto-scroll to bottom whenever messages update
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, sendingMessage]);

  // Find quick replies from the latest assistant message
  const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;
  const activeQuickReplies =
    lastMessage && lastMessage.role === 'assistant' && lastMessage.quick_replies
      ? lastMessage.quick_replies
      : [];

  const handleSelectQuickReply = (reply) => {
    sendMessage(reply);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-50 border-r border-slate-200 overflow-hidden">
      {/* Conversation Header */}
      <div className="h-14 px-6 bg-white border-b border-slate-200/90 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <h2 className="text-sm font-bold text-slate-900 tracking-wide">Conversation</h2>
          <span className="text-xs text-slate-400 font-normal">| Live Guidance</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => navigateHome(navigate)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-all cursor-pointer shadow-2xs"
            title="Return to Home (Progress is saved)"
          >
            <Home className="w-3.5 h-3.5 text-blue-600" />
            <span>Back to Home</span>
          </button>

          <button
            onClick={clearChat}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer"
            title="Clear Conversation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Clear Chat</span>
          </button>
        </div>
      </div>

      {/* Message List */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-2">
        {messages.map((msg, idx) => (
          <MessageBubble key={msg.id || idx} message={msg} />
        ))}
      </div>

      {/* Quick Action Suggestion Buttons */}
      <QuickReplies
        replies={activeQuickReplies}
        onSelect={handleSelectQuickReply}
        disabled={sendingMessage}
      />

      {/* Bottom Input */}
      <ChatInput
        onSend={sendMessage}
        disabled={sendingMessage}
        isThinking={sendingMessage}
      />
    </div>
  );
};

export default ChatInterface;
