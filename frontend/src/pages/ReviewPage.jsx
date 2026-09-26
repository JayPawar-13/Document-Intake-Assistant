import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User,
  Users,
  Shield,
  Gift,
  Edit2,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  FileText,
  AlertCircle,
  Home
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import ProgressSteps from '../components/ProgressSteps';
import EditModal from '../components/EditModal';
import { useIntake } from '../context/IntakeContext';

export const ReviewPage = () => {
  const navigate = useNavigate();
  const { structuredState, fieldStatuses, navigateHome } = useIntake();
  const [editSection, setEditSection] = useState(null);

  const formatBool = (val) => {
    if (val === true) return 'Yes';
    if (val === false) return 'No';
    return <span className="text-slate-400 italic font-normal">Not provided</span>;
  };

  const formatList = (arr) => {
    if (!arr || arr.length === 0) {
      return <span className="text-slate-400 italic font-normal">Not provided</span>;
    }
    return arr.join(', ');
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 font-sans">
      <Sidebar />

      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        <ProgressSteps activeStep={5} />

        <div className="flex-1 overflow-y-auto p-6 sm:p-10">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Page Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
              <div>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-100/70 text-blue-700 text-xs font-bold uppercase tracking-wider mb-2">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Review Step</span>
                </div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  Your Information
                </h1>
                <p className="text-sm text-slate-500 mt-1">
                  Review the structured details extracted from your interview before document generation.
                </p>
              </div>

              <div className="flex items-center gap-2.5">
                <button
                  onClick={() => navigateHome(navigate)}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors cursor-pointer shadow-2xs"
                  title="Return to Home (Progress is saved)"
                >
                  <Home className="w-3.5 h-3.5 text-blue-600" />
                  <span>Back to Home</span>
                </button>
                <button
                  onClick={() => setEditSection('all')}
                  className="px-3.5 py-2.5 rounded-xl border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
                >
                  Edit All Fields
                </button>
                <button
                  onClick={() => navigate('/document')}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-md shadow-blue-500/25 transition-all cursor-pointer"
                >
                  <span>Continue to Document</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Information Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* 1. Personal Details Card */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-card transition-shadow">
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                      <User className="w-4 h-4" />
                    </div>
                    <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Personal Details</h2>
                  </div>
                  <button
                    onClick={() => setEditSection('personal')}
                    className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 cursor-pointer"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </button>
                </div>

                <div className="space-y-4 text-xs sm:text-sm">
                  <div>
                    <span className="text-slate-400 block text-[11px] font-medium mb-0.5">Full Legal Name</span>
                    <span className="font-semibold text-slate-800">
                      {structuredState.full_name || <span className="text-slate-400 italic font-normal">Not provided</span>}
                    </span>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[11px] font-medium mb-0.5">Home Address</span>
                    <span className="font-semibold text-slate-800">
                      {structuredState.home_address || <span className="text-slate-400 italic font-normal">Not provided</span>}
                    </span>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[11px] font-medium mb-0.5">Worldwide Assets Scope</span>
                    <span className="font-semibold text-slate-800">
                      {formatBool(structuredState.covers_worldwide_assets)}
                    </span>
                  </div>
                </div>
              </div>

              {/* 2. Family Card */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-card transition-shadow">
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                      <Users className="w-4 h-4" />
                    </div>
                    <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Family Details</h2>
                  </div>
                  <button
                    onClick={() => setEditSection('family')}
                    className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 cursor-pointer"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </button>
                </div>

                <div className="space-y-4 text-xs sm:text-sm">
                  <div>
                    <span className="text-slate-400 block text-[11px] font-medium mb-0.5">Has Children</span>
                    <span className="font-semibold text-slate-800">
                      {formatBool(structuredState.has_children)}
                    </span>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[11px] font-medium mb-0.5">Children's Names</span>
                    <span className="font-semibold text-slate-800">
                      {formatList(structuredState.children)}
                    </span>
                  </div>
                </div>
              </div>

              {/* 3. Executor Card */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-card transition-shadow">
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                      <Shield className="w-4 h-4" />
                    </div>
                    <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Appointment of Executor</h2>
                  </div>
                  <button
                    onClick={() => setEditSection('executor')}
                    className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 cursor-pointer"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </button>
                </div>

                <div className="space-y-4 text-xs sm:text-sm">
                  <div>
                    <span className="text-slate-400 block text-[11px] font-medium mb-0.5">Executor Full Name</span>
                    <span className="font-semibold text-slate-800">
                      {structuredState.executor.name || <span className="text-slate-400 italic font-normal">Not provided</span>}
                    </span>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[11px] font-medium mb-0.5">Relationship to You</span>
                    <span className="font-semibold text-slate-800 capitalize">
                      {structuredState.executor.relationship || <span className="text-slate-400 italic font-normal">Not provided</span>}
                    </span>
                  </div>
                </div>
              </div>

              {/* 4. Gifts & Wishes Card */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-card transition-shadow">
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
                      <Gift className="w-4 h-4" />
                    </div>
                    <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Specific Gifts & Wishes</h2>
                  </div>
                  <button
                    onClick={() => setEditSection('gifts')}
                    className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 cursor-pointer"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </button>
                </div>

                <div className="space-y-4 text-xs sm:text-sm">
                  <div>
                    <span className="text-slate-400 block text-[11px] font-medium mb-1">Specific Gifts</span>
                    {structuredState.specific_gifts && structuredState.specific_gifts.length > 0 ? (
                      <ul className="space-y-1">
                        {structuredState.specific_gifts.map((g, i) => (
                          <li key={i} className="font-semibold text-slate-800 flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                            <span>{g}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-slate-400 italic font-normal">No specific gifts recorded</span>
                    )}
                  </div>

                  <div className="pt-2">
                    <span className="text-slate-400 block text-[11px] font-medium mb-0.5">Additional Wishes</span>
                    <p className="font-medium text-slate-800 whitespace-pre-wrap">
                      {structuredState.additional_wishes || <span className="text-slate-400 italic font-normal">No additional wishes specified</span>}
                    </p>
                  </div>
                </div>
              </div>

            </div>

            {/* Bottom Actions */}
            <div className="flex items-center justify-between pt-6 border-t border-slate-200">
              <button
                onClick={() => navigate('/app')}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Return to Conversation</span>
              </button>

              <button
                onClick={() => navigate('/document')}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold shadow-md shadow-blue-500/25 transition-all cursor-pointer"
              >
                <span>Continue to Document Preview</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <EditModal
        isOpen={Boolean(editSection)}
        onClose={() => setEditSection(null)}
        initialSection={editSection || 'all'}
      />
    </div>
  );
};

export default ReviewPage;
