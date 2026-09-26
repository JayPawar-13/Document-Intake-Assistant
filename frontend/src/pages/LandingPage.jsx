import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  FileText,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Clock,
  Edit3,
  Bot
} from 'lucide-react';
import Navbar from '../components/Navbar';
import { useIntake } from '../context/IntakeContext';

export const LandingPage = () => {
  const navigate = useNavigate();
  const { createNewSession, loading, sessionId } = useIntake();

  const handleGetStarted = async () => {
    if (!sessionId) {
      await createNewSession();
    }
    navigate('/app');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 border-b border-slate-200/80 bg-gradient-to-b from-blue-50/50 via-white to-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            
            {/* Left Column: Headlines and CTAs */}
            <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-100/80 border border-blue-200 text-blue-700 text-xs font-bold tracking-wide uppercase">
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI-Assisted Legal Document Intake</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
                Create Your <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 bg-clip-text text-transparent">Personal Wishes Document</span> with Ease
              </h1>

              <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                A friendly AI assistant that guides you through a simple conversation to create a personalized, structured Personal Wishes Document. No complex forms—just natural, guided dialogue.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
                <button
                  onClick={handleGetStarted}
                  disabled={loading}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-base shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 transform hover:-translate-y-0.5 active:translate-y-0"
                >
                  <span>Get Started Now</span>
                  <ArrowRight className="w-5 h-5" />
                </button>

                <a
                  href="#how-it-works"
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white hover:bg-slate-100 text-slate-700 font-semibold text-base border border-slate-200 shadow-xs transition-colors"
                >
                  Learn More
                </a>
              </div>

              {/* Trust Badges */}
              <div className="pt-6 flex flex-wrap items-center justify-center lg:justify-start gap-6 text-xs font-semibold text-slate-500">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Validated Structured State</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Real-Time Document Preview</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Instant Corrections Support</span>
                </div>
              </div>
            </div>

            {/* Right Column: Hero Visual Card Mockup */}
            <div className="lg:col-span-5 relative">
              <div className="relative mx-auto max-w-md lg:max-w-none">
                {/* Glowing background gradient blur */}
                <div className="absolute -inset-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl blur-xl opacity-20 transform -rotate-1" />

                {/* Main Mockup Card */}
                <div className="relative bg-white rounded-2xl shadow-2xl border border-slate-200 p-6 overflow-hidden">
                  {/* Card Header */}
                  <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                        <Bot className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-900">Intake Assistant</div>
                        <div className="text-[10px] text-emerald-600 font-medium">● Online & Ready</div>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold">
                      DRAFT PREVIEW
                    </span>
                  </div>

                  {/* Chat Preview snippet */}
                  <div className="space-y-3 mb-5 text-xs">
                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 text-slate-700">
                      <span className="font-semibold text-blue-700 block mb-0.5">Assistant:</span>
                      "Hi! I'll help you create your Personal Wishes Document. What is your full legal name?"
                    </div>
                    <div className="bg-blue-600 p-3 rounded-xl text-white ml-8 shadow-sm">
                      <span className="font-semibold text-blue-100 block mb-0.5">You:</span>
                      "My name is Jane Smith."
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 text-slate-700">
                      <span className="font-semibold text-blue-700 block mb-0.5">Assistant:</span>
                      "Thanks, Jane. What is your current home address?"
                    </div>
                  </div>

                  {/* Live Extracted State Box */}
                  <div className="bg-blue-50/70 p-3.5 rounded-xl border border-blue-100">
                    <div className="flex items-center justify-between text-[11px] font-bold text-blue-900 mb-2">
                      <span>Live Extracted State:</span>
                      <span className="text-emerald-700 font-semibold">✓ Confirmed</span>
                    </div>
                    <div className="text-[11px] space-y-1 text-slate-700">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Full Name:</span>
                        <span className="font-semibold">Jane Smith</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Asset Coverage:</span>
                        <span className="font-semibold">Worldwide</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Feature Cards Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-2">Built for Precision & Simplicity</h2>
            <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">Everything You Need for a Seamless Intake</h3>
            <p className="mt-3 text-base text-slate-600">
              Designed around reliable structured state management, avoiding hallucination and giving you total control.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature 1 */}
            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200/80 hover:border-blue-300 hover:shadow-card transition-all duration-200 group">
              <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <MessageSquare className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">Conversational Guidance</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Step-by-step interview that intelligently extracts multiple fields from single answers and handles out-of-order responses.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200/80 hover:border-blue-300 hover:shadow-card transition-all duration-200 group">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <FileText className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">Live Document Preview</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Watch your formal Personal Wishes Document take shape in real time as your answers are validated and processed.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200/80 hover:border-blue-300 hover:shadow-card transition-all duration-200 group">
              <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <Edit3 className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">Easy Corrections</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Say "Actually, make that Sarah instead of James" or click Edit on any field to instantly update MongoDB and the document.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200/80 hover:border-blue-300 hover:shadow-card transition-all duration-200 group">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">Contradiction Guard</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Detects conflicting statements and ambiguities, asking clarification questions with quick-action buttons.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-slate-50 border-t border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-2">Simple 3-Step Process</h2>
            <h3 className="text-3xl font-extrabold text-slate-900">How It Works</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-xs relative">
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center mx-auto mb-4 text-sm">
                1
              </div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Answer Questions</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Chat naturally with the intake assistant about your details, family, executor, and wishes.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-xs relative">
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center mx-auto mb-4 text-sm">
                2
              </div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Review & Edit</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                View your structured information side-by-side and make inline corrections at any time.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-xs relative">
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center mx-auto mb-4 text-sm">
                3
              </div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Export Document</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Generate and download your clean, formal Personal Wishes Document as a PDF ready for signing.
              </p>
            </div>
          </div>

          <div className="mt-16 text-center">
            <button
              onClick={handleGetStarted}
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-base shadow-lg shadow-blue-500/25 transition-all cursor-pointer"
            >
              <span>Start Your Intake Interview</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="about" className="mt-auto bg-slate-900 text-slate-400 py-10 border-t border-slate-800 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded bg-blue-600 flex items-center justify-center text-white">
              <FileText className="w-3.5 h-3.5" />
            </div>
            <span className="font-semibold text-white">Document Intake Assistant</span>
            <span className="text-slate-500">| Technical Assessment Prototype</span>
          </div>
          <p className="text-slate-500">
            Fictional Document Generation &copy; {new Date().getFullYear()} — Not Legal Advice.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
