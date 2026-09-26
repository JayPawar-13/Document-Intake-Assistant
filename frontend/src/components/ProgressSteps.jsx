import React from 'react';
import { Check, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useIntake } from '../context/IntakeContext';

export const ProgressSteps = ({ activeStep = 1, onStepClick }) => {
  const navigate = useNavigate();
  const { navigateHome } = useIntake();

  const steps = [
    { number: 1, label: 'Personal Details', route: '/app' },
    { number: 2, label: 'Family', route: '/app' },
    { number: 3, label: 'Executor', route: '/app' },
    { number: 4, label: 'Gifts & Wishes', route: '/app' },
    { number: 5, label: 'Review', route: '/review' },
  ];

  const handleClick = (step) => {
    if (onStepClick) {
      onStepClick(step.number);
    }
    if (step.number === 5) {
      navigate('/review');
    }
  };

  return (
    <div className="w-full bg-white border-b border-slate-200/90 py-3 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        {/* Back to Home Button in Progress Header */}
        <button
          onClick={() => navigateHome(navigate)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-all cursor-pointer mr-4 shrink-0 shadow-2xs"
          title="Return to Home (Progress is saved)"
        >
          <Home className="w-3.5 h-3.5 text-blue-600" />
          <span className="hidden sm:inline">Back to Home</span>
        </button>

        <div className="flex-1 flex items-center justify-between">
        {steps.map((step, idx) => {
          const isCompleted = activeStep > step.number;
          const isCurrent = activeStep === step.number;

          return (
            <React.Fragment key={step.number}>
              {/* Step indicator */}
              <button
                onClick={() => handleClick(step)}
                className="flex items-center gap-2 group cursor-pointer focus:outline-none"
              >
                <div
                  className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-200 ${
                    isCompleted
                      ? 'bg-emerald-600 text-white shadow-xs'
                      : isCurrent
                      ? 'bg-blue-600 text-white ring-4 ring-blue-100 shadow-sm'
                      : 'bg-slate-100 text-slate-400 group-hover:bg-slate-200'
                  }`}
                >
                  {isCompleted ? <Check className="w-4 h-4 stroke-[2.5]" /> : step.number}
                </div>
                <span
                  className={`text-xs sm:text-sm font-semibold hidden md:inline transition-colors ${
                    isCurrent
                      ? 'text-blue-700'
                      : isCompleted
                      ? 'text-slate-800'
                      : 'text-slate-400'
                  }`}
                >
                  {step.label}
                </span>
              </button>

              {/* Connecting line */}
              {idx < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-2 sm:mx-4 transition-colors ${
                    activeStep > step.number ? 'bg-emerald-500' : 'bg-slate-200'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
        </div>
      </div>
    </div>
  );
};

export default ProgressSteps;
