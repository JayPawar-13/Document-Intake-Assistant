import React from 'react';
import { Edit3 } from 'lucide-react';

export const InformationCard = ({ title, icon: Icon, children, onEditSection }) => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card p-4 sm:p-5 mb-4 hover:border-slate-300 transition-colors">
      <div className="flex items-center justify-between pb-3 mb-2 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          {Icon && (
            <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <Icon className="w-4 h-4" />
            </div>
          )}
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">{title}</h3>
        </div>

        {onEditSection && (
          <button
            onClick={onEditSection}
            className="flex items-center gap-1 text-[11px] font-semibold text-blue-600 hover:text-blue-700 hover:underline cursor-pointer"
          >
            <Edit3 className="w-3 h-3" />
            <span>Edit</span>
          </button>
        )}
      </div>

      <div className="space-y-1">
        {children}
      </div>
    </div>
  );
};

export default InformationCard;
