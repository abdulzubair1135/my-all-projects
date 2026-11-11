import React, { useState } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Sidebar } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { ToastContainer } from './components/common/ToastContainer';

// Pages
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ImportPage } from './pages/ImportPage';
import { FollowersPage } from './pages/FollowersPage';
import { FollowingPage } from './pages/FollowingPage';
import { UnfollowersPage } from './pages/UnfollowersPage';
import { NotFollowingBackPage } from './pages/NotFollowingBackPage';
import { FansPage } from './pages/FansPage';
import { MutualsPage } from './pages/MutualsPage';
import { HistoryPage } from './pages/HistoryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SmartUnfollowManagerPage } from './pages/SmartUnfollowManagerPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { PrivacyPage } from './pages/PrivacyPage';

const AppContent: React.FC = () => {
  const { currentPage, isLoading } = useApp();
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage />;
      case 'dashboard':
        return <DashboardPage />;
      case 'import':
        return <ImportPage />;
      case 'followers':
        return <FollowersPage />;
      case 'following':
        return <FollowingPage />;
      case 'unfollowers':
        return <UnfollowersPage />;
      case 'not-following-back':
        return <NotFollowingBackPage />;
      case 'fans':
        return <FansPage />;
      case 'mutuals':
        return <MutualsPage />;
      case 'history':
        return <HistoryPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'smart-unfollow':
        return <SmartUnfollowManagerPage />;
      case 'reports':
        return <ReportsPage />;
      case 'settings':
        return <SettingsPage />;
      case 'privacy':
        return <PrivacyPage />;
      default:
        return <DashboardPage />;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0D12] text-[#F8FAFC] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#8B5CF6] to-[#6366F1] flex items-center justify-center animate-pulse shadow-xl shadow-[#8B5CF6]/30">
          <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
        </div>
        <p className="text-xs text-[#94A3B8] font-medium tracking-wide">
          Initializing FollowTrack Secure Engine...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0D12] text-[#F8FAFC] flex flex-col">
      {/* Sidebar Navigation */}
      <Sidebar
        isOpen={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="lg:pl-64 flex flex-col min-h-screen">
        <Navbar onToggleMobileSidebar={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)} />

        <main className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
          {renderCurrentPage()}
        </main>
      </div>

      <ToastContainer />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

export default App;
