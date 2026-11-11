import React, { useEffect } from 'react';
import { useAppStore } from './stores/useAppStore';
import { Header } from './components/layout/Header';
import { StatusBar } from './components/layout/StatusBar';
import { Sidebar } from './components/sidebar/Sidebar';
import { EditorTabs } from './components/editor/EditorTabs';
import { CodeEditor } from './components/editor/CodeEditor';
import { TerminalPanel } from './components/terminal/TerminalPanel';
import { AgentPromptBar } from './components/agent/AgentPromptBar';
import { ApprovalModal } from './components/approvals/ApprovalModal';
import { CommandPalette } from './components/common/CommandPalette';
import { FileSearchModal } from './components/files/FileSearchModal';
import { TemplateGalleryModal } from './components/common/TemplateGalleryModal';
import { ProjectWizardModal } from './components/common/ProjectWizardModal';

export default function App() {
  const { loadProjects, initWebSocketListeners, fetchHealth, isTemplateGalleryOpen, setTemplateGalleryOpen, isProjectWizardOpen, setProjectWizardOpen } = useAppStore();

  useEffect(() => {
    initWebSocketListeners();
    loadProjects();
    fetchHealth();

    const interval = setInterval(() => {
      fetchHealth();
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen bg-ide-bg text-ide-text overflow-hidden font-sans">
      {/* Header */}
      <Header />

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar />

        {/* Center/Right Main Editor + Terminal */}
        <div className="flex-1 flex flex-col min-w-0 bg-ide-bg">
          <EditorTabs />
          <CodeEditor />
          <TerminalPanel />
        </div>
      </div>

      {/* Bottom Agent Controls */}
      <AgentPromptBar />

      {/* Status Bar */}
      <StatusBar />

      {/* Modals */}
      <ApprovalModal />
      <CommandPalette />
      <FileSearchModal />
      <TemplateGalleryModal
        isOpen={isTemplateGalleryOpen}
        onClose={() => setTemplateGalleryOpen(false)}
      />
      <ProjectWizardModal
        isOpen={isProjectWizardOpen}
        onClose={() => setProjectWizardOpen(false)}
      />
    </div>
  );
}
