import React, { useState } from 'react';
import { ScreenType, NavTab, UserProfile, ActivityItem, Shelter, Hospital } from './types';
import { defaultUserProfile, initialActivities } from './data/mockData';
import { StatusBar } from './components/StatusBar';
import { BottomNav } from './components/BottomNav';
import { SignInScreen } from './screens/SignInScreen';
import { HomeScreen } from './screens/HomeScreen';
import { NeedHelpScreen } from './screens/NeedHelpScreen';
import { SafeSheltersScreen } from './screens/SafeSheltersScreen';
import { MedicalHelpScreen } from './screens/MedicalHelpScreen';
import { DisasterMapScreen } from './screens/DisasterMapScreen';
import { ReportIncidentScreen } from './screens/ReportIncidentScreen';
import { HistoryScreen } from './screens/HistoryScreen';
import { SettingsScreen } from './screens/SettingsScreen';
import { AlertsScreen } from './screens/AlertsScreen';
import { EmergencyChatScreen } from './screens/EmergencyChatScreen';
import { OfflineNetworkScreen } from './screens/OfflineNetworkScreen';
import { DirectionsModal } from './components/DirectionsModal';
import { SosAlertModal } from './components/SosAlertModal';

export const CitizenApp: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<ScreenType>('signin');
  const [activeTab, setActiveTab] = useState<NavTab>('home');
  const [userProfile, setUserProfile] = useState<UserProfile>(defaultUserProfile);
  const [activities, setActivities] = useState<ActivityItem[]>(initialActivities);
  const [sosModalOpen, setSosModalOpen] = useState(false);
  const [directionsTarget, setDirectionsTarget] = useState<{
    name: string;
    area: string;
    distance: string;
  } | null>(null);

  // Sync bottom tab when current screen matches a tab
  const handleNavigate = (screen: ScreenType) => {
    setCurrentScreen(screen);
    if (screen === 'home') setActiveTab('home');
    else if (screen === 'alerts') setActiveTab('alerts');
    else if (screen === 'safe-shelters') setActiveTab('shelters');
    else if (screen === 'disaster-map') setActiveTab('map');
    else if (screen === 'history') setActiveTab('history');
    else if (screen === 'settings') setActiveTab('settings');
  };

  const handleTabChange = (tab: NavTab) => {
    setActiveTab(tab);
    switch (tab) {
      case 'home':
        setCurrentScreen('home');
        break;
      case 'alerts':
        setCurrentScreen('alerts');
        break;
      case 'shelters':
        setCurrentScreen('safe-shelters');
        break;
      case 'map':
        setCurrentScreen('disaster-map');
        break;
      case 'history':
        setCurrentScreen('history');
        break;
      case 'settings':
        setCurrentScreen('settings');
        break;
    }
  };

  const handleHelpRequestSubmit = (newActivity: ActivityItem) => {
    setActivities((prev) => [newActivity, ...prev]);
  };

  const handleReportSubmit = (newReport: ActivityItem) => {
    setActivities((prev) => [newReport, ...prev]);
  };

  const handleOpenDirections = (place: Shelter | Hospital) => {
    setDirectionsTarget({
      name: place.name,
      area: place.area,
      distance: place.distance,
    });
  };

  // Determine whether to render the Bottom Navigation Bar
  const shouldShowBottomNav =
    currentScreen === 'home' ||
    currentScreen === 'alerts' ||
    currentScreen === 'safe-shelters' ||
    currentScreen === 'disaster-map' ||
    currentScreen === 'history' ||
    currentScreen === 'settings' ||
    currentScreen === 'need-help';

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-0 sm:p-4 md:p-6 font-sans">
      {/* Mobile Device Frame Container */}
      <div className="w-full sm:max-w-[428px] h-screen sm:h-[920px] sm:max-h-[92vh] bg-white sm:rounded-[44px] shadow-2xl sm:border-[8px] sm:border-slate-800 flex flex-col overflow-hidden relative">
        {/* Status Bar */}
        <StatusBar />

        {/* Screen Router */}
        <div className="flex-1 flex flex-col overflow-hidden relative">
          {currentScreen === 'signin' && (
            <SignInScreen
              onSignInSuccess={(profile) => {
                setUserProfile((prev) => ({ ...prev, ...profile }));
                setCurrentScreen('home');
              }}
              onSuccessSignIn={(phone) => {
                setUserProfile((prev) => ({ ...prev, phone }));
                setCurrentScreen('home');
              }}
              onBack={() => setCurrentScreen('home')}
            />
          )}

          {currentScreen === 'home' && (
            <HomeScreen
              user={userProfile}
              userProfile={userProfile}
              onNavigate={handleNavigate}
              onTriggerSos={() => setSosModalOpen(true)}
            />
          )}

          {currentScreen === 'alerts' && (
            <AlertsScreen
              onBack={() => handleNavigate('home')}
            />
          )}

          {currentScreen === 'need-help' && (
            <NeedHelpScreen
              onBack={() => handleNavigate('home')}
              onSubmitHelpRequest={handleHelpRequestSubmit}
            />
          )}

          {currentScreen === 'safe-shelters' && (
            <SafeSheltersScreen
              onBack={() => handleNavigate('home')}
              onOpenDirections={handleOpenDirections}
              onOpenFullMap={() => handleNavigate('disaster-map')}
            />
          )}

          {currentScreen === 'medical-help' && (
            <MedicalHelpScreen
              onBack={() => handleNavigate('home')}
              onOpenDirections={handleOpenDirections}
            />
          )}

          {currentScreen === 'disaster-map' && (
            <DisasterMapScreen
              onBack={() => handleNavigate('home')}
              onNavigateToShelters={() => handleNavigate('safe-shelters')}
              onNavigateToMedical={() => handleNavigate('medical-help')}
            />
          )}

          {currentScreen === 'report-incident' && (
            <ReportIncidentScreen
              onBack={() => handleNavigate('home')}
              onSubmitReport={handleReportSubmit}
            />
          )}

          {currentScreen === 'history' && (
            <HistoryScreen
              activities={activities}
              onSelectActivity={(act) => {
                // If it's a chat, navigate to emergency chat
                if (act.type === 'chat') {
                  setCurrentScreen('emergency-chat');
                }
              }}
            />
          )}

          {currentScreen === 'settings' && (
            <SettingsScreen
              userProfile={userProfile}
              onUpdateProfile={(updated) => setUserProfile((prev) => ({ ...prev, ...updated }))}
              onSignOut={() => setCurrentScreen('signin')}
            />
          )}

          {currentScreen === 'emergency-chat' && (
            <EmergencyChatScreen
              userProfile={userProfile}
              onBack={() => handleNavigate('home')}
            />
          )}

          {currentScreen === 'offline-network' && (
            <OfflineNetworkScreen
              onBack={() => handleNavigate('home')}
            />
          )}
        </div>

        {/* Bottom Navigation */}
        {shouldShowBottomNav && (
          <BottomNav activeTab={activeTab} onChangeTab={handleTabChange} />
        )}

        {/* Directions Modal */}
        {directionsTarget && (
          <DirectionsModal
            destinationName={directionsTarget.name}
            destinationArea={directionsTarget.area}
            distance={directionsTarget.distance}
            onClose={() => setDirectionsTarget(null)}
            onOpenMap={() => {
              setDirectionsTarget(null);
              handleNavigate('disaster-map');
            }}
          />
        )}

        {/* Emergency SOS Active Modal */}
        {sosModalOpen && (
          <SosAlertModal
            userProfile={userProfile}
            onCancel={() => setSosModalOpen(false)}
            onOpenChat={() => {
              setSosModalOpen(false);
              setCurrentScreen('emergency-chat');
            }}
          />
        )}
      </div>

      {/* Responsive screen quick switcher bar for desktop users */}
      <div className="hidden sm:flex items-center space-x-2 mt-3 bg-slate-800/80 backdrop-blur-xs px-4 py-2 rounded-full border border-slate-700 text-xs text-slate-300">
        <span className="text-[11px] font-semibold text-slate-400">Quick Screen Switch:</span>
        {[
          { id: 'home', label: 'Home' },
          { id: 'need-help', label: 'I Need Help' },
          { id: 'safe-shelters', label: 'Shelters' },
          { id: 'medical-help', label: 'Medical' },
          { id: 'disaster-map', label: 'Disaster Map' },
          { id: 'report-incident', label: 'Report' },
          { id: 'emergency-chat', label: 'Chat' },
          { id: 'offline-network', label: 'Mesh' },
          { id: 'history', label: 'History' },
          { id: 'settings', label: 'Settings' },
          { id: 'signin', label: 'Sign In' },
        ].map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => handleNavigate(s.id as ScreenType)}
            className={`px-2.5 py-1 rounded-full text-[11px] transition-colors ${
              currentScreen === s.id
                ? 'bg-red-600 text-white font-bold'
                : 'hover:bg-slate-700 text-slate-300'
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
