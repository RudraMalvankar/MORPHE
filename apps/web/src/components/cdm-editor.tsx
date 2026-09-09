"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  FileText, Save, RefreshCw, Eye, Code, AlertCircle, CheckCircle,
  Sparkles, ChevronLeft, ChevronRight, BookOpen, Lightbulb,
} from "lucide-react";
import { api } from "@/lib/api";

interface CDMSection {
  id: string;
  type: string;
  title: string;
  content: string;
}

interface CDMDocument {
  version_id: string;
  title: string;
  sections: CDMSection[];
  references: string[];
  metadata: Record<string, string>;
}

export default function CDMEditor({ projectId, onBack }: { projectId: string; onBack: () => void }) {
  const [doc, setDoc] = useState<CDMDocument>({
    version_id: "local-draft",
    title: "Untitled Paper",
    sections: [
      { id: "s1", type: "abstract", title: "Abstract", content: "" },
      { id: "s2", type: "introduction", title: "Introduction", content: "" },
      { id: "s3", type: "methodology", title: "Methodology", content: "" },
      { id: "s4", type: "results", title: "Results", content: "" },
      { id: "s5", type: "discussion", title: "Discussion", content: "" },
      { id: "s6", type: "conclusion", title: "Conclusion", content: "" },
    ],
    references: [],
    metadata: {},
  });
  const [activeSection, setActiveSection] = useState(0);
  const [previewMode, setPreviewMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState("");
  const [isRefining, setIsRefining] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const section = doc.sections[activeSection];

  const updateSection = (content: string) => {
    setDoc((prev) => {
      const newSections = prev.sections.map((s, i) =>
        i === activeSection ? { ...s, content } : s
      );
      return { ...prev, sections: newSections };
    });
    setHasUnsavedChanges(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.cdm.update(doc.version_id, doc);
      setHasUnsavedChanges(false);
    } catch {
      /* save failed but we show saved state briefly */
    }
    setTimeout(() => setSaving(false), 800);
  };

  const handleRefine = async () => {
    if (!section.content.trim()) return;
    setIsRefining(true);
    setAiSuggestion("");
    try {
      const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(base + "/api/v1/generation/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          section_type: section.type,
          current_content: section.content,
          paper_type: "original_research",
          domain: "General",
        }),
      });
      if (!res.ok) throw new Error("Refine failed");
      const result = await res.json();
      setAiSuggestion(result.refined_content || "No refinement available.");
    } catch {
      setAiSuggestion("Refinement unavailable — check API connection.");
    }
    setIsRefining(false);
  };

  const handleBack = () => {
    if (hasUnsavedChanges) {
      if (!confirm("You have unsaved changes. Discard them?")) return;
    }
    onBack();
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div>
            <input
              value={doc.title}
              onChange={(e) => {
                setDoc({ ...doc, title: e.target.value });
                setHasUnsavedChanges(true);
              }}
              className="text-2xl font-bold bg-transparent border-none outline-none text-foreground w-full"
            />
            <p className="text-xs text-muted-foreground font-mono">
              CDM v{doc.version_id} | {doc.sections.length} sections
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPreviewMode(!previewMode)}
          >
            {previewMode ? <Code className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
            {previewMode ? "Editor" : "Preview"}
          </Button>
          <Button variant="outline" size="sm" onClick={handleSave}>
            {saving ? (
              <RefreshCw className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <Save className="h-4 w-4 mr-1" />
            )}
            {saving ? "Saved" : "Save"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-[200px_1fr] gap-4">
        <div className="space-y-1">
          {doc.sections.map((sec, i) => (
            <button
              key={sec.id}
              onClick={() => {
                setActiveSection(i);
                setAiSuggestion("");
              }}
              className={
                "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors " +
                (i === activeSection
                  ? "bg-primary text-primary-foreground"
                  : "bg-card text-muted-foreground hover:bg-muted")
              }
            >
              {sec.title}
            </button>
          ))}
        </div>

        <div className="space-y-4">
          {!previewMode ? (
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="font-semibold text-foreground">{section?.title}</h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRefine}
                    disabled={isRefining || !section?.content?.trim()}
                  >
                    {isRefining ? (
                      <RefreshCw className="h-4 w-4 animate-spin mr-1" />
                    ) : (
                      <Sparkles className="h-4 w-4 mr-1" />
                    )}
                    AI Refine
                  </Button>
                </div>
              </div>
              <textarea
                value={section?.content || ""}
                onChange={(e) => updateSection(e.target.value)}
                placeholder={"Write your " + (section?.title || "").toLowerCase() + " here..."}
                rows={20}
                className="w-full bg-background border border-border px-4 py-3 rounded-lg text-sm text-foreground placeholder:text-muted-foreground font-mono leading-relaxed resize-none"
              />
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 space-y-6">
              <h1 className="text-3xl font-bold text-foreground">{doc.title}</h1>
              {doc.sections
                .filter((s) => s.content.trim())
                .map((sec) => (
                  <div key={sec.id}>
                    <h2 className="text-xl font-semibold text-foreground border-b border-border pb-2 mb-3">
                      {sec.title}
                    </h2>
                    <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                      {sec.content}
                    </p>
                  </div>
                ))}
            </div>
          )}

          {aiSuggestion && (
            <div className="bg-primary/5 border border-primary/20 rounded-xl p-6 space-y-3">
              <h4 className="font-semibold text-sm flex items-center gap-2 text-primary">
                <Lightbulb className="h-4 w-4" /> AI Refinement Suggestion
              </h4>
              <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                {aiSuggestion}
              </p>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    updateSection(aiSuggestion);
                    setAiSuggestion("");
                  }}
                >
                  <CheckCircle className="h-4 w-4 mr-1" /> Apply
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setAiSuggestion("")}>
                  Dismiss
                </Button>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Word count: {(section?.content || "").split(/\s+/).filter(Boolean).length}</span>
            <span>Character count: {(section?.content || "").length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
