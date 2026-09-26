import React, { useState } from 'react';
import { User, Users, Shield, Gift, FileText, CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import FieldRow from './FieldRow';
import InformationCard from './InformationCard';
import DocumentViewer from '../DocumentPreview/DocumentViewer';
import EditModal from '../EditModal';
import { useIntake } from '../../context/IntakeContext';

export const InformationPanel = () => {
  const { structuredState, fieldStatuses } = useIntake();
  const [activeTab, setActiveTab] = useState('info'); // 'info' | 'preview'
  const [editModalSection, setEditModalSection] = useState(null); // 'all' | 'personal' | 'family' | 'executor' | 'gifts' | null

  const calculateCompletion = () => {
    let completed = 0;
    const total = 7;
    if (structuredState.full_name) completed++;
    if (structuredState.home_address) completed++;
    if (structuredState.covers_worldwide_assets !== null) completed++;
    if (structuredState.has_children !== null && (!structuredState.has_children || structuredState.children.length > 0)) completed++;
    if (structuredState.executor.name && structuredState.executor.relationship) completed++;
    if (structuredState.specific_gifts.length > 0) completed++;
    if (structuredState.additional_wishes) completed++;
    return Math.round((completed / total) * 100);
  };

  const completionPct = calculateCompletion();

  return (
    <div className="w-full lg:w-[460px] xl:w-[500px] flex flex-col h-full bg-slate-100/70 border-l border-slate-200 overflow-hidden shrink-0">
      {/* Panel Top Header & Tab Toggle */}
      <div className="p-4 bg-white border-b border-slate-200 shrink-0">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Your Information</h3>
            <p className="text-[11px] text-slate-500">Live extracted structured state</p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-blue-700">{completionPct}%</span>
            <div className="w-16 h-2 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-300 rounded-full"
                style={{ width: `${completionPct}%` }}
              />
            </div>
          </div>
        </div>

        {/* Tab Buttons */}
        <div className="flex p-1 bg-slate-100 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setActiveTab('info')}
            className={`flex-1 py-1.5 rounded-lg transition-all ${
              activeTab === 'info'
                ? 'bg-white text-blue-700 shadow-2xs font-bold'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Structured State
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex-1 py-1.5 rounded-lg transition-all ${
              activeTab === 'preview'
                ? 'bg-white text-blue-700 shadow-2xs font-bold'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Live Document
          </button>
        </div>
      </div>

      {/* Panel Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === 'info' ? (
          <>
            {/* 1. Personal Details */}
            <InformationCard
              title="Personal Details"
              icon={User}
              onEditSection={() => setEditModalSection('personal')}
            >
              <FieldRow
                label="Full Name"
                value={structuredState.full_name}
                status={fieldStatuses.full_name}
                onEdit={() => setEditModalSection('personal')}
              />
              <FieldRow
                label="Home Address"
                value={structuredState.home_address}
                status={fieldStatuses.home_address}
                onEdit={() => setEditModalSection('personal')}
              />
              <FieldRow
                label="Worldwide Assets"
                value={structuredState.covers_worldwide_assets}
                status={fieldStatuses.covers_worldwide_assets}
                onEdit={() => setEditModalSection('personal')}
              />
            </InformationCard>

            {/* 2. Family */}
            <InformationCard
              title="Family"
              icon={Users}
              onEditSection={() => setEditModalSection('family')}
            >
              <FieldRow
                label="Has Children"
                value={structuredState.has_children}
                status={fieldStatuses.has_children}
                onEdit={() => setEditModalSection('family')}
              />
              <FieldRow
                label="Children's Names"
                value={structuredState.children}
                status={fieldStatuses.children}
                onEdit={() => setEditModalSection('family')}
              />
            </InformationCard>

            {/* 3. Executor */}
            <InformationCard
              title="Executor"
              icon={Shield}
              onEditSection={() => setEditModalSection('executor')}
            >
              <FieldRow
                label="Executor Name"
                value={structuredState.executor.name}
                status={fieldStatuses.executor_name}
                onEdit={() => setEditModalSection('executor')}
              />
              <FieldRow
                label="Relationship"
                value={structuredState.executor.relationship}
                status={fieldStatuses.executor_relationship}
                onEdit={() => setEditModalSection('executor')}
              />
            </InformationCard>

            {/* 4. Gifts & Wishes */}
            <InformationCard
              title="Gifts & Wishes"
              icon={Gift}
              onEditSection={() => setEditModalSection('gifts')}
            >
              <FieldRow
                label="Specific Gifts"
                value={structuredState.specific_gifts}
                status={fieldStatuses.specific_gifts}
                onEdit={() => setEditModalSection('gifts')}
              />
              <FieldRow
                label="Additional Wishes"
                value={structuredState.additional_wishes}
                status={fieldStatuses.additional_wishes}
                onEdit={() => setEditModalSection('gifts')}
              />
            </InformationCard>

            {/* Bottom Review CTA */}
            <div className="pt-2 pb-4">
              <Link
                to="/review"
                className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-md shadow-blue-500/20 hover:shadow-lg transition-all"
              >
                <span>Review & Full Edit Page</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </>
        ) : (
          <DocumentViewer isEmbedded={true} />
        )}
      </div>

      {/* Edit Modal */}
      <EditModal
        isOpen={Boolean(editModalSection)}
        onClose={() => setEditModalSection(null)}
        initialSection={editModalSection || 'all'}
      />
    </div>
  );
};

export default InformationPanel;
