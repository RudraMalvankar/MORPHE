"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { BookOpen, Search, Globe, BookMarked, BarChart3, CheckCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function KnowledgeBasePage() {
  const [tab, setTab] = useState<"publishers" | "citations" | "journals">("publishers");
  const [publishers, setPublishers] = useState<any>({});
  const [citationStyles, setCitationStyles] = useState<any>({});
  const [journals, setJournals] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [selectedItem, setSelectedItem] = useState<any>(null);

  useEffect(() => {
    api.knowledge.stats().then(setStats).catch(() => {});
    api.knowledge.publishers().then(setPublishers).catch(() => {});
    api.knowledge.citations().then(setCitationStyles).catch(() => {});
    api.knowledge.journals().then(setJournals).catch(() => {});
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) { setSearchResults([]); return; }
    try {
      const data = await api.knowledge.search({ query: searchQuery, limit: 20 });
      setSearchResults(data.results || []);
    } catch { setSearchResults([]); }
  };

  const publisherEntries = Object.entries(publishers);
  const citationEntries = Object.entries(citationStyles);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <BookOpen className="h-8 w-8 text-primary" />
            Knowledge Base
          </h2>
          <p className="text-muted-foreground text-sm mt-1">Publisher guidelines, citation styles, and journal metrics.</p>
        </div>
        {stats && (
          <div className="flex gap-4 text-xs font-mono">
            <span className="bg-muted px-2 py-1 rounded">{stats.publishers} publishers</span>
            <span className="bg-muted px-2 py-1 rounded">{stats.citation_styles} styles</span>
            <span className="bg-muted px-2 py-1 rounded">{stats.journals} journals</span>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search publishers, styles, journals..."
            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-md text-sm text-foreground placeholder:text-muted-foreground"
          />
        </div>
        <Button onClick={handleSearch} variant="outline">Search</Button>
      </div>

      {searchResults.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-6 space-y-3">
          <h3 className="font-semibold text-sm border-b border-border pb-2">Search Results ({searchResults.length})</h3>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {searchResults.map((r, i) => (
              <div key={i} className="p-3 bg-background border border-border rounded-lg text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono bg-muted px-1.5 py-0.5 rounded">{r.category}</span>
                  <span className="font-medium text-foreground">{r.key}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-2">
        {[
          { key: "publishers" as const, label: "Publishers", icon: Globe },
          { key: "citations" as const, label: "Citation Styles", icon: BookMarked },
          { key: "journals" as const, label: "Journal Metrics", icon: BarChart3 },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => { setTab(key); setSelectedItem(null); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
              tab === key ? "bg-primary text-primary-foreground border-primary" : "bg-card text-muted-foreground border-border hover:border-primary/50"
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      {tab === "publishers" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {publisherEntries.map(([key, data]: [string, any]) => (
            <div key={key} onClick={() => setSelectedItem({ type: "publisher", key, data })}
              className={`bg-card border border-border rounded-xl p-5 cursor-pointer transition-all hover:shadow-md ${
                selectedItem?.key === key ? "ring-2 ring-primary" : ""
              }`}>
              <h4 className="font-semibold text-foreground">{data.name}</h4>
              <div className="mt-2 space-y-1 text-xs text-muted-foreground">
                <div className="flex justify-between"><span>Abstract limit</span><span className="font-mono">{data.abstract_word_limit || "N/A"} words</span></div>
                <div className="flex justify-between"><span>Page limit</span><span className="font-mono">{data.page_limit || "N/A"}</span></div>
                <div className="flex justify-between"><span>Review process</span><span className="font-mono">{data.review_process || "N/A"}</span></div>
              </div>
              <div className="flex flex-wrap gap-1 mt-3">
                {data.required_sections?.slice(0, 3).map((s: string) => (
                  <span key={s} className="text-[10px] font-mono bg-muted px-1.5 py-0.5 rounded">{s}</span>
                ))}
                {data.required_sections?.length > 3 && (
                  <span className="text-[10px] text-muted-foreground">+{data.required_sections.length - 3} more</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "citations" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {citationEntries.map(([key, data]: [string, any]) => (
            <div key={key} onClick={() => setSelectedItem({ type: "citation", key, data })}
              className={`bg-card border border-border rounded-xl p-5 cursor-pointer transition-all hover:shadow-md ${
                selectedItem?.key === key ? "ring-2 ring-primary" : ""
              }`}>
              <h4 className="font-semibold text-foreground">{data.name}</h4>
              <div className="mt-3 space-y-2 text-xs">
                <div><span className="text-muted-foreground font-mono">In-text: </span><code className="bg-muted px-1.5 py-0.5 rounded">{data.in_text_format}</code></div>
                <div><span className="text-muted-foreground font-mono">Order: </span><span className="text-foreground">{data.order}</span></div>
              </div>
              {data.rules && (
                <div className="mt-3 text-[10px] text-muted-foreground space-y-1">
                  {data.rules.slice(0, 2).map((r: string, i: number) => (
                    <div key={i} className="flex items-start gap-1"><CheckCircle className="h-3 w-3 mt-0.5 shrink-0" />{r}</div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === "journals" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {journals.map((j, i) => (
            <div key={i} onClick={() => setSelectedItem({ type: "journal", key: j.journal_name, data: j })}
              className={`bg-card border border-border rounded-xl p-5 cursor-pointer transition-all hover:shadow-md ${
                selectedItem?.key === j.journal_name ? "ring-2 ring-primary" : ""
              }`}>
              <div className="flex items-start justify-between">
                <h4 className="font-semibold text-sm text-foreground line-clamp-2">{j.journal_name}</h4>
                <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                  j.quartile === "Q1" ? "bg-emerald-500/10 text-emerald-400" : "bg-muted text-muted-foreground"
                }`}>{j.quartile}</span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                <div className="bg-background p-2 rounded border border-border text-center">
                  <span className="text-[10px] text-muted-foreground font-mono">IF</span>
                  <p className="font-bold text-foreground">{j.impact_factor}</p>
                </div>
                <div className="bg-background p-2 rounded border border-border text-center">
                  <span className="text-[10px] text-muted-foreground font-mono">H-Index</span>
                  <p className="font-bold text-foreground">{j.h_index}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-1 mt-3">
                {j.topics?.slice(0, 2).map((t: string) => (
                  <span key={t} className="text-[10px] bg-muted px-1.5 py-0.5 rounded">{t}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedItem && (
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h3 className="font-semibold text-lg text-foreground">{selectedItem.key}</h3>
            <button onClick={() => setSelectedItem(null)} className="text-xs text-muted-foreground hover:text-foreground">Close</button>
          </div>
          <pre className="text-xs text-muted-foreground font-mono whitespace-pre-wrap bg-background border border-border rounded-lg p-4 max-h-64 overflow-y-auto">
            {JSON.stringify(selectedItem.data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
