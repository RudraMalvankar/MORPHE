"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  FileText, Sparkles, Loader2, Send, FileUp, ListChecks,
  ChevronRight, ChevronLeft, AlertCircle,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAppStore } from "@/store/use-app-store";

const PAPER_TYPES = [
  "original_research", "review", "meta_analysis", "case_study",
  "short_communication", "technical_note", "perspective",
];
const DOMAINS = [
  "Computer Science", "Physics", "Chemistry", "Biology", "Medicine",
  "Mathematics", "Engineering", "Psychology", "Economics", "Sociology",
];

export default function GenerationPage() {
  const { activeProject } = useAppStore();
  const [mode, setMode] = useState<"scratch" | "content" | "data">("scratch");
  const [step, setStep] = useState(0);
  const [topic, setTopic] = useState("");
  const [keywords, setKeywords] = useState("");
  const [paperType, setPaperType] = useState("original_research");
  const [domain, setDomain] = useState("Computer Science");
  const [userContent, setUserContent] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [events, setEvents] = useState<any[]>([]);
  const [generatedPaper, setGeneratedPaper] = useState<any>(null);
  const [uploadedFile, setUploadedFile] = useState<any>(null);
  const [streamError, setStreamError] = useState("");
  const abortRef = useRef<AbortController | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    try {
      const result = await api.upload.document(e.target.files[0]);
      setUploadedFile(result);
    } catch (err: any) {
      alert("Upload failed: " + err.message);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setEvents([]);
    setGeneratedPaper(null);
    setStreamError("");
    setStep(3);

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      setStreamError("Generation timed out after 120 seconds");
      setIsGenerating(false);
      abortRef.current?.abort();
    }, 120000);

    const data: any = {
      topic,
      keywords: keywords.split(",").map((k) => k.trim()).filter(Boolean),
      paper_type: paperType,
      research_domain: domain,
      project_id: activeProject || "dev-project",
    };
    if (mode === "content" && userContent.trim()) {
      data.raw_content = userContent;
    }
    if (uploadedFile) {
      data.file_id = uploadedFile.file_id;
    }

    try {
      await api.generation.stream(data, (event) => {
        setEvents((prev) => [...prev, event]);
        if (event.type === "complete") {
          if (timerRef.current) clearTimeout(timerRef.current);
          setGeneratedPaper({
            title: event.title,
            keywords: event.keywords,
            sections: event.sections,
          });
          setIsGenerating(false);
        }
        if (event.type === "error") {
          if (timerRef.current) clearTimeout(timerRef.current);
          setStreamError(event.message || "Generation failed");
          setIsGenerating(false);
        }
      });
    } catch (err: any) {
      if (timerRef.current) clearTimeout(timerRef.current);
      setStreamError(err.message || "Connection failed");
      setEvents((prev) => [...prev, { type: "error", message: err.message }]);
      setIsGenerating(false);
    }
  };

  const sections = events.filter((e) => e.type === "section");
  const steps = events.filter((e) => e.type === "step");
  const titleEvent = events.find((e) => e.type === "title");
  const keywordsEvent = events.find((e) => e.type === "keywords");

  if (isGenerating || generatedPaper) {
    return (
      <div className="space-y-6 animate-in fade-in duration-300">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-primary" />
            {isGenerating ? "Generating..." : "Generated Paper"}
          </h2>
          {isGenerating && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Streaming...
            </div>
          )}
        </div>

        {streamError && (
          <div className="bg-rose-500/10 border border-rose-500/20 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-rose-400" />
            <span className="text-sm text-rose-400">{streamError}</span>
          </div>
        )}

        {titleEvent && (
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="text-xl font-bold text-foreground">{titleEvent.title}</h3>
            {keywordsEvent && (
              <div className="flex flex-wrap gap-2 mt-3">
                {keywordsEvent.keywords.map((k: string) => (
                  <span key={k} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                    {k}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="space-y-4">
          {sections.map((sec, i) => (
            <div key={i} className="bg-card border border-border rounded-xl p-6">
              <h4 className="font-semibold text-sm text-primary uppercase mb-3">{sec.name}</h4>
              <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                {sec.content}
              </p>
            </div>
          ))}
          {isGenerating && steps.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-4 flex items-center gap-3">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">
                {steps[steps.length - 1]?.message}
              </span>
            </div>
          )}
        </div>

        {generatedPaper && (
          <div className="flex gap-2">
            <Button
              onClick={() => {
                setGeneratedPaper(null);
                setEvents([]);
                setStep(0);
              }}
              variant="outline"
            >
              Generate Another
            </Button>
          </div>
        )}
      </div>
    );
  }

  const stepTitles = ["Mode", "Configure", "Content", "Generate"];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
        <FileText className="h-8 w-8 text-primary" /> Paper Generation
      </h2>

      <div className="flex items-center gap-2">
        {stepTitles.map((t, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className={
                "w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold " +
                (i <= step ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground")
              }
            >
              {i + 1}
            </div>
            <span className={"text-xs " + (i <= step ? "text-foreground" : "text-muted-foreground")}>
              {t}
            </span>
            {i < stepTitles.length - 1 && <ChevronRight className="h-4 w-4 text-muted-foreground" />}
          </div>
        ))}
      </div>

      {step === 0 && (
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold">Select Generation Mode</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {[
              { key: "scratch" as const, label: "From Scratch", desc: "Start from a topic or keywords" },
              { key: "content" as const, label: "From Content", desc: "Use existing notes or drafts" },
              { key: "data" as const, label: "From Data", desc: "Generate from research data" },
            ].map(({ key, label, desc }) => (
              <button
                key={key}
                onClick={() => {
                  setMode(key);
                  setStep(1);
                }}
                className={
                  "p-4 rounded-lg border text-left transition-all " +
                  (mode === key
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50")
                }
              >
                <span className="font-medium text-foreground">{label}</span>
                <p className="text-xs text-muted-foreground mt-1">{desc}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold">Configure Paper</h3>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-muted-foreground font-mono mb-1 block">
                Topic / Title
              </label>
              <input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Attention Is All You Need"
                className="w-full bg-background border border-border px-3 py-2 rounded-md text-sm text-foreground placeholder:text-muted-foreground"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground font-mono mb-1 block">
                Keywords (comma separated)
              </label>
              <input
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="e.g. transformer, attention, NLP"
                className="w-full bg-background border border-border px-3 py-2 rounded-md text-sm text-foreground placeholder:text-muted-foreground"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-muted-foreground font-mono mb-1 block">
                  Paper Type
                </label>
                <select
                  value={paperType}
                  onChange={(e) => setPaperType(e.target.value)}
                  className="w-full bg-background border border-border px-3 py-2 rounded-md text-sm text-foreground"
                >
                  {PAPER_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t.replace(/_/g, " ")}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-muted-foreground font-mono mb-1 block">Domain</label>
                <select
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  className="w-full bg-background border border-border px-3 py-2 rounded-md text-sm text-foreground"
                >
                  {DOMAINS.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setStep(0)}>
              <ChevronLeft className="h-4 w-4 mr-1" /> Back
            </Button>
            <Button onClick={() => setStep(mode === "content" ? 2 : 3)} disabled={!topic.trim()}>
              {mode === "content" ? "Next" : "Generate"} <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {step === 2 && mode === "content" && (
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold">Provide Content</h3>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-muted-foreground font-mono mb-1 block">
                Upload Document (optional)
              </label>
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center relative hover:border-primary/50 transition-colors">
                <input
                  type="file"
                  onChange={handleUpload}
                  accept=".txt,.md,.pdf,.docx,.tex,.csv,.json"
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <FileUp className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Drop a file or click to upload</p>
              </div>
              {uploadedFile && (
                <div className="mt-2 bg-background border border-border rounded-lg p-3 text-sm">
                  <span className="font-medium text-foreground">{uploadedFile.filename}</span>
                  <span className="text-muted-foreground ml-2">
                    ({(uploadedFile.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
              )}
            </div>
            <div>
              <label className="text-xs text-muted-foreground font-mono mb-1 block">
                Notes / Draft Content
              </label>
              <textarea
                value={userContent}
                onChange={(e) => setUserContent(e.target.value)}
                placeholder="Paste or type your existing content, notes, or draft here..."
                rows={10}
                className="w-full bg-background border border-border px-3 py-2 rounded-md text-sm text-foreground placeholder:text-muted-foreground font-mono"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setStep(1)}>
              <ChevronLeft className="h-4 w-4 mr-1" /> Back
            </Button>
            <Button onClick={() => setStep(3)}>
              <Send className="h-4 w-4 mr-1" /> Generate
            </Button>
          </div>
        </div>
      )}

      {step === 3 && !isGenerating && !generatedPaper && (
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold flex items-center gap-2">
            <ListChecks className="h-5 w-5 text-primary" /> Review & Generate
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Topic</span>
              <span className="text-foreground">{topic}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Type</span>
              <span className="text-foreground">{paperType.replace(/_/g, " ")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Domain</span>
              <span className="text-foreground">{domain}</span>
            </div>
            {keywords && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Keywords</span>
                <span className="text-foreground">{keywords}</span>
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setStep(mode === "content" ? 2 : 1)}>
              <ChevronLeft className="h-4 w-4 mr-1" /> Back
            </Button>
            <Button onClick={handleGenerate} className="bg-primary">
              <Sparkles className="h-4 w-4 mr-1" /> Start Generation
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
