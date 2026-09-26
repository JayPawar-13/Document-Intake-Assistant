import React, { useState, useEffect } from 'react';
import { X, Check, Save, AlertCircle } from 'lucide-react';
import { useIntake } from '../context/IntakeContext';

export const EditModal = ({ isOpen, onClose, initialSection = 'all' }) => {
  const { structuredState, updateStateField, loading } = useIntake();

  const [formData, setFormData] = useState({
    full_name: '',
    home_address: '',
    covers_worldwide_assets: null,
    has_children: null,
    children_text: '',
    executor_name: '',
    executor_relationship: '',
    specific_gifts_text: '',
    additional_wishes: '',
  });

  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Pre-fill form from current structured state
  useEffect(() => {
    if (structuredState) {
      setFormData({
        full_name: structuredState.full_name || '',
        home_address: structuredState.home_address || '',
        covers_worldwide_assets: structuredState.covers_worldwide_assets,
        has_children: structuredState.has_children,
        children_text: (structuredState.children || []).join(', '),
        executor_name: structuredState.executor?.name || '',
        executor_relationship: structuredState.executor?.relationship || '',
        specific_gifts_text: (structuredState.specific_gifts || []).join('\n'),
        additional_wishes: structuredState.additional_wishes || '',
      });
    }
  }, [structuredState, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');

    try {
      const updates = {};

      if (initialSection === 'all' || initialSection === 'personal') {
        if (formData.full_name.trim()) updates.full_name = formData.full_name.trim();
        if (formData.home_address.trim()) updates.home_address = formData.home_address.trim();
        if (formData.covers_worldwide_assets !== null) {
          updates.covers_worldwide_assets = formData.covers_worldwide_assets;
        }
      }

      if (initialSection === 'all' || initialSection === 'family') {
        if (formData.has_children !== null) {
          updates.has_children = formData.has_children;
        }
        if (formData.children_text.trim()) {
          const names = formData.children_text
            .split(',')
            .map((n) => n.trim())
            .filter(Boolean);
          updates.children = names;
          updates.has_children = true;
        } else if (formData.has_children === false) {
          updates.children = [];
        }
      }

      if (initialSection === 'all' || initialSection === 'executor') {
        const exec = {};
        if (formData.executor_name.trim()) exec.name = formData.executor_name.trim();
        if (formData.executor_relationship.trim()) exec.relationship = formData.executor_relationship.trim();
        if (Object.keys(exec).length > 0) updates.executor = exec;
      }

      if (initialSection === 'all' || initialSection === 'gifts') {
        if (formData.specific_gifts_text.trim()) {
          const gifts = formData.specific_gifts_text
            .split('\n')
            .map((g) => g.trim())
            .filter(Boolean);
          updates.specific_gifts = gifts;
        }
        if (formData.additional_wishes.trim()) {
          updates.additional_wishes = formData.additional_wishes.trim();
        }
      }

      await updateStateField(updates);
      onClose();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail?.errors?.join(', ') || 'Failed to update information.');
    } finally {
      setSaving(false);
    }
  };

  const showPersonal = initialSection === 'all' || initialSection === 'personal';
  const showFamily = initialSection === 'all' || initialSection === 'family';
  const showExecutor = initialSection === 'all' || initialSection === 'executor';
  const showGifts = initialSection === 'all' || initialSection === 'gifts';

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 shadow-2xl border border-slate-200 my-8">
        <div className="flex items-center justify-between pb-4 mb-5 border-b border-slate-100">
          <div>
            <h3 className="text-lg font-bold text-slate-900">
              {initialSection === 'all' ? 'Edit Your Information' : `Edit ${initialSection.toUpperCase()}`}
            </h3>
            <p className="text-xs text-slate-500">Update backend state and re-sync document</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5 max-h-[65vh] overflow-y-auto pr-1">
          {/* Personal Details */}
          {showPersonal && (
            <div className="space-y-3 pb-4 border-b border-slate-100">
              <h4 className="text-xs font-bold uppercase tracking-wider text-blue-700">1. Personal Details</h4>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  placeholder="e.g. Jane Smith"
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Home Address</label>
                <input
                  type="text"
                  value={formData.home_address}
                  onChange={(e) => setFormData({ ...formData, home_address: e.target.value })}
                  placeholder="e.g. 21 High Street, London"
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Cover Worldwide Assets?</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input
                      type="radio"
                      name="worldwide"
                      checked={formData.covers_worldwide_assets === true}
                      onChange={() => setFormData({ ...formData, covers_worldwide_assets: true })}
                      className="text-blue-600 focus:ring-blue-500"
                    />
                    <span>Yes (Worldwide)</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input
                      type="radio"
                      name="worldwide"
                      checked={formData.covers_worldwide_assets === false}
                      onChange={() => setFormData({ ...formData, covers_worldwide_assets: false })}
                      className="text-blue-600 focus:ring-blue-500"
                    />
                    <span>No (Domestic only)</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Family */}
          {showFamily && (
            <div className="space-y-3 pb-4 border-b border-slate-100">
              <h4 className="text-xs font-bold uppercase tracking-wider text-blue-700">2. Family</h4>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Do you have children?</label>
                <div className="flex gap-4 mb-2">
                  <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input
                      type="radio"
                      name="has_children"
                      checked={formData.has_children === true}
                      onChange={() => setFormData({ ...formData, has_children: true })}
                      className="text-blue-600 focus:ring-blue-500"
                    />
                    <span>Yes</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input
                      type="radio"
                      name="has_children"
                      checked={formData.has_children === false}
                      onChange={() => setFormData({ ...formData, has_children: false, children_text: '' })}
                      className="text-blue-600 focus:ring-blue-500"
                    />
                    <span>No</span>
                  </label>
                </div>
              </div>

              {formData.has_children !== false && (
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Children's Names (comma separated)</label>
                  <input
                    type="text"
                    value={formData.children_text}
                    onChange={(e) => setFormData({ ...formData, children_text: e.target.value, has_children: true })}
                    placeholder="e.g. Sarah, Michael"
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition"
                  />
                </div>
              )}
            </div>
          )}

          {/* Executor */}
          {showExecutor && (
            <div className="space-y-3 pb-4 border-b border-slate-100">
              <h4 className="text-xs font-bold uppercase tracking-wider text-blue-700">3. Executor</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Executor Full Name</label>
                  <input
                    type="text"
                    value={formData.executor_name}
                    onChange={(e) => setFormData({ ...formData, executor_name: e.target.value })}
                    placeholder="e.g. James Smith"
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Relationship</label>
                  <input
                    type="text"
                    value={formData.executor_relationship}
                    onChange={(e) => setFormData({ ...formData, executor_relationship: e.target.value })}
                    placeholder="e.g. Brother, Sister, Solicitor"
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Gifts & Wishes */}
          {showGifts && (
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-blue-700">4. Gifts & Wishes</h4>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Specific Gifts (one per line)</label>
                <textarea
                  rows={2}
                  value={formData.specific_gifts_text}
                  onChange={(e) => setFormData({ ...formData, specific_gifts_text: e.target.value })}
                  placeholder="e.g. My watch to Michael"
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition resize-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Additional Wishes</label>
                <textarea
                  rows={2}
                  value={formData.additional_wishes}
                  onChange={(e) => setFormData({ ...formData, additional_wishes: e.target.value })}
                  placeholder="e.g. My photographs to Sarah"
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition resize-none"
                />
              </div>
            </div>
          )}

          <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 text-sm font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-semibold shadow-md shadow-blue-500/25 flex items-center gap-2 transition-all cursor-pointer"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving...' : 'Save & Update Document'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditModal;
