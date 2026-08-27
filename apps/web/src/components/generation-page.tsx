"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Sparkles, Send, FileText, Database, RefreshCw,
  CheckCircle, Loader2, Copy, Download
} from "lucide-react";

const API = "http://localhost:8000/api/v1";

const PAPER_TYPES = [
  "research", "review", "systematic_review", "meta_analysis",
  "case_study", "position", "conference", "theoretical",
  "methodological", "literature_review", "technical_report",
  "thesis", "white_paper"
];

const CITATION_STYLES = [
  "apa", "mla", "chicago", "ieee", "harvard",
  "vancouver", "ama", "acs", "turabian"
];

export default function GenerationPage() {
  const [mode, setMode] = useState<"scratch" | "content" | "data">("scratch");
  const [paperType, setPaperType] = useState("research");
  const [citationStyle, setCitationStyle] = useState("apa");
  const [topic, setTopic] = useState("");
  const [content, setContent] = useState("");
  const [keyPoints, setKeyPoints] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setGenerating(true);
    setError("");
    setResult(null);

    try {
      let endpoint = "";
      let body: any = {};

      if (mode === "scratch") {
        endpoint = API + "/generation/from-scratch";
        body = {
          topic,
          paper_type: paperType,
          citation_style: citationStyle,
          key_points: keyPoints.split("\n").filter(Boolean),
        };
      } else if (mode === "content") {
        endpoint = API + "/generation/from-content";
        body = {
          content,
          paper_type: paperType,
          citation_style: citationStyle,
          target_publisher: "ieee",
        };
      } else {
        endpoint = API + "/generation/from-data";
        body = {
          topic,
          paper_type: paperType,
          citation_style: citationStyle,
          data_description: content,
        };
      }

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div>
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-primary" />
          AI Paper Generation
        </h2>
        <p className="text-muted-foreground text-sm mt-1">
          Generate complete research papers using Google Gemini AI.
        </p>
      </div>

      {/* Mode Selection */}
      <div className="flex gap-2">
        {[
          { key: "scratch", label: "From Scratch", icon: Sparkles },
          { key: "content", label: "From Content", icon: FileText },
          { key: "data", label: "From Data", icon: Database },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setMode(key as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
              mode === key
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-card text-muted-foreground border-border hover:border-primary/50"
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Panel */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">
            Configuration
          </h3>

          <div className="space-y-3">
            <div>
              <label className="text-xs text-muted-foreground font-mono">Paper Type</label>
              <select
                value={paperType}
                onChange={(e) => setPaperType(e.target.value)}
                className="w-full mt-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground"
              >
                {PAPER_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground font-mono">Citation Style</label>
              <select
                value={citationStyle}
                onChange={(e) => setCitationStyle(e.target.value)}
                className="w-full mt-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground"
              >
                {CITATION_STYLES.map((s) => (
                  <option key={s} value={s}>{s.toUpperCase()}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground font-mono">
                {mode === "scratch" ? "Research Topic" : "Description"}
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Transformer architectures for NLP"
                className="w-full mt-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground"
              />
            </div>

            {mode === "scratch" && (
              <div>
                <label className="text-xs text-muted-foreground font-mono">
                  Key Points (one per line)
                </label>
                <textarea
                  value={keyPoints}
                  onChange={(e) => setKeyPoints(e.target.value)}
                  rows={4}
                  placeholder={"Attention mechanism is key\nSelf-supervised learning\nScalability challenges"}
                  className="w-full mt-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground font-mono"
                />
              </div>
            )}

            {(mode === "content" || mode === "data") && (
              <div>
                <label className="text-xs text-muted-foreground font-mono">
                  {mode === "content" ? "Raw Content" : "Data Description"}
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={6}
                  placeholder="Paste your content or describe your data..."
                  className="w-full mt-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground"
                />
              </div>
            )}
          </div>

          <Button
            onClick={handleGenerate}
            disabled={generating || !topic}
            className="w-full"
          >
            {generating ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Send className="h-4 w-4 mr-2" />
            )}
            {generating ? "Generating..." : "Generate Paper"}
          </Button>

          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Result Panel */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h3 className="font-semibold text-lg">Generated Paper</h3>
            {result && (
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => navigator.clipboard.writeText(JSON.stringify(result, null, 2))}
                >
                  <Copy className="h-3 w-3 mr-1" /> Copy
                </Button>
              </div>
            )}
          </div>

          {!result && !generating && (
            <div className="text-center py-16 text-muted-foreground">
              <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-30" />
              <p className="text-sm">Configure and click "Generate" to create your paper.</p>
            </div>
          )}

          {generating && (
            <div className="text-center py-16">
              <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Gemini is writing your paper...</p>
            </div>
          )}

          {result && (
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {result.title && (
                <div>
                  <span className="text-[10px] font-mono text-muted-foreground uppercase">Title</span>
                  <h4 className="text-lg font-bold text-foreground">{result.title}</h4>
                </div>
              )}
              {result.abstract && (
                <div>
                  <span className="text-[10px] font-mono text-muted-foreground uppercase">Abstract</span>
                  <p className="text-sm text-muted-foreground leading-relaxed">{result.abstract}</p>
                </div>
              )}
              {result.sections?.map((s: any, i: number) => (
                <div key={i}>
                  <span className="text-[10px] font-mono text-muted-foreground uppercase">
                    Section {i + 1}
                  </span>
                  <h5 className="font-semibold text-sm text-foreground">{s.heading}</h5>
                  <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{s.content}</p>
                </div>
              ))}
              {result.references?.length > 0 && (
                <div>
                  <span className="text-[10px] font-mono text-muted-foreground uppercase">References</span>
                  <ol className="list-decimal list-inside text-xs text-muted-foreground space-y-1">
                    {result.references.map((r: any, i: number) => (
                      <li key={i}>{typeof r === "string" ? r : `${r.authors?.join(", ")}. ${r.title}. ${r.journal}. ${r.year}.`}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
