"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Download, CheckCircle, Loader2,
  Eye, Globe
} from "lucide-react";

const API_URL = "http://localhost:8000/api/v1";

export default function ExportPage() {
  const [publishers, setPublishers] = useState<any[]>([]);
  const [formats, setFormats] = useState<any[]>([]);
  const [selectedPublisher, setSelectedPublisher] = useState("ieee");
  const [selectedFormat, setSelectedFormat] = useState("html");
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(API_URL + "/export/publishers").then(r => r.json()).then(setPublishers);
    fetch(API_URL + "/export/formats").then(r => r.json()).then(d => setFormats(d));
  }, []);

  const sampleCdm = {
    title: "Sample Research Paper: AI in Healthcare",
    authors: ["John Doe", "Jane Smith"],
    abstract: "This paper explores the application of artificial intelligence in modern healthcare systems.",
    sections: [
      { heading: "Introduction", content: "The integration of AI in healthcare has shown remarkable promise in recent years." },
      { heading: "Methods", content: "We conducted a systematic review of 150 peer-reviewed publications from 2020-2025." },
      { heading: "Results", content: "AI-assisted diagnostics achieved an average accuracy of 94.3%, compared to 87.6% for traditional methods." },
      { heading: "Discussion", content: "AI tools can significantly enhance diagnostic capabilities when used as adjuncts to clinical judgment." },
      { heading: "Conclusion", content: "AI-assisted diagnostic tools demonstrate substantial potential for improving healthcare outcomes." }
    ],
    references: [
      { authors: ["Smith, J.", "Johnson, A."], title: "AI in Modern Medicine", journal: "Nature Medicine", year: "2024", volume: "30", issue: "2", pages: "123-145" },
      { authors: ["Williams, B.", "Chen, L."], title: "Machine Learning for Diagnostics", journal: "The Lancet", year: "2023", volume: "401", issue: "10278", pages: "567-578" }
    ],
    keywords: ["artificial intelligence", "healthcare", "diagnostics", "machine learning"]
  };

  const handlePreview = async () => {
    setLoading(true);
    try {
      const res = await fetch(API_URL + "/export/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          publisher_key: selectedPublisher,
          format: selectedFormat,
          cdm: sampleCdm,
        }),
      });
      const data = await res.json();
      setPreview(data.html || data.latex || data.docx_xml || data.typst || "");
    } catch (e) {
      setPreview("Error loading preview");
    } finally {
      setLoading(false);
    }
  };

  const getPublisherInfo = (key: string) => publishers.find(p => p.key === key);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div>
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Download className="h-8 w-8 text-primary" />
          Export Engine
        </h2>
        <p className="text-muted-foreground text-sm mt-1">
          Export papers in PDF, LaTeX, DOCX, or HTML with 25 publisher templates.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">Export Settings</h3>

          <div>
            <label className="text-xs text-muted-foreground font-mono">Publisher</label>
            <select
              value={selectedPublisher}
              onChange={(e) => setSelectedPublisher(e.target.value)}
              className="w-full mt-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground"
            >
              {publishers.map((p) => (
                <option key={p.key} value={p.key}>{p.name}</option>
              ))}
            </select>
          </div>

          {getPublisherInfo(selectedPublisher) && (
            <div className="bg-background border border-border rounded-lg p-3 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">LaTeX Class</span>
                <span className="font-mono text-foreground">{getPublisherInfo(selectedPublisher).latex_class}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Citation</span>
                <span className="font-mono text-foreground">{getPublisherInfo(selectedPublisher).citation_style}</span>
              </div>
            </div>
          )}

          <div>
            <label className="text-xs text-muted-foreground font-mono">Format</label>
            <div className="grid grid-cols-2 gap-2 mt-1">
              {formats.map((f) => (
                <button
                  key={f.format}
                  onClick={() => setSelectedFormat(f.format)}
                  className={`p-3 rounded-lg border text-xs font-medium transition-colors text-left ${
                    selectedFormat === f.format
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-card text-muted-foreground border-border hover:border-primary/50"
                  }`}
                >
                  <div>{f.name}</div>
                  <div className="text-[10px] opacity-70">{f.description}</div>
                </button>
              ))}
            </div>
          </div>

          <Button onClick={handlePreview} disabled={loading} className="w-full">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
            {loading ? "Generating..." : "Preview Export"}
          </Button>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">
            All Publishers ({publishers.length})
          </h3>
          <div className="space-y-2 max-h-[500px] overflow-y-auto">
            {publishers.map((p) => (
              <div
                key={p.key}
                onClick={() => setSelectedPublisher(p.key)}
                className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                  selectedPublisher === p.key
                    ? "bg-primary/10 border-primary"
                    : "bg-background border-border hover:border-muted-foreground/40"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm text-foreground">{p.name}</span>
                  {selectedPublisher === p.key && <CheckCircle className="h-4 w-4 text-primary" />}
                </div>
                <div className="flex gap-2 mt-1">
                  <span className="text-[10px] font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                    {p.latex_class}
                  </span>
                  <span className="text-[10px] font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                    {p.citation_style}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-lg border-b border-border pb-3">
            Preview ({selectedFormat.toUpperCase()})
          </h3>
          {preview ? (
            <div className="max-h-[500px] overflow-y-auto">
              {selectedFormat === "html" ? (
                <div dangerouslySetInnerHTML={{ __html: preview }} className="prose prose-sm dark:prose-invert max-w-none" />
              ) : (
                <pre className="text-xs text-muted-foreground font-mono whitespace-pre-wrap bg-background border border-border rounded-lg p-4">
                  {preview.substring(0, 3000)}
                  {preview.length > 3000 && "\n\n... (truncated)"}
                </pre>
              )}
            </div>
          ) : (
            <div className="text-center py-16 text-muted-foreground">
              <Globe className="h-12 w-12 mx-auto mb-4 opacity-30" />
              <p className="text-sm">Click &quot;Preview&quot; to see the export output.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
