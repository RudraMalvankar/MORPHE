"use client";

import Link from "next/link";
import { FileText, Cpu, Settings, FolderKanban } from "lucide-react";

export function NavShell({ children }: { children: React.ReactNode }) {
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
            <Link
              href="#"
              className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md bg-accent text-accent-foreground"
            >
              <FolderKanban className="h-4 w-4" />
              Workspaces
            </Link>
            <Link
              href="#"
              className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-accent/50 hover:text-foreground"
            >
              <FileText className="h-4 w-4" />
              Documents
            </Link>
            <Link
              href="#"
              className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-accent/50 hover:text-foreground"
            >
              <Cpu className="h-4 w-4" />
              NLP Engine
            </Link>
          </nav>

          <div className="pt-4 border-t border-border">
            <Link
              href="#"
              className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-accent/50 hover:text-foreground"
            >
              <Settings className="h-4 w-4" />
              Settings
            </Link>
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
