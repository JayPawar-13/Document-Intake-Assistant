import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

export const ChatInput = ({ onSend, disabled = false, isThinking = false }) => {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!text.trim() || disabled || isThinking) return;
    onSend(text.trim());
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleInput = (e) => {
    setText(e.target.value);
    // Auto-expand textarea
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  useEffect(() => {
    if (!disabled && !isThinking && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled, isThinking]);

  return (
    <div className="p-4 bg-white border-t border-slate-200">
      {/* Typing indicator */}
      {isThinking && (
        <div className="flex items-center gap-2 mb-2 px-2 text-xs font-medium text-blue-600 animate-pulse">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span>Assistant is thinking...</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-end gap-2.5">
        <div className="flex-1 relative bg-slate-50 border border-slate-300 rounded-2xl focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={disabled || isThinking}
            placeholder="Type your message here... (Enter to send, Shift+Enter for new line)"
            className="w-full px-4 py-3 bg-transparent text-sm text-slate-800 placeholder-slate-400 focus:outline-none resize-none max-h-32 disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={!text.trim() || disabled || isThinking}
          className="h-11 px-5 rounded-2xl bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 text-white disabled:text-slate-400 flex items-center justify-center gap-2 font-medium text-sm shadow-md shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200 disabled:shadow-none cursor-pointer disabled:cursor-not-allowed shrink-0"
        >
          {isThinking ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <span>Send</span>
              <Send className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default ChatInput;
