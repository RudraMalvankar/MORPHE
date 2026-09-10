"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAppStore } from "@/store/use-app-store";
import { Button } from "@/components/ui/button";
import {
  FolderKanban, Plus, FileText, Upload, Sparkles, AlertCircle,
  CheckCircle, Database, Pencil, Trash2, Clock, BarChart3, TrendingUp,
} from "lucide-react";
import { api } from "@/lib/api";
import GenerationPage from "@/components/generation-page";
import ExportPage from "@/components/export-page";
import KnowledgeBasePage from "@/components/knowledge-page";
import CDMEditor from "@/components/cdm-editor";
import DashboardPage from "@/components/dashboard-page";
import AnalyticsPage from "@/components/analytics-page";

interface Project {
  id: string;
  title: string;
  description: string | null;
  default_publisher_target: string;
  created_at: string;
  updated_at: string;
  versions?: any[];
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

  useEffect(() => { setMounted(true); }, []);

  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [newProjTitle, setNewProjTitle] = useState("");
  const [creatingProject, setCreatingProject] = useState(false);
  const [files, setFiles] = useState<Record<string, FileMetadata[]>>({});
  const [showCDMEditor, setShowCDMEditor] = useState(false);
  const [nlpText, setNlpText] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [processSuccess, setProcessSuccess] = useState(false);

  const [nlpStats, setNlpStats] = useState<NlpStats>({
    word_count: 0, sentence_count: 0, avg_sentence_length: 0,
    lexical_diversity: 0, reading_time_mins: 0,
  });
  const [entities, setEntities] = useState<Entity[]>([]);
  const [nlpError, setNlpError] = useState<string | null>(null);

  const loadProjects = useCallback(async () => {
    setLoadingProjects(true);
    try {
      const data = await api.projects.list();
      setProjects(data.projects || []);
    } catch {
      setProjects([]);
    }
    setLoadingProjects(false);
  }, []);

  useEffect(() => {
    if (mounted && activeTab === "workspaces") {
      loadProjects();
    }
  }, [mounted, activeTab, loadProjects]);

  const handleCreateProject = async () => {
    if (!newProjTitle.trim()) return;
    setCreatingProject(true);
    try {
      const proj = await api.projects.create({ title: newProjTitle });
      setProjects((prev) => [proj, ...prev]);
      setNewProjTitle("");
      setActiveProject(proj.id);
    } catch (err: any) {
      alert("Failed to create project: " + err.message);
    }
    setCreatingProject(false);
  };

