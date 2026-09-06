"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Sparkles, Send, FileText, Database, Loader2,
  Copy, ChevronRight, ChevronLeft, CheckCircle
} from "lucide-react";
import { api } from "@/lib/api";

const PAPER_TYPES = [
  { value: "research", label: "Research Paper" },
  { value: "review", label: "Review Paper" },
  { value: "systematic_review", label: "Systematic Review" },
  { value: "meta_analysis", label: "Meta-Analysis" },
  { value: "case_study", label: "Case Study" },
  { value: "position", label: "Position Paper" },
  { value: "conference", label: "Conference Paper" },
  { value: "technical_report", label: "Technical Report" },
  { value: "thesis", label: "Thesis Chapter" },
  { value: "white_paper", label: "White Paper" },
];

const CITATION_STYLES = [
  { value: "apa", label: "APA" },
  { value: "mla", label: "MLA" },
  { value: "chicago", label: "Chicago" },
  { value: "ieee", label: "IEEE" },
  { value: "harvard", label: "Harvard" },
  { value: "vancouver", label: "Vancouver" },
  { value: "ama", label: "AMA" },
  { value: "acs", label: "ACS" },
  { value: "turabian", label: "Turabian" },
];

type WizardStep = "mode" | "config" | "content" | "generate";

export default function GenerationPage() {
  const [step, setStep] = useState<WizardStep>("mode");
  const [mode, setMode] = useState<"scratch" | "content" | "data">("scratch");
  const [paperType, setPaperType] = useState("research");
  const [citationStyle, setCitationStyle] = useState("apa");
  const [topic, setTopic] = useState("");
  const [keyPoints, setKeyPoints] = useState("");
  const [content, setContent] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const steps: WizardStep[] = ["mode", "config", "content", "generate"];
  const currentIdx = steps.indexOf(step);

  const next = () => {
    if (currentIdx < steps.length - 1) setStep(steps[currentIdx + 1]);
  };
  const prev = () => {
    if (currentIdx > 0) setStep(steps[currentIdx - 1]);
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError("");
    setResult(null);
    try {
      let data;
      if (mode === "scratch") {
        data = await api.generation.fromScratch({
          topic,
          paper_type: paperType,
          citation_style: citationStyle,
          key_points: keyPoints.split("\n").filter(Boolean),
        });
      } else if (mode === "content") {
        data = await api.generation.fromContent({
          content,
          paper_type: paperType,
          citation_style: citationStyle,
          target_publisher: "ieee",
        });
      } else {
        data = await api.generation.fromData({
          topic,
          paper_type: paperType,
          citation_style: citationStyle,
          data_description: content,
        });
      }
      setResult(data);
      setStep("generate");
    } catch (e: any) {
      setError(e.message || "Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const canNext = () => {
    if (step === "mode") return true;
    if (step === "config") return topic.trim().length > 0;
    if (step === "content") return content.trim().length > 0 || mode === "scratch";
    return false;
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300 max-w-5xl">
      <div>
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-primary" />
          AI Paper Generation
        </h2>
        <p className="text-muted-foreground text-sm mt-1">
          Generate complete research papers powered by Google Gemini.
        </p>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-2">
        {steps.map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border ${
              i < currentIdx ? "bg-primary text-primary-foreground border-primary" :
              i === currentIdx ? "border-primary text-primary" :
              "border-border text-muted-foreground"
            }`}>
              {i < currentIdx ? <CheckCircle className="h-4 w-4" /> : i + 1}
            </div>
            <span className={`text-xs ${i === currentIdx ? "text-foreground font-medium" : "text-muted-foreground"}`}>
              {s === "mode" ? "Mode" : s === "config" ? "Config" : s === "content" ? "Content" : "Result"}
            </span>
            {i < steps.length - 1 && <div className="w-8 h-px bg-border" />}
          </div>
        ))}
      </div>

      {/* Step: Mode Selection */}
      {step === "mode" && (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Choose Generation Mode</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {[
              { key: "scratch" as const, icon: Sparkles, title: "From Scratch", desc: "Start with just a topic. AI writes the entire paper." },
              { key: "content" as const, icon: FileText, title: "From Content", desc: "Provide raw text/notes. AI structures and refines it." },
              { key: "data" as const, icon: Database, title: "From Data", desc: "Upload CSV/data. AI generates analysis sections." },
            ].map(({ key, icon: Icon, title, desc }) => (
              <button
                key={key}
                onClick={() => { setMode(key); next(); }}
                className={`p-6 rounded-xl border text-left transition-all hover:shadow-md ${
                  mode === key
                    ? "bg-primary/10 border-primary ring-1 ring-primary"
                    : "bg-card border-border hover:border-primary/50"
                }`}
              >
                <Icon className="h-8 w-8 text-primary mb-3" />
                <h4 className="font-semibold text-foreground">{title}</h4>
                <p className="text-sm text-muted-foreground mt-1">{desc}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step: Config */}
      {step === "config" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="bg-card border border-border rounded-xl p-6 space-y-4">
            <h3 className="font-semibold text-lg border-b border-border pb-3">Paper Configuration</h3>
            <div>
              <label className="text-xs text-muted-foreground font-mono">Research Topic *</label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Transformer architectures for NLP"
                className="w-full mt-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground font-mono">Paper Type</label>
              <select
                value={paperType}
                onChange={(e) => setPaperType(e.target.value)}
                className="w-full mt-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground"
              >
                {PAPER_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
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
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="bg-card border border-border rounded-xl p-6 space-y-4">
            <h3 className="font-semibold text-lg border-b border-border pb-3">Key Points</h3>
            <p className="text-xs text-muted-foreground">Optional: Add key points (one per line) to guide the generation.</p>
            <textarea
              value={keyPoints}
              onChange={(e) => setKeyPoints(e.target.value)}
              rows={8}
              placeholder={"Attention mechanism is key\nSelf-supervised learning\nScalability challenges\nNovel architecture proposed"}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground font-mono"
            />
          </div>
        </div>
      )}

      {/* Step: Content */}
      {step === "content" && mode !== "scratch" && (
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">
            {mode === "content" ? "Raw Content" : "Data Description"}
          </h3>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={12}
            placeholder={mode === "content"
              ? "Paste your research notes, draft text, or raw content here..."
              : "Describe your dataset: what columns, what analysis you need, sample data..."}
            className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground"
          />
        </div>
      )}

      {step === "content" && mode === "scratch" && (
        <div className="bg-card border border-border rounded-xl p-6 text-center py-16">
          <Sparkles className="h-12 w-12 mx-auto mb-4 text-primary opacity-50" />
          <p className="text-muted-foreground">Ready to generate from scratch. Click Next to proceed.</p>
        </div>
      )}

      {/* Step: Generate / Result */}
      {step === "generate" && (
        <div className="space-y-4">
          {!result && (
            <div className="bg-card border border-border rounded-xl p-6 text-center py-16">
              {generating ? (
                <>
                  <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin text-primary" />
                  <p className="text-foreground font-medium">Gemini is writing your paper...</p>
                  <p className="text-xs text-muted-foreground mt-2">This may take 30-60 seconds</p>
                </>
              ) : (
                <>
                  <h3 className="font-semibold text-lg mb-2">Ready to Generate</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Topic: <span className="text-foreground">{topic}</span> | Type: {paperType} | Style: {citationStyle.toUpperCase()}
                  </p>
                  <Button onClick={handleGenerate} size="lg">
                    <Sparkles className="h-4 w-4 mr-2" /> Generate Paper
                  </Button>
                </>
              )}
              {error && (
                <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-sm text-left">
                  {error}
                </div>
              )}
            </div>
          )}

          {result && (
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="font-semibold text-lg">Generated Paper</h3>
                <Button size="sm" variant="outline" onClick={() => navigator.clipboard.writeText(JSON.stringify(result, null, 2))}>
                  <Copy className="h-3 w-3 mr-1" /> Copy JSON
                </Button>
              </div>
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
                    <span className="text-[10px] font-mono text-muted-foreground uppercase">Section {i + 1}</span>
                    <h5 className="font-semibold text-sm text-foreground">{s.heading}</h5>
                    <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{s.content}</p>
                  </div>
                ))}
                {result.references?.length > 0 && (
                  <div>
                    <span className="text-[10px] font-mono text-muted-foreground uppercase">References</span>
                    <ol className="list-decimal list-inside text-xs text-muted-foreground space-y-1">
                      {result.references.map((r: any, i: number) => (
                        <li key={i}>{typeof r === "string" ? r : (r.authors || []).join(", ") + ". " + r.title + ". " + r.journal + ". " + r.year + "."}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
              <Button variant="outline" onClick={() => { setResult(null); setStep("mode"); }}>
                Generate Another
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Navigation */}
      {step !== "generate" && (
        <div className="flex justify-between">
          <Button variant="outline" onClick={prev} disabled={currentIdx === 0}>
            <ChevronLeft className="h-4 w-4 mr-1" /> Back
          </Button>
          <Button onClick={next} disabled={!canNext()}>
            Next <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  );
}
