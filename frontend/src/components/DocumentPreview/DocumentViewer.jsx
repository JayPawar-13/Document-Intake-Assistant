import React, { useState } from 'react';
import { Printer, RefreshCw, Copy, Check, FileDown, ArrowLeft } from 'lucide-react';
import { useIntake } from '../../context/IntakeContext';
import { useNavigate } from 'react-router-dom';

export const DocumentViewer = ({ isEmbedded = false }) => {
  const { documentData, regenerateDocument, loading, structuredState } = useIntake();
  const [copied, setCopied] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const navigate = useNavigate();

  const handlePrint = () => {
    window.print();
  };

  const handleCopyText = async () => {
    if (documentData.document_text) {
      await navigator.clipboard.writeText(documentData.document_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    await regenerateDocument();
    setRegenerating(false);
  };

  return (
    <div className={`flex flex-col h-full ${isEmbedded ? '' : 'max-w-5xl mx-auto px-4 py-8'}`}>
      {/* Top Action Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6 no-print bg-white p-4 rounded-2xl border border-slate-200/90 shadow-xs">
        <div className="flex items-center gap-3">
          {!isEmbedded && (
            <button
              onClick={() => navigate('/app')}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Chat</span>
            </button>
          )}
          <div>
            <h2 className="text-base font-bold text-slate-900">Personal Wishes Document</h2>
            <p className="text-xs text-slate-500">Live draft generated from validated state</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Copy Plain Text */}
          <button
            onClick={handleCopyText}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium transition-colors cursor-pointer"
            title="Copy plain text"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied!' : 'Copy Text'}</span>
          </button>

          {/* Regenerate Button */}
          <button
            onClick={handleRegenerate}
            disabled={regenerating || loading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium transition-colors cursor-pointer disabled:opacity-50"
            title="Re-run document generator"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${regenerating ? 'animate-spin text-blue-600' : ''}`} />
            <span>{regenerating ? 'Regenerating...' : 'Regenerate'}</span>
          </button>

          {/* Download PDF / Print */}
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-md shadow-blue-500/20 hover:shadow-lg transition-all cursor-pointer"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      {/* Render Document HTML */}
      <div className="flex-1 overflow-y-auto pb-8">
        {documentData.document_html ? (
          <div
            className="prose prose-slate max-w-none"
            dangerouslySetInnerHTML={{ __html: documentData.document_html }}
          />
        ) : (
          <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center max-w-lg mx-auto">
            <p className="text-slate-500 text-sm">Preparing document draft from your responses...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;
