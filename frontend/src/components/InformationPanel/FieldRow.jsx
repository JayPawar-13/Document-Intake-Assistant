import React from 'react';
import { Edit2, Check, Minus } from 'lucide-react';

export const FieldRow = ({ label, value, status, onEdit }) => {
  const isProvided = value !== null && value !== undefined && value !== '' && !(Array.isArray(value) && value.length === 0);

  const renderValue = () => {
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="text-slate-400 italic font-normal text-xs">Not provided</span>;
      }
      return (
        <span className="font-medium text-slate-800 text-xs sm:text-sm">
          {value.join(', ')}
        </span>
      );
    }
    if (!isProvided) {
      return <span className="text-slate-400 italic font-normal text-xs">Not provided</span>;
    }
    return <span className="font-semibold text-slate-800 text-xs sm:text-sm truncate block">{String(value)}</span>;
  };

  return (
    <div className="py-2.5 border-b border-slate-100 last:border-0 flex items-center justify-between gap-3 text-xs sm:text-sm">
      <div className="flex-1 min-w-0">
        <span className="text-[11px] font-medium text-slate-400 block mb-0.5">{label}</span>
        <div className="truncate">{renderValue()}</div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {/* Status Badge */}
        {isProvided ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            <Check className="w-3 h-3 text-emerald-600" />
            <span>Provided</span>
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-400 border border-slate-200">
            <Minus className="w-3 h-3" />
            <span>Pending</span>
          </span>
        )}

        {/* Edit Button */}
        {onEdit && (
          <button
            onClick={onEdit}
            className="p-1 rounded-md text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
            title={`Edit ${label}`}
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
};

export default FieldRow;
