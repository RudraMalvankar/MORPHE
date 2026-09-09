"use client";

import { useState, useEffect } from "react";
import {
  LayoutDashboard, FolderKanban, FileText, Download, Sparkles,
  Database, Clock, TrendingUp, RefreshCw, Globe,
} from "lucide-react";
import { api } from "@/lib/api";

interface DashboardStats {
  total_files: number;
  total_exports: number;
  total_publishers: number;
  file_types: Record<string, number>;
  export_types: Record<string, number>;
  storage_size_bytes: number;
  gemini_status: string;
  dev_mode: boolean;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState<any[]>([]);

  const loadStats = async () => {
    setLoading(true);
    try {
      const [dashData, projData] = await Promise.all([
        api.generation.dashboard(),
        api.projects.list().catch(() => ({ projects: [] })),
      ]);
      setStats(dashData);
      setProjects(projData.projects || []);
    } catch {
      setStats(null);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadStats();
  }, []);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  const maxVal = (obj: Record<string, number>) => {
    const vals = Object.values(obj);
    return vals.length > 0 ? Math.max.apply(null, vals) : 1;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <LayoutDashboard className="h-8 w-8 text-primary" />
            Dashboard
          </h2>
          <p className="text-muted-foreground text-sm">
            System overview and quick stats for MORPHE.
          </p>
        </div>
        <button
          onClick={loadStats}
          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground"
        >
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Projects", value: projects.length, icon: FolderKanban, color: "text-blue-400" },
          { label: "Files Uploaded", value: stats?.total_files || 0, icon: FileText, color: "text-emerald-400" },
          { label: "Exports Generated", value: stats?.total_exports || 0, icon: Download, color: "text-purple-400" },
          { label: "Publishers", value: stats?.total_publishers || 0, icon: Globe, color: "text-amber-400" },
        ].map((card, i) => (
          <div key={i} className="bg-card border border-border rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground font-mono">{card.label}</span>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </div>
            <p className="text-3xl font-bold text-foreground">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">System Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between bg-background p-3 rounded-lg border border-border">
              <span className="text-sm text-muted-foreground">Gemini AI</span>
              <span
                className={
                  "text-xs font-mono px-2 py-0.5 rounded " +
                  (stats?.gemini_status === "available"
                    ? "bg-emerald-500/10 text-emerald-400"
                    : "bg-amber-500/10 text-amber-400")
                }
              >
                {stats?.gemini_status || "unavailable"}
              </span>
            </div>
            <div className="flex items-center justify-between bg-background p-3 rounded-lg border border-border">
              <span className="text-sm text-muted-foreground">Dev Mode</span>
              <span
                className={
                  "text-xs font-mono px-2 py-0.5 rounded " +
                  (stats?.dev_mode
                    ? "bg-emerald-500/10 text-emerald-400"
                    : "bg-muted text-muted-foreground")
                }
              >
                {stats?.dev_mode ? "enabled" : "disabled"}
              </span>
            </div>
            <div className="flex items-center justify-between bg-background p-3 rounded-lg border border-border">
              <span className="text-sm text-muted-foreground">Storage Used</span>
              <span className="text-xs font-mono text-foreground">
                {formatBytes(stats?.storage_size_bytes || 0)}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">File Types</h3>
          <div className="space-y-2">
            {Object.entries(stats?.file_types || {}).length === 0 && (
              <p className="text-xs text-muted-foreground">No files uploaded yet.</p>
            )}
            {Object.entries(stats?.file_types || {}).map(([ext, count]) => (
              <div key={ext} className="flex items-center justify-between">
                <span className="text-sm font-mono text-foreground">{ext || "(no ext)"}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{
                        width:
                          Math.min(
                            100,
                            ((count as number) /
                              maxVal(stats?.file_types || {})) *
                                100
                          ) + "%",
                      }}
                    />
                  </div>
                  <span className="text-xs font-mono text-muted-foreground w-8 text-right">
                    {count as number}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">Export Formats</h3>
          <div className="space-y-2">
            {Object.entries(stats?.export_types || {}).length === 0 && (
              <p className="text-xs text-muted-foreground">No exports yet.</p>
            )}
            {Object.entries(stats?.export_types || {}).map(([ext, count]) => (
              <div key={ext} className="flex items-center justify-between">
                <span className="text-sm font-mono text-foreground">{ext}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-purple-500 rounded-full"
                      style={{
                        width:
                          Math.min(
                            100,
                            ((count as number) /
                              maxVal(stats?.export_types || {})) *
                                100
                          ) + "%",
                      }}
                    />
                  </div>
                  <span className="text-xs font-mono text-muted-foreground w-8 text-right">
                    {count as number}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">Recent Projects</h3>
          <div className="space-y-2">
            {projects.length === 0 && (
              <p className="text-xs text-muted-foreground">No projects yet.</p>
            )}
            {projects.slice(0, 5).map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between bg-background p-3 rounded-lg border border-border"
              >
                <div className="space-y-0.5">
                  <p className="text-sm font-medium text-foreground line-clamp-1">{p.title}</p>
                  <p className="text-[10px] text-muted-foreground font-mono flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(p.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className="text-[10px] font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                  {p.default_publisher_target?.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
