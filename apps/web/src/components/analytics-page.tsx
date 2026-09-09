"use client";

import { useState, useEffect } from "react";
import { BarChart3, TrendingUp, PieChart, Activity, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";

export default function AnalyticsPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [dashData, pubData] = await Promise.all([
          api.generation.dashboard(),
          api.export.publishers().catch(() => []),
        ]);
        setStats({ ...dashData, publishers: pubData });
      } catch {
        setStats(null);
      }
      setLoading(false);
    };
    load();
  }, []);

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

  const totalFiles = stats?.total_files || 0;
  const totalExports = stats?.total_exports || 0;
  const publishers = stats?.publishers || [];

  const publisherGroups: Record<string, number> = {};
  publishers.forEach((p: any) => {
    const group = p.citation_style || "other";
    publisherGroups[group] = (publisherGroups[group] || 0) + 1;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div>
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-8 w-8 text-primary" />
          Analytics
        </h2>
        <p className="text-muted-foreground text-sm">
          Usage analytics and publisher distribution insights.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="bg-card border border-border rounded-xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-mono">Total Activity</span>
            <Activity className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="text-4xl font-bold text-foreground">{totalFiles + totalExports}</p>
          <p className="text-xs text-muted-foreground">files + exports combined</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-mono">File-to-Export Ratio</span>
            <TrendingUp className="h-4 w-4 text-blue-400" />
          </div>
          <p className="text-4xl font-bold text-foreground">
            {totalFiles > 0 ? ((totalExports / totalFiles) * 100).toFixed(0) : 0}%
          </p>
          <p className="text-xs text-muted-foreground">conversion rate</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-mono">Publisher Templates</span>
            <PieChart className="h-4 w-4 text-purple-400" />
          </div>
          <p className="text-4xl font-bold text-foreground">{publishers.length}</p>
          <p className="text-xs text-muted-foreground">available publishers</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">
            Publisher Citation Styles
          </h3>
          <div className="space-y-3">
            {Object.entries(publisherGroups).map(([style, count]) => (
              <div key={style} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-foreground font-medium">{style}</span>
                  <span className="text-xs font-mono text-muted-foreground">{count} publishers</span>
                </div>
                <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary/80 to-primary rounded-full transition-all"
                    style={{
                      width: Math.min(100, (count / maxVal(publisherGroups)) * 100) + "%",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">
            File Type Distribution
          </h3>
          <div className="space-y-3">
            {Object.entries(stats?.file_types || {}).length === 0 && (
              <p className="text-xs text-muted-foreground">No data yet.</p>
            )}
            {Object.entries(stats?.file_types || {}).map(([ext, count]) => {
              const colors: Record<string, string> = {
                ".pdf": "bg-rose-500",
                ".docx": "bg-blue-500",
                ".tex": "bg-emerald-500",
                ".md": "bg-purple-500",
                ".txt": "bg-amber-500",
                ".csv": "bg-cyan-500",
                ".json": "bg-orange-500",
              };
              return (
                <div key={ext} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-foreground font-mono">{ext || "(none)"}</span>
                    <span className="text-xs font-mono text-muted-foreground">{count as number}</span>
                  </div>
                  <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                    <div
                      className={
                        "h-full rounded-full transition-all " +
                        (colors[ext] || "bg-primary")
                      }
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
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 space-y-4 lg:col-span-2">
          <h3 className="font-semibold text-lg border-b border-border pb-3">
            All Publishers by Class
          </h3>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {publishers.map((p: any) => (
              <div
                key={p.key}
                className="flex items-center justify-between bg-background p-3 rounded-lg border border-border"
              >
                <div className="space-y-0.5">
                  <p className="text-sm font-medium text-foreground">{p.name}</p>
                  <p className="text-[10px] font-mono text-muted-foreground">{p.latex_class}</p>
                </div>
                <span className="text-[10px] font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                  {p.citation_style}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
