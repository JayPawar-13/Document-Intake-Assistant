import React from 'react';
import { ArrowRight } from 'lucide-react';

export const QuickReplies = ({ replies = [], onSelect, disabled = false }) => {
  if (!replies || replies.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 my-3 px-2">
      <span className="text-xs font-semibold text-slate-400 mr-1">Suggested:</span>
      {replies.map((reply, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(reply)}
          disabled={disabled}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 shadow-2xs hover:shadow-xs transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 text-left"
        >
          <span>{reply}</span>
          <ArrowRight className="w-3 h-3 text-blue-500" />
        </button>
      ))}
    </div>
  );
};

export default QuickReplies;
