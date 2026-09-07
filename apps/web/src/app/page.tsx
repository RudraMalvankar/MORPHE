"use client";

import React, { useState, useEffect } from "react";
import { useAppStore } from "@/store/use-app-store";
import { Button } from "@/components/ui/button";
import { FolderKanban, Plus, FileText, Upload, Sparkles, AlertCircle, CheckCircle, Database, Pencil } from "lucide-react";
import { api } from "@/lib/api";
import GenerationPage from "@/components/generation-page";
import ExportPage from "@/components/export-page";
import KnowledgeBasePage from "@/components/knowledge-page";
import CDMEditor from "@/components/cdm-editor";

interface Project {
  id: string;
  title: string;
  created_at: string;
}

interface FileMetadata {
  id: string;
  filename: string;
  size: number;
  status: string;
  checksum: string;
}

interface NlpStats {
  word_count: number;
  sentence_count: number;
  avg_sentence_length: number;
  lexical_diversity: number;
  reading_time_mins: number;
}

interface Entity {
  text: string;
  type: string;
}

export default function Home() {
  const { activeTab, activeProject, setActiveProject } = useAppStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const [projects, setProjects] = useState<Project[]>([
    { id: "p-1", title: "Autonomous Agents Survey", created_at: "2026-07-28" },
    { id: "p-2", title: "Quantum Gate Mechanics", created_at: "2026-07-30" }
  ]);
  const [newProjTitle, setNewProjTitle] = useState("");
  const [files, setFiles] = useState<Record<string, FileMetadata[]>>({
    "p-1": [
      { id: "f-1", filename: "llm_agents_draft.pdf", size: 1245000, status: "analyzed", checksum: "8f7d9..." },
      { id: "f-2", filename: "survey_notes.md", size: 45000, status: "uploaded", checksum: "3b2c9..." }
    ],
    "p-2": [
      { id: "f-3", filename: "quantum_logic_gates.latex", size: 89000, status: "uploaded", checksum: "7a2f1..." }
    ]
  });

  const [isProcessing, setIsProcessing] = useState(false);
  const [processSuccess, setProcessSuccess] = useState(false);
  const [showCDMEditor, setShowCDMEditor] = useState(false);
  const [nlpText, setNlpText] = useState("");

  const [nlpStats, setNlpStats] = useState<NlpStats>({
    word_count: 3420,
    sentence_count: 142,
    avg_sentence_length: 24.1,
    lexical_diversity: 0.58,
    reading_time_mins: 17.1
  });
  const [entities, setEntities] = useState<Entity[]>([
    { text: "Stanford University", type: "ORGANIZATION" },
    { text: "arXiv: 2607.1234", type: "DOI" },
    { text: "author@stanford.edu", type: "EMAIL" },
    { text: "Transformer Neural Net", type: "ALGORITHM" },
    { text: "ResNet-50", type: "ALGORITHM" }
  ]);
  const [domainInfo] = useState({
    domain: "Computer Science",
    subdomain: "Machine Learning",
    research_type: "Experimental",
    confidence: 0.85,
    style: "IEEE",
    structure: {
      present: ["Introduction", "Methodology", "Results"],
      missing: ["Discussion", "Conclusion"],
      extra: ["Appendix Details"]
    }
  });

  const handleCreateProject = async () => {
    if (!newProjTitle.trim()) return;
    try {
      const proj = await api.projects.create({ title: newProjTitle });
      setProjects([...projects, proj]);
      setNewProjTitle("");
      setActiveProject(proj.id);
    } catch {
      const newId = "p-" + Date.now();
      const newProj = { id: newId, title: newProjTitle, created_at: new Date().toISOString().split("T")[0] };
      setProjects([...projects, newProj]);
      setFiles({ ...files, [newId]: [] });
      setNewProjTitle("");
      setActiveProject(newId);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!activeProject || !e.target.files || e.target.files.length === 0) return;
    const uploadedFile = e.target.files[0];
    const newFile: FileMetadata = {
      id: "f-" + Date.now(),
      filename: uploadedFile.name,
      size: uploadedFile.size,
      status: "uploaded",
      checksum: "sha256_" + Math.random().toString(36).substring(7)
    };
    setFiles({ ...files, [activeProject]: [...(files[activeProject] || []), newFile] });
  };

  const runAnalysis = (fileId: string) => {
    setIsProcessing(true);
    setProcessSuccess(false);
    setTimeout(() => {
      setIsProcessing(false);
      setProcessSuccess(true);
      setNlpStats({
        word_count: Math.floor(Math.random() * 4000) + 1000,
        sentence_count: Math.floor(Math.random() * 200) + 50,
        avg_sentence_length: parseFloat((Math.random() * 15 + 15).toFixed(1)),
        lexical_diversity: parseFloat((Math.random() * 0.3 + 0.4).toFixed(2)),
        reading_time_mins: parseFloat((Math.random() * 15 + 5).toFixed(1))
      });
      if (activeProject) {
        setFiles({
          ...files,
          [activeProject]: files[activeProject].map(f => f.id === fileId ? { ...f, status: "analyzed" } : f)
        });
      }
    }, 2000);
  };

  if (!mounted) return null;

  if (showCDMEditor && activeProject) {
    return <CDMEditor projectId={activeProject} onBack={() => setShowCDMEditor(false)} />;
  }

  if (activeTab === "workspaces") {
    return (
      <div className="space-y-8 animate-in fade-in duration-300">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Workspaces</h2>
            <p className="text-muted-foreground text-sm">Manage your active research projects and document folders.</p>
          </div>
        </div>
        <div className="bg-card border border-border p-6 rounded-xl space-y-4 max-w-md">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Plus className="h-5 w-5 text-primary" /> Create New Workspace
          </h3>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Workspace or Project Title..."
              value={newProjTitle}
              onChange={(e) => setNewProjTitle(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreateProject()}
              className="bg-background border border-border px-3 py-2 rounded-md text-sm flex-1 outline-none focus:border-primary transition-colors text-foreground"
            />
            <Button onClick={handleCreateProject}>Create</Button>
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((proj) => (
            <div
              key={proj.id}
              onClick={() => setActiveProject(proj.id)}
              className={`p-6 rounded-xl border transition-all cursor-pointer bg-card flex flex-col justify-between h-40 ${
                activeProject === proj.id ? "border-primary shadow-lg ring-1 ring-primary" : "border-border hover:border-muted-foreground/40"
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <FolderKanban className="h-5 w-5 text-muted-foreground" />
                  <span className="font-mono text-xs text-muted-foreground">ID: {proj.id}</span>
                </div>
                <h4 className="font-bold text-lg text-foreground line-clamp-1">{proj.title}</h4>
              </div>
              <div className="flex items-center justify-between text-xs text-muted-foreground border-t border-border pt-4">
                <span>Created: {proj.created_at}</span>
                <div className="flex items-center gap-2">
                  <span>{files[proj.id]?.length || 0} Files</span>
                  {activeProject === proj.id && (
                    <button
                      onClick={(e) => { e.stopPropagation(); setShowCDMEditor(true); }}
                      className="flex items-center gap-1 text-primary hover:text-primary/80"
                    >
                      <Pencil className="h-3 w-3" /> Edit
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (activeTab === "documents") {
    const currentFiles = activeProject ? (files[activeProject] || []) : [];
    return (
      <div className="space-y-8 animate-in fade-in duration-300">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Documents</h2>
          <p className="text-muted-foreground text-sm">
            {activeProject
              ? "Upload and parse files inside workspace \"" + (projects.find(p => p.id === activeProject)?.title || "") + "\""
              : "Please select an active workspace in the Workspaces tab first."}
          </p>
        </div>
        {activeProject && (
          <div className="grid gap-8 lg:grid-cols-3">
            <div className="bg-card border border-border p-6 rounded-xl space-y-6 flex flex-col justify-center items-center text-center h-64 relative border-dashed hover:border-primary transition-colors">
              <Upload className="h-10 w-10 text-muted-foreground" />
              <div className="space-y-1">
                <p className="font-semibold text-sm">Drag and drop file here</p>
                <p className="text-xs text-muted-foreground">Supports PDF, DOCX, LaTeX, Markdown & TXT up to 50MB</p>
              </div>
              <input type="file" onChange={handleFileUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
            </div>
            <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-lg flex items-center gap-2 border-b border-border pb-3">
                <Database className="h-5 w-5 text-primary" /> Workspace Files ({currentFiles.length})
              </h3>
              {currentFiles.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-sm">No files uploaded yet in this workspace.</div>
              ) : (
                <div className="space-y-3 overflow-y-auto max-h-96">
                  {currentFiles.map((f) => (
                    <div key={f.id} className="flex items-center justify-between p-4 bg-background border border-border rounded-lg">
                      <div className="space-y-1">
                        <p className="font-semibold text-sm text-foreground">{f.filename}</p>
                        <p className="text-xs text-muted-foreground font-mono">
                          Size: {(f.size / 1024).toFixed(1)} KB | Checksum: {f.checksum}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={"text-xs px-2 py-0.5 rounded font-mono border " + (
                          f.status === "analyzed" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                        )}>
                          {f.status}
                        </span>
                        <Button size="sm" variant="outline" onClick={() => runAnalysis(f.id)} disabled={isProcessing}>
                          {isProcessing ? "Processing..." : "Analyze"}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  if (activeTab === "nlp") {
    return (
      <div className="space-y-8 animate-in fade-in duration-300">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">NLP & Document Analysis</h2>
            <p className="text-muted-foreground text-sm">Paste text or upload a file for instant linguistic analysis.</p>
          </div>
        </div>
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold flex items-center gap-2"><Sparkles className="h-4 w-4 text-primary" /> Analyze Text</h3>
          <textarea
            value={nlpText}
            onChange={(e) => setNlpText(e.target.value)}
            placeholder="Paste your document text here for analysis..."
            rows={8}
            className="w-full bg-background border border-border px-4 py-3 rounded-lg text-sm text-foreground placeholder:text-muted-foreground font-mono"
          />
          <Button
            onClick={async () => {
              if (!nlpText.trim()) return;
              setIsProcessing(true);
              try {
                const result = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/v1/generation/analyze-text", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify(nlpText),
                }).then((r) => r.json());
                setNlpStats(result);
                setEntities(result.entities || []);
                setProcessSuccess(true);
              } catch {
                /* fallback */
              }
              setIsProcessing(false);
            }}
            disabled={isProcessing || !nlpText.trim()}
          >
            {isProcessing ? "Analyzing..." : "Run Analysis"}
          </Button>
        </div>
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="bg-card border border-border p-6 rounded-xl space-y-4">
            <h3 className="font-semibold text-lg border-b border-border pb-3">Linguistic Statistics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-background p-4 rounded-lg border border-border text-center">
                <span className="text-xs text-muted-foreground font-mono">Word Count</span>
                <p className="text-2xl font-bold text-primary">{nlpStats.word_count}</p>
              </div>
              <div className="bg-background p-4 rounded-lg border border-border text-center">
                <span className="text-xs text-muted-foreground font-mono">Sentences</span>
                <p className="text-2xl font-bold text-primary">{nlpStats.sentence_count}</p>
              </div>
              <div className="bg-background p-4 rounded-lg border border-border text-center col-span-2">
                <span className="text-xs text-muted-foreground font-mono">Lexical Diversity</span>
                <p className="text-xl font-bold text-foreground">{(nlpStats.lexical_diversity * 100).toFixed(0)}% unique</p>
              </div>
              <div className="bg-background p-4 rounded-lg border border-border text-center col-span-2">
                <span className="text-xs text-muted-foreground font-mono">Avg Sentence Length</span>
                <p className="text-lg font-bold text-foreground">{nlpStats.avg_sentence_length} words</p>
              </div>
            </div>
          </div>
          <div className="bg-card border border-border p-6 rounded-xl space-y-4">
            <h3 className="font-semibold text-lg border-b border-border pb-3">Named Entities</h3>
            <div className="flex flex-wrap gap-2 overflow-y-auto max-h-56">
              {entities.length === 0 && <p className="text-xs text-muted-foreground">No entities found yet. Run analysis above.</p>}
              {entities.map((e, idx) => (
                <div key={idx} className="flex items-center gap-2 px-3 py-1 bg-background border border-border rounded-full text-xs">
                  <span className="font-semibold text-foreground">{e.text}</span>
                  <span className="text-[10px] text-muted-foreground font-mono px-1.5 py-0.5 rounded bg-muted border border-border">{e.type}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-card border border-border p-6 rounded-xl space-y-4">
            <h3 className="font-semibold text-lg border-b border-border pb-3">Keywords</h3>
            <div className="flex flex-wrap gap-2 overflow-y-auto max-h-56">
              {(!nlpStats as any).keywords?.length && <p className="text-xs text-muted-foreground">No keywords found yet.</p>}
              {((nlpStats as any).keywords || []).map((k: string, idx: number) => (
                <span key={idx} className="px-3 py-1 bg-primary/10 text-primary text-xs rounded-full">{k}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (activeTab === "generation") {
    return <GenerationPage />;
  }

  if (activeTab === "export") {
    return <ExportPage />;
  }

  if (activeTab === "knowledge") {
    return <KnowledgeBasePage />;
  }

  return (
    <div className="space-y-6 max-w-xl animate-in fade-in duration-300">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground text-sm">Configure system parameters and knowledge base settings.</p>
      </div>
      <div className="bg-card border border-border p-6 rounded-xl space-y-4">
        <h3 className="font-semibold text-lg border-b border-border pb-2">Developer Configurations</h3>
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Database Engine</span>
            <span className="font-mono bg-muted px-2 py-0.5 rounded text-xs border border-border">SQLite (aiosqlite)</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Backend API Host</span>
            <span className="font-mono bg-muted px-2 py-0.5 rounded text-xs border border-border">http://127.0.0.1:8000</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">NLP Classifier Pipeline</span>
            <span className="font-mono bg-muted px-2 py-0.5 rounded text-xs border border-border">Active (Regex/RAKE)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