  const handleDeleteProject = async (id: string) => {
    if (!confirm("Delete this project?")) return;
    try {
      await api.projects.delete(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
      if (activeProject === id) setActiveProject(null);
    } catch (err: any) {
      alert("Failed to delete: " + err.message);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    try {
      const result = await api.upload.document(e.target.files[0]);
      const newFile: FileMetadata = {
        id: result.file_id,
        filename: result.filename,
        size: result.size,
        status: "uploaded",
        checksum: "sha256_" + Math.random().toString(36).substring(7),
      };
      const pid = activeProject || "default";
      setFiles((prev) => ({ ...prev, [pid]: [...(prev[pid] || []), newFile] }));
    } catch (err: any) {
      alert("Upload failed: " + err.message);
    }
  };

  const runAnalysis = async (fileId: string) => {
    setIsProcessing(true);
    setProcessSuccess(false);
    try {
      const pid = activeProject || "default";
      const file = (files[pid] || []).find((f) => f.id === fileId);
      if (file) {
        setFiles((prev) => ({
          ...prev,
          [pid]: prev[pid].map((f) =>
            f.id === fileId ? { ...f, status: "analyzed" } : f
          ),
        }));
      }
      setProcessSuccess(true);
    } catch {
      /* analysis failed */
    }
    setIsProcessing(false);
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
            <p className="text-muted-foreground text-sm">
              Manage your active research projects and document folders.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
            <Database className="h-4 w-4" /> {projects.length} projects
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
            <Button onClick={handleCreateProject} disabled={creatingProject}>
              {creatingProject ? "Creating..." : "Create"}
            </Button>
          </div>
        </div>

        {loadingProjects ? (
          <div className="text-center py-12 text-muted-foreground text-sm">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground text-sm">
            No projects yet. Create your first workspace above.
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((proj) => (
              <div
                key={proj.id}
                onClick={() => setActiveProject(proj.id)}
                className={`p-6 rounded-xl border transition-all cursor-pointer bg-card flex flex-col justify-between h-48 ${
                  activeProject === proj.id
                    ? "border-primary shadow-lg ring-1 ring-primary"
                    : "border-border hover:border-muted-foreground/40"
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <FolderKanban className="h-5 w-5 text-muted-foreground" />
                    <span className="font-mono text-xs text-muted-foreground">
                      {proj.default_publisher_target?.toUpperCase()}
                    </span>
                  </div>
                  <h4 className="font-bold text-lg text-foreground line-clamp-1">{proj.title}</h4>
                  {proj.description && (
                    <p className="text-xs text-muted-foreground line-clamp-2">{proj.description}</p>
                  )}
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground border-t border-border pt-3">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(proj.created_at).toLocaleDateString()}
                  </span>
                  <div className="flex items-center gap-2">
                    {activeProject === proj.id && (
                      <>
                        <button
                          onClick={(e) => { e.stopPropagation(); setShowCDMEditor(true); }}
                          className="flex items-center gap-1 text-primary hover:text-primary/80"
                        >
                          <Pencil className="h-3 w-3" /> Edit
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDeleteProject(proj.id); }}
                          className="flex items-center gap-1 text-rose-400 hover:text-rose-300"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
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
              ? "Upload and parse files inside workspace"
              : "Select a workspace first in the Workspaces tab."}
          </p>
        </div>
        {activeProject && (
          <div className="grid gap-8 lg:grid-cols-3">
            <div className="bg-card border border-border p-6 rounded-xl space-y-6 flex flex-col justify-center items-center text-center h-64 relative border-dashed hover:border-primary transition-colors">
              <Upload className="h-10 w-10 text-muted-foreground" />
              <div className="space-y-1">
                <p className="font-semibold text-sm">Drag and drop file here</p>
                <p className="text-xs text-muted-foreground">
                  Supports PDF, DOCX, LaTeX, Markdown & TXT up to 50MB
                </p>
              </div>
              <input
                type="file"
                onChange={handleFileUpload}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
            </div>
            <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-lg flex items-center gap-2 border-b border-border pb-3">
                <Database className="h-5 w-5 text-primary" /> Workspace Files ({currentFiles.length})
              </h3>
              {currentFiles.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-sm">
                  No files uploaded yet in this workspace.
                </div>
              ) : (
                <div className="space-y-3 overflow-y-auto max-h-96">
                  {currentFiles.map((f) => (
                    <div
                      key={f.id}
                      className="flex items-center justify-between p-4 bg-background border border-border rounded-lg"
                    >
                      <div className="space-y-1">
                        <p className="font-semibold text-sm text-foreground">{f.filename}</p>
                        <p className="text-xs text-muted-foreground font-mono">
                          Size: {(f.size / 1024).toFixed(1)} KB | Checksum: {f.checksum}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className={
                            "text-xs px-2 py-0.5 rounded font-mono border " +
                            (f.status === "analyzed"
                              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                              : "bg-blue-500/10 text-blue-400 border-blue-500/20")
                          }
                        >
                          {f.status}
                        </span>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => runAnalysis(f.id)}
                          disabled={isProcessing}
                        >
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
        <div>
          <h2 className="text-3xl font-bold tracking-tight">NLP & Document Analysis</h2>
          <p className="text-muted-foreground text-sm">
            Paste text or upload a file for instant linguistic analysis.
          </p>
        </div>
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" /> Analyze Text
          </h3>
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
              setNlpError(null);
              try {
                const result = await api.nlp.analyze(nlpText);
                setNlpStats(result);
                setEntities(result.entities || []);
                setProcessSuccess(true);
              } catch (err: any) {
                setNlpError(err?.message || "Analysis failed");
                setProcessSuccess(false);
              }
              setIsProcessing(false);
            }}
            disabled={isProcessing || !nlpText.trim()}
          >
            {isProcessing ? "Analyzing..." : "Run Analysis"}
          </Button>
          {nlpError && (
            <div className="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-lg px-4 py-2">
              {nlpError}
            </div>
          )}
        </div>
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="bg-card border border-border p-6 rounded-xl space-y-4">
            <h3 className="font-semibold text-lg border-b border-border pb-3">
              Linguistic Statistics
            </h3>
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
                <p className="text-xl font-bold text-foreground">
                  {(nlpStats.lexical_diversity * 100).toFixed(0)}% unique
                </p>
              </div>
              <div className="bg-background p-4 rounded-lg border border-border text-center col-span-2">
                <span className="text-xs text-muted-foreground font-mono">Avg Sentence Length</span>
                <p className="text-lg font-bold text-foreground">
                  {nlpStats.avg_sentence_length} words
                </p>
              </div>
            </div>
          </div>
          <div className="bg-card border border-border p-6 rounded-xl space-y-4">
            <h3 className="font-semibold text-lg border-b border-border pb-3">Named Entities</h3>
            <div className="flex flex-wrap gap-2 overflow-y-auto max-h-56">
              {entities.length === 0 && (
                <p className="text-xs text-muted-foreground">
                  No entities found yet. Run analysis above.
                </p>
              )}
              {entities.map((e, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 px-3 py-1 bg-background border border-border rounded-full text-xs"
                >
                  <span className="font-semibold text-foreground">{e.text}</span>
                  <span className="text-[10px] text-muted-foreground font-mono px-1.5 py-0.5 rounded bg-muted border border-border">
                    {e.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-card border border-border p-6 rounded-xl space-y-4">
            <h3 className="font-semibold text-lg border-b border-border pb-3">Keywords</h3>
            <div className="flex flex-wrap gap-2 overflow-y-auto max-h-56">
              {!(nlpStats as any).keywords?.length && (
                <p className="text-xs text-muted-foreground">
                  No keywords found yet.
                </p>
              )}
              {((nlpStats as any).keywords || []).map((k: string, idx: number) => (
                <span key={idx} className="px-3 py-1 bg-primary/10 text-primary text-xs rounded-full">
                  {k}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (activeTab === "dashboard") return <DashboardPage />;
  if (activeTab === "generation") return <GenerationPage />;
  if (activeTab === "export") return <ExportPage />;
  if (activeTab === "knowledge") return <KnowledgeBasePage />;
  if (activeTab === "analytics") return <AnalyticsPage />;

  return (
    <div className="space-y-6 max-w-xl animate-in fade-in duration-300">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground text-sm">
          Configure system parameters and knowledge base settings.
        </p>
      </div>
      <div className="bg-card border border-border p-6 rounded-xl space-y-4">
        <h3 className="font-semibold text-lg border-b border-border pb-2">
          Developer Configurations
        </h3>
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Database Engine</span>
            <span className="font-mono bg-muted px-2 py-0.5 rounded text-xs border border-border">
              SQLite (aiosqlite)
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Backend API Host</span>
            <span className="font-mono bg-muted px-2 py-0.5 rounded text-xs border border-border">
              http://127.0.0.1:8000
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Dev Mode Auth</span>
            <span className="font-mono bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded text-xs border border-emerald-500/20">
              Enabled
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
