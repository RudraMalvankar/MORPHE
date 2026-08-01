"use client";

import { useState, useEffect } from "react";
import { useAppStore } from "@/store/use-app-store";
import { FileText, Cpu, Settings, FolderKanban } from "lucide-react";

export function NavShell({ children }: { children: React.ReactNode }) {
  const { activeTab, setActiveTab } = useAppStore();
  const [mounted, setMounted] = useState(false);
  console.log("NAV_SHELL: rendered, activeTab is", activeTab, "mounted is", mounted);

  useEffect(() => {
    setMounted(true);
  }, []);

  const getLinkClass = (tab: string) => {
    const base = "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md w-full text-left transition-colors ";
    if (activeTab === tab) {
      return base + "bg-primary text-primary-foreground";
    }
    return base + "text-muted-foreground hover:bg-accent/50 hover:text-foreground";
  };

  if (!mounted) {
    return <div className="min-h-screen bg-background text-foreground p-6">{children}</div>;
  }

  return (
    <div className="flex h-screen w-full flex-col bg-background text-foreground overflow-hidden">
      {/* Top Navbar */}
      <header className="flex h-14 items-center justify-between border-b border-border px-6 bg-card">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-lg">
            M
          </div>
          <span className="font-semibold text-lg tracking-wider">MORPHE</span>
          <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded border border-border">
            v1.0.0
          </span>
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span>AI-Powered Research Document Intelligence Platform</span>
        </div>
      </header>

      {/* Main Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 border-r border-border bg-card p-4 flex flex-col justify-between">
          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab("workspaces")}
              className={getLinkClass("workspaces")}
            >
              <FolderKanban className="h-4 w-4" />
              Workspaces
            </button>
            <button
              onClick={() => setActiveTab("documents")}
              className={getLinkClass("documents")}
            >
              <FileText className="h-4 w-4" />
              Documents
            </button>
            <button
              onClick={() => setActiveTab("nlp")}
              className={getLinkClass("nlp")}
            >
              <Cpu className="h-4 w-4" />
              NLP Engine
            </button>
          </nav>

          <div className="pt-4 border-t border-border">
            <button
              onClick={() => setActiveTab("settings")}
              className={getLinkClass("settings")}
            >
              <Settings className="h-4 w-4" />
              Settings
            </button>
          </div>
        </aside>

        {/* Content Viewport */}
        <main className="flex-1 overflow-auto p-6 bg-background">
          {children}
        </main>
      </div>
    </div>
  );
}
