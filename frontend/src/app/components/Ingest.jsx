'use client'

import { useState } from "react";
import { Field, FieldDescription, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Upload, FileText, ShieldAlert, Zap, ArrowRight, Info, CheckCircle2 } from 'lucide-react'

export default function Ingest() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [debug, setDebug] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisReport, setAnalysisReport] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a document first.");

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const url = debug
        ? `${API_BASE_URL}/api/ingest/upload?debug=true`
        : `${API_BASE_URL}/api/ingest/upload`;

      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!result || !result.document_id) return;

    setAnalysisLoading(true);
    setAnalysisReport(null);

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${API_BASE_URL}/api/analytics/compare/${result.document_id}`, {
        method: "POST",
      });

      if (!res.ok) throw new Error("Analysis failed");

      const data = await res.json();
      setAnalysisReport(data.report);
    } catch (err) {
      setError(`Analysis Error: ${err.message}`);
    } finally {
      setAnalysisLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {!result ? (
        <div className="glass-card p-12 border-2 border-dashed border-white/10 hover:border-leagle-accent/50 transition-all group relative overflow-hidden text-center space-y-8">
          <div className="absolute inset-0 bg-leagle-accent/5 opacity-0 group-hover:opacity-100 transition-opacity blur-3xl rounded-full scale-150" />

          <div className="relative z-10">
            <div className="w-16 h-16 bg-white/2 rounded-sm flex items-center justify-center text-3xl mx-auto border border-white/5 mb-6 group-hover:border-leagle-accent/30 transition-all">
              {loading ? '⏳' : '📥'}
            </div>
            <div>
              <h3 className="text-3xl font-serif text-white tracking-tight italic">Diagnostic Ingestion</h3>
              <p className="text-gray-500 mt-2 font-medium max-w-sm mx-auto text-[10px] uppercase tracking-widest">Aggregate & Indexed Jurisdictional Artifacts</p>
            </div>
          </div>

          <div className="relative z-10 flex flex-col items-center gap-4">
            <Input
              id="pdf-upload"
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              disabled={loading}
              className="hidden"
            />
            <label
              htmlFor="pdf-upload"
              className={`bg-leagle-accent text-black font-black text-[10px] tracking-[0.2em] uppercase px-10 py-4 rounded-sm cursor-pointer inline-flex items-center gap-3 hover:bg-white transition-all shadow-xl ${loading ? 'opacity-50 pointer-events-none' : ''}`}
            >
              <Upload size={18} />
              {file ? file.name : 'Select PDF Portfolio'}
            </label>

            {file && !loading && (
              <button onClick={handleUpload} className="text-leagle-accent font-black uppercase tracking-widest text-[10px] hover:underline underline-offset-4 animate-bounce">
                Start Ingestion
              </button>
            )}
          </div>

          <div className="relative z-10 flex items-center justify-center gap-6 pt-4">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={debug}
                onChange={(e) => setDebug(e.target.checked)}
                disabled={loading}
                className="w-4 h-4 rounded border-white/10 bg-white/5 text-leagle-accent focus:ring-leagle-accent"
              />
              <span className="text-[10px] uppercase font-black text-gray-500 tracking-widest">Enhanced Debug Stream</span>
            </label>
          </div>
        </div>
      ) : (
        <div className="space-y-10">
          {/* SUCCESS HEADER */}
          <div className="glass-card p-8 bg-white/2 border-leagle-accent/10 flex flex-col md:flex-row md:items-center justify-between gap-6 rounded-sm">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 bg-leagle-accent/5 rounded-sm border border-leagle-accent/20 flex items-center justify-center text-leagle-accent">
                <CheckCircle2 size={30} />
              </div>
              <div>
                <h3 className="text-2xl font-serif text-white italic italic">Ingestion Complete</h3>
                <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Record ID: <span className="font-mono">{result.document_id}</span></p>
              </div>
            </div>

            {!analysisReport && (
              <button
                onClick={handleRunAnalysis}
                disabled={analysisLoading}
                className="btn-premium px-8 py-4 text-sm tracking-tighter"
              >
                {analysisLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Running analysis...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Zap size={18} className="fill-white" />
                    Run Compliance Analysis
                  </span>
                )}
              </button>
            )}
          </div>

          {/* STATS GRID */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { label: "File Mass", value: `${result.pipeline_stats.file_size_mb} MB`, icon: <FileText size={14} /> },
              { label: "Text Chunks", value: result.pipeline_stats.num_chunks, icon: <Zap size={14} /> },
              { label: "Embeddings", value: result.pipeline_stats.num_embeddings, icon: <ArrowRight size={14} /> },
              { label: "Strategy", value: result.pipeline_stats.chunking_strategy, icon: <Info size={14} /> },
            ].map((stat, i) => (
              <div key={i} className="glass-card p-6 bg-white/2 rounded-sm border-white/5">
                <div className="flex items-center gap-2 text-gray-500 mb-2 font-black uppercase tracking-widest text-[9px]">
                  {stat.icon}
                  {stat.label}
                </div>
                <p className="text-xl font-serif text-white italic">{stat.value}</p>
              </div>
            ))}
          </div>

          {/* GAP REPORT */}
          {analysisReport && (
            <div className="space-y-10 animate-in zoom-in-95 duration-500">
              {/* HOLISTIC DETERMINATION */}
              {analysisReport.comprehensive_synthesis && (
                <div className="glass-card border-none bg-gradient-to-br from-[#1e1b4b] to-[#030617] p-12 relative overflow-hidden backdrop-blur-3xl shadow-[0_0_100px_rgba(56,189,248,0.05)]">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-leagle-accent to-transparent opacity-50" />

                  <div className="relative z-10 space-y-10">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <h4 className="text-3xl font-serif text-white italic tracking-tight underline decoration-leagle-accent/30 underline-offset-8">Compliance Determination</h4>
                        <p className="text-leagle-accent text-[10px] font-black uppercase tracking-[0.2em] mt-2">Executive Audit Result</p>
                      </div>
                      <div className={`px-6 py-3 rounded-sm text-sm font-black border tracking-widest ${analysisReport.comprehensive_synthesis.overall_compliance_status === "COMPLIANT" ? "bg-green-500/10 border-green-500/30 text-green-400" :
                        analysisReport.comprehensive_synthesis.overall_compliance_status === "PARTIALLY_COMPLIANT" ? "bg-yellow-500/10 border-yellow-500/30 text-yellow-400" :
                          "bg-red-500/10 border-red-500/30 text-red-500"
                        }`}>
                        {analysisReport.comprehensive_synthesis.overall_compliance_status}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                      <div className="lg:col-span-2 space-y-8">
                        <div className="prose prose-invert max-w-none">
                          <p className="text-xl text-gray-300 leading-relaxed font-serif italic border-l-2 border-leagle-accent/30 pl-8 bg-white/2 py-4">
                            {analysisReport.comprehensive_synthesis.executive_summary}
                          </p>
                        </div>

                        <div className="space-y-4">
                          <h5 className="text-xs font-black uppercase tracking-widest text-red-500 flex items-center gap-2">
                            <ShieldAlert size={14} /> Critical Findings
                          </h5>
                          <div className="grid gap-4">
                            {analysisReport.comprehensive_synthesis.critical_issues?.map((issue, idx) => (
                              <div key={idx} className="p-6 bg-red-500/5 border border-red-500/20 rounded-3xl space-y-2">
                                <p className="text-lg font-black text-gray-100">{issue.issue}</p>
                                <p className="text-sm text-red-400/80 font-medium">Exposure: {issue.legal_exposure}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="space-y-8">
                        <div className="p-8 bg-leagle-accent/5 border border-leagle-accent/10 rounded-3xl text-center space-y-4">
                          <p className="text-[10px] font-black uppercase tracking-widest text-leagle-accent">Audit Score</p>
                          <p className="text-6xl font-black text-white tracking-tighter">
                            {analysisReport.comprehensive_synthesis.compliance_score}%
                          </p>
                          <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-leagle-accent h-full shadow-[0_0_10px_#38bdf8]" style={{ width: `${analysisReport.comprehensive_synthesis.compliance_score}%` }} />
                          </div>
                        </div>

                        <div className="space-y-4">
                          <h5 className="text-[10px] font-black uppercase tracking-widest text-gray-500">Immediate Actions</h5>
                          <div className="space-y-2">
                            {analysisReport.comprehensive_synthesis.immediate_actions?.map((action, idx) => (
                              <div key={idx} className="p-4 bg-white/2 border border-white/5 rounded-2xl flex gap-3 items-start">
                                <div className="w-5 h-5 rounded-lg bg-leagle-accent text-[10px] flex items-center justify-center font-black text-black mt-0.5">
                                  {action.priority}
                                </div>
                                <p className="text-xs font-medium text-gray-300">{action.action}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* DETAIL LIST */}
              <div className="space-y-6">
                <h4 className="text-xl font-black text-white px-2">Document Findings</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysisReport.findings.map((finding, idx) => (
                    <div key={idx} className="glass-card p-6 bg-white/2 group hover:bg-white/5 transition-all">
                      <div className="flex items-center justify-between mb-4">
                        <span className={`px-2 py-1 rounded text-[9px] font-black tracking-widest uppercase ${finding.risk_impact === "HIGH" ? "bg-red-500/20 text-red-400" :
                          finding.risk_impact === "MEDIUM" ? "bg-orange-500/20 text-orange-400" :
                            "bg-green-500/20 text-green-400"
                          }`}>
                          {finding.risk_impact} Severity
                        </span>
                        <span className="text-[9px] font-mono text-gray-500">#{idx + 1}</span>
                      </div>
                      <p className="text-sm font-bold text-gray-200 mb-2 leading-tight">{finding.alignment_summary}</p>
                      <ul className="text-xs text-red-400/80 space-y-1 mb-4">
                        {finding.specific_gaps.map((gap, gIdx) => (
                          <li key={gIdx} className="flex gap-2">
                            <span>•</span>
                            {gap}
                          </li>
                        ))}
                      </ul>
                      <div className="pt-4 border-t border-white/5 flex flex-wrap gap-2">
                        {finding.matched_regulations.map((reg, rIdx) => (
                          <span key={rIdx} className="px-2 py-1 bg-white/5 rounded text-[8px] font-bold text-leagle-accent uppercase border border-white/5">
                            {reg}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-3xl text-center">
              <p className="text-red-500 font-bold">🚨 {error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}