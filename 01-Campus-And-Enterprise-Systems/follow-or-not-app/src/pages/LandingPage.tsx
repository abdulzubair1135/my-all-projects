import React from 'react';
import { useApp } from '../context/AppContext';
import { SampleDataService } from '../services/SampleDataService';
import { storageService } from '../services/StorageService';
import {
  ShieldCheck,
  Lock,
  UploadCloud,
  TrendingUp,
  UserX,
  UserMinus,
  Sparkles,
  ArrowRight,
  CheckCircle,
  Cpu,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { setCurrentPage, refreshData, addToast } = useApp();

  const handleLoadDemoData = async () => {
    try {
      const { snapshot1, snapshot2 } = SampleDataService.getSampleSnapshots();
      await storageService.saveSnapshot(snapshot1);
      await storageService.saveSnapshot(snapshot2);
      await refreshData();
      addToast({
        type: 'success',
        title: 'Demo Snapshots Loaded',
        message: 'Loaded 2 historical snapshots to showcase follower tracking!',
      });
      setCurrentPage('dashboard');
    } catch {
      addToast({
        type: 'error',
        title: 'Demo Load Failed',
        message: 'Could not write sample data to IndexedDB.',
      });
    }
  };

  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="relative pt-6 md:pt-12 text-center max-w-4xl mx-auto px-4">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-[#8B5CF6]/10 border border-[#8B5CF6]/30 text-[#8B5CF6] text-xs font-semibold mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          <span>100% Privacy-First Instagram Intelligence</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold text-[#F8FAFC] tracking-tight leading-tight">
          Know Who Follows You. <br />
          <span className="bg-gradient-to-r from-[#8B5CF6] via-[#A78BFA] to-[#6366F1] bg-clip-text text-transparent">
            Track Every Change.
          </span>
        </h1>

        <p className="mt-5 text-base md:text-lg text-[#94A3B8] max-w-2xl mx-auto leading-relaxed">
          The professional Instagram follower analytics dashboard powered completely in your browser.
          Identify unfollowers, mutuals, and ghost accounts without sharing passwords or tokens.
        </p>

        {/* Call to Actions */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={() => setCurrentPage('import')}
            className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-gradient-to-r from-[#8B5CF6] to-[#6366F1] hover:from-[#7C3AED] hover:to-[#4F46E5] text-white font-semibold text-sm shadow-xl shadow-[#8B5CF6]/25 transition-all flex items-center justify-center space-x-2 group active:scale-95"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Import Your Instagram Export</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>

          <button
            onClick={handleLoadDemoData}
            className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-[#151B27] hover:bg-[#1C2433] text-[#F8FAFC] border border-[#252B38] font-medium text-sm transition-all flex items-center justify-center space-x-2 active:scale-95"
          >
            <Sparkles className="w-4 h-4 text-[#8B5CF6]" />
            <span>Try With Realistic Demo Data</span>
          </button>
        </div>

        {/* Security badges */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-xs text-[#94A3B8]">
          <span className="flex items-center space-x-1.5">
            <Lock className="w-4 h-4 text-[#22C55E]" />
            <span>Zero Password Access</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <Cpu className="w-4 h-4 text-[#8B5CF6]" />
            <span>Client-Side In-Memory Engine</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <ShieldCheck className="w-4 h-4 text-[#6366F1]" />
            <span>Official Instagram Data Compatible</span>
          </span>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto px-4">
        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 transition-all hover:border-[#8B5CF6]/40">
          <div className="w-10 h-10 rounded-xl bg-[#EF4444]/10 text-[#EF4444] flex items-center justify-center mb-4">
            <UserMinus className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-[#F8FAFC]">True Unfollower Detection</h3>
          <p className="mt-2 text-xs text-[#94A3B8] leading-relaxed">
            By comparing snapshots over time, pinpoint exactly which accounts unfollowed your profile.
            Never rely on deceptive third-party bots that steal your password.
          </p>
        </div>

        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 transition-all hover:border-[#8B5CF6]/40">
          <div className="w-10 h-10 rounded-xl bg-[#F59E0B]/10 text-[#F59E0B] flex items-center justify-center mb-4">
            <UserX className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-[#F8FAFC]">Not Following Back</h3>
          <p className="mt-2 text-xs text-[#94A3B8] leading-relaxed">
            Quickly identify high-maintenance accounts you follow that don’t return the courtesy.
            Review them and curate your feed cleanly.
          </p>
        </div>

        <div className="bg-[#151B27] border border-[#252B38] rounded-2xl p-6 transition-all hover:border-[#8B5CF6]/40">
          <div className="w-10 h-10 rounded-xl bg-[#8B5CF6]/10 text-[#8B5CF6] flex items-center justify-center mb-4">
            <TrendingUp className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-[#F8FAFC]">Historical Snapshots</h3>
          <p className="mt-2 text-xs text-[#94A3B8] leading-relaxed">
            Keep an audit trail of your account’s evolution across weeks and months.
            Compare any two snapshots side-by-side with net growth indicators.
          </p>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="bg-[#10141D] border border-[#252B38] rounded-3xl p-8 md:p-12 max-w-5xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <span className="text-xs font-bold text-[#8B5CF6] uppercase tracking-wider">
            Safe & Simple Process
          </span>
          <h2 className="text-2xl md:text-3xl font-extrabold text-[#F8FAFC] mt-2">
            How FollowTrack Works Without Passwords
          </h2>
          <p className="text-xs md:text-sm text-[#94A3B8] mt-2">
            Instagram provides an official data export tool under Meta Accounts Center.
            FollowTrack processes your export file completely in your web browser.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-[#8B5CF6]/15 text-[#8B5CF6] flex items-center justify-center font-bold text-lg">
              1
            </div>
            <h4 className="font-bold text-[#F8FAFC] text-sm">Request Official Export</h4>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              In Instagram Settings &rarr; Your Activity &rarr; Download your information.
              Select JSON format and 'Followers and following'.
            </p>
          </div>

          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-[#6366F1]/15 text-[#6366F1] flex items-center justify-center font-bold text-lg">
              2
            </div>
            <h4 className="font-bold text-[#F8FAFC] text-sm">Drop ZIP or JSON Files</h4>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Drag your downloaded archive into FollowTrack. JSZip extracts and normalizes
              the records in browser memory without sending a single byte to any server.
            </p>
          </div>

          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-[#22C55E]/15 text-[#22C55E] flex items-center justify-center font-bold text-lg">
              3
            </div>
            <h4 className="font-bold text-[#F8FAFC] text-sm">Instant Analytics</h4>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              View your not-following-back list, mutuals, fans, and unfollowers.
              Export reports and safely manage your follows manually.
            </p>
          </div>
        </div>

        <div className="mt-10 pt-8 border-t border-[#252B38] flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-xs text-[#94A3B8]">
            <CheckCircle className="w-4 h-4 text-[#22C55E]" />
            <span>Supports both Public and Private Instagram Accounts</span>
          </div>

          <button
            onClick={() => setCurrentPage('import')}
            className="text-xs font-semibold text-[#8B5CF6] hover:text-[#A78BFA] transition-colors flex items-center space-x-1"
          >
            <span>Go to Import Data</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>
    </div>
  );
};
