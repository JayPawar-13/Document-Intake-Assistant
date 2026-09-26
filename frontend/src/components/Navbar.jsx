import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FileText, ArrowRight, Home, Sparkles } from 'lucide-react';
import { useIntake } from '../context/IntakeContext';

export const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { createNewSession, backendStatus, sessionId, navigateHome } = useIntake();

  const handleStartIntake = async () => {
    if (!sessionId) {
      await createNewSession();
    }
    navigate('/app');
  };

  const handleLogoClick = (e) => {
    e.preventDefault();
    if (location.pathname === '/') return;
    navigateHome(navigate);
  };

  const isApp = location.pathname.startsWith('/app') || location.pathname.startsWith('/review') || location.pathname.startsWith('/document');

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200/80 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo and Name */}
        <button
          onClick={handleLogoClick}
          className="flex items-center gap-3 group text-left cursor-pointer focus:outline-none"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform duration-200">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 tracking-tight text-lg">Document Intake</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                AI Assistant
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium hidden sm:block">Personal Wishes & Estate Guidance</p>
          </div>
        </button>

        {/* Center Nav Links (visible on landing) */}
        {!isApp && (
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <button
              onClick={() => navigateHome(navigate)}
              className="text-blue-600 font-semibold hover:text-blue-700 transition-colors cursor-pointer"
            >
              Home
            </button>
            <a href="#how-it-works" className="hover:text-slate-900 transition-colors">How It Works</a>
            <a href="#features" className="hover:text-slate-900 transition-colors">Features</a>
            <a href="#about" className="hover:text-slate-900 transition-colors">About</a>
          </nav>
        )}

        {/* Right CTA and status */}
        <div className="flex items-center gap-3">
          {/* Back to Home Button (shown when in active intake pages or always visible) */}
          {isApp && (
            <button
              onClick={() => navigateHome(navigate)}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-xs sm:text-sm font-semibold transition-all cursor-pointer shadow-xs"
              title="Return to Home"
            >
              <Home className="w-4 h-4 text-blue-600" />
              <span>Back to Home</span>
            </button>
          )}

          {/* Server Connection Pill */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 border border-slate-200 text-slate-600" title={`Backend & MongoDB status: ${backendStatus}`}>
            <span className={`w-2 h-2 rounded-full ${backendStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : backendStatus === 'checking' ? 'bg-amber-400' : 'bg-rose-500'}`} />
            <span className="capitalize">{backendStatus === 'connected' ? 'MongoDB Online' : backendStatus}</span>
          </div>

          {!isApp ? (
            <button
              onClick={handleStartIntake}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold shadow-md shadow-blue-500/25 hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-200 cursor-pointer"
            >
              <span>{sessionId ? 'Resume Intake' : 'Get Started'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={() => navigate('/document')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium transition-colors cursor-pointer"
            >
              <FileText className="w-4 h-4 text-blue-600" />
              <span>Preview Document</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
