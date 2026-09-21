"use client"

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { getRegulations, getPolicies, analyzeImpact } from '../api/client'
import { Target, Shield, FileText, Zap, Loader2, CheckCircle2, AlertTriangle, ArrowRight, ChevronRight, Clock, User } from 'lucide-react'

export default function ImpactAnalysis() {
    const [regulations, setRegulations] = useState([])
    const [policies, setPolicies] = useState([])
    const [selectedReg, setSelectedReg] = useState(null)
    const [selectedPolicy, setSelectedPolicy] = useState(null)
    const [loading, setLoading] = useState(false)
    const [dataLoading, setDataLoading] = useState(true)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        async function fetchData() {
            try {
                const [regRes, polRes] = await Promise.all([
                    getRegulations(),
                    getPolicies()
                ])
                setRegulations(regRes.data)
                setPolicies(polRes.data)
            } catch (err) {
                console.error("Failed to fetch data:", err)
                setError("Failed to load regulations and policies. Please ensure the backend is running.")
            } finally {
                setDataLoading(false)
            }
        }
        fetchData()
    }, [])

    const handleRunAnalysis = async () => {
        if (!selectedReg || !selectedPolicy) return

        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const res = await analyzeImpact(selectedReg.id, selectedPolicy.id)
            setResult(res.data)
        } catch (err) {
            console.error("Impact Analysis failed:", err)
            setError("Analysis failed. This usually happens if the LLM provider is busy or the document content is missing.")
        } finally {
            setLoading(false)
        }
    }

    if (dataLoading) return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
            <Loader2 className="w-8 h-8 sm:w-10 sm:h-10 text-leagle-accent animate-spin" />
            <p className="text-gray-500 font-bold tracking-widest uppercase text-[10px] text-center">Synchronizing Selection Hub...</p>
        </div>
    )

    return (
        <div className="max-w-6xl mx-auto space-y-8 sm:space-y-10 pb-20 px-2 sm:px-0">
            {/* Header */}
            <header className="space-y-2 text-center md:text-left">
                <div className="flex items-center justify-center md:justify-start gap-2">
                    <Target className="text-leagle-accent" size={20} />
                    <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-leagle-accent">Impact Intelligence</h2>
                </div>
                <h1 className="text-3xl sm:text-4xl font-serif italic text-white tracking-tight">Cross-Reference Engine</h1>
                <p className="text-gray-500 font-medium uppercase text-[9px] sm:text-[10px] tracking-widest px-4 md:px-0">Select a direct regulation and a specific policy to analyze semantic friction.</p>
            </header>

            {/* Comparison Hub */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 items-stretch">
                {/* Regulation Selector Card */}
                <div className={`glass-card p-4 sm:p-6 transition-all duration-500 border-leagle-accent/10 flex flex-col rounded-sm ${selectedReg ? 'bg-leagle-accent/5' : 'bg-white/2'}`}>
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 sm:gap-3">
                            <Image src="/logo.png" alt="Leagle Logo" width={20} height={20} />
                            <h3 className="font-black text-white text-[10px] sm:text-sm uppercase tracking-widest">Regulation</h3>
                        </div>
                        {selectedReg && (
                            <button onClick={() => setSelectedReg(null)} className="text-[8px] font-black text-leagle-accent hover:underline uppercase tracking-widest min-h-[44px] flex items-center">Change</button>
                        )}
                    </div>

                    {!selectedReg ? (
                        <div className="space-y-3 max-h-[200px] sm:max-h-[250px] overflow-y-auto pr-2 custom-scrollbar flex-1">
                            {regulations.map(reg => (
                                <button
                                    key={reg.id}
                                    onClick={() => setSelectedReg(reg)}
                                    className="w-full p-3 sm:p-4 min-h-[48px] rounded-xl text-left bg-white/2 border border-white/5 hover:bg-white/5 hover:border-leagle-accent/30 transition-all group"
                                >
                                    <p className="font-black text-[10px] sm:text-xs text-gray-300 line-clamp-1 group-hover:text-white">{reg.title}</p>
                                    <span className="text-[8px] font-black uppercase text-gray-600 block mt-1">{reg.category}</span>
                                </button>
                            ))}
                        </div>
                    ) : (
                        <div className="p-4 bg-leagle-accent/10 border border-leagle-accent/20 rounded-xl flex-1 flex flex-col justify-center text-center space-y-2">
                            <p className="text-xs sm:text-sm font-black text-white tracking-tight px-2">{selectedReg.title}</p>
                            <p className="text-[8px] sm:text-[9px] font-black text-leagle-accent uppercase tracking-widest">{selectedReg.jurisdiction} • {selectedReg.category}</p>
                        </div>
                    )}
                </div>

                {/* Policy Selector Card */}
                <div className={`glass-card p-4 sm:p-6 transition-all duration-500 border-indigo-500/10 flex flex-col rounded-sm ${selectedPolicy ? 'bg-indigo-500/5' : 'bg-white/2'}`}>
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 sm:gap-3">
                            <FileText className="text-indigo-400" size={20} />
                            <h3 className="font-black text-white text-[10px] sm:text-sm uppercase tracking-widest">Policy</h3>
                        </div>
                        {selectedPolicy && (
                            <button onClick={() => setSelectedPolicy(null)} className="text-[8px] font-black text-indigo-400 hover:underline uppercase tracking-widest min-h-[44px] flex items-center">Change</button>
                        )}
                    </div>

                    {!selectedPolicy ? (
                        <div className="space-y-3 max-h-[200px] sm:max-h-[250px] overflow-y-auto pr-2 custom-scrollbar flex-1">
                            {policies.map(pol => (
                                <button
                                    key={pol.id}
                                    onClick={() => setSelectedPolicy(pol)}
                                    className="w-full p-3 sm:p-4 min-h-[48px] rounded-xl text-left bg-white/2 border border-white/5 hover:bg-white/5 hover:border-indigo-400/30 transition-all group"
                                >
                                    <p className="font-black text-[10px] sm:text-xs text-gray-300 line-clamp-1 group-hover:text-white">{pol.title}</p>
                                    <span className="text-[8px] font-black uppercase text-gray-600 block mt-1">{pol.department}</span>
                                </button>
                            ))}
                        </div>
                    ) : (
                        <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-xl flex-1 flex flex-col justify-center text-center space-y-2">
                            <p className="text-xs sm:text-sm font-black text-white tracking-tight px-2">{selectedPolicy.title}</p>
                            <p className="text-[8px] sm:text-[9px] font-black text-indigo-400 uppercase tracking-widest">{selectedPolicy.owner} • {selectedPolicy.department}</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Run Button */}
            <div className="flex justify-center">
                <button
                    onClick={handleRunAnalysis}
                    disabled={!selectedReg || !selectedPolicy || loading}
                    className={`w-full sm:w-auto px-6 sm:px-12 py-4 rounded-sm font-black text-[9px] sm:text-[10px] tracking-[0.2em] uppercase transition-all flex items-center justify-center gap-2 sm:gap-3 shadow-xl min-h-[48px] ${selectedReg && selectedPolicy && !loading
                        ? 'bg-leagle-accent text-black hover:bg-white active:scale-95'
                        : 'bg-white/5 text-gray-600 border border-white/5 cursor-not-allowed'
                        }`}
                >
                    {loading ? (
                        <>
                            <Loader2 className="animate-spin" size={16} />
                            Analyzing Friction...
                        </>
                    ) : (
                        <>
                            <Zap size={16} />
                            Run Comparison Briefing
                        </>
                    )}
                </button>
            </div>

            {error && (
                <div className="p-4 sm:p-6 bg-red-500/10 border border-red-500/20 rounded-2xl flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-3 sm:gap-4 animate-in fade-in slide-in-from-top-4 max-w-2xl mx-auto">
                    <AlertTriangle className="text-red-500 shrink-0" size={20} />
                    <p className="text-xs sm:text-sm text-red-200 font-medium">{error}</p>
                </div>
            )}

            {/* Analysis Result */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 min-h-[400px]">
                <div className="lg:col-span-1 space-y-4 sm:space-y-6">
                    {result ? (
                        <div className="space-y-4 sm:space-y-6 animate-in fade-in duration-700 h-full flex flex-col">
                            {/* Executive Verdict Card */}
                            <div className="glass-card p-4 sm:p-6 border-leagle-accent/20 space-y-4 rounded-sm">
                                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                                    <h3 className="text-base sm:text-lg font-serif text-white tracking-tight uppercase italic underline decoration-leagle-accent/30 underline-offset-8">Strategic Verdict</h3>
                                    <div className={`px-3 py-1 rounded-sm text-[8px] sm:text-[9px] font-black border tracking-widest uppercase self-start sm:self-auto ${result.impact_level === 'HIGH' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                                        result.impact_level === 'MEDIUM' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                                            'bg-green-500/20 text-green-400 border-green-500/30'
                                        }`}>
                                        {result.impact_level} IMPACT
                                    </div>
                                </div>
                                <p className="text-sm sm:text-lg text-gray-300 leading-relaxed font-serif italic border-l-2 border-leagle-accent/30 pl-3 sm:pl-4 py-2 bg-white/2">
                                    &ldquo;{result.reasoning}&rdquo;
                                </p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex items-center gap-3">
                                        <Clock size={14} className="text-gray-500 shrink-0" />
                                        <div className="overflow-hidden min-w-0">
                                            <p className="text-[7px] font-bold text-gray-500 uppercase tracking-widest truncate">Req. Deadline</p>
                                            <p className="text-[10px] sm:text-xs font-black text-white truncate">{result.compliance_deadline || "Active"}</p>
                                        </div>
                                    </div>
                                    <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex items-center gap-3">
                                        <CheckCircle2 size={14} className="text-leagle-accent shrink-0" />
                                        <div className="overflow-hidden min-w-0">
                                            <p className="text-[7px] font-bold text-gray-500 uppercase tracking-widest truncate">Model</p>
                                            <p className="text-[10px] sm:text-xs font-black text-white truncate">Llama-3.3-Nemotron</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Target Clauses */}
                            <div className="glass-card p-4 sm:p-6 border-white/5 space-y-4">
                                <h3 className="text-[9px] font-black uppercase tracking-widest text-gray-500 flex items-center gap-2">
                                    <FileText size={12} className="text-indigo-400" />
                                    Impacted Legal Artifacts
                                </h3>
                                <div className="flex flex-wrap gap-2 max-h-[120px] overflow-y-auto pr-2 custom-scrollbar">
                                    {Array.isArray(result.affected_clauses) ? (
                                        result.affected_clauses.map((clause, i) => (
                                            <div key={i} className="px-2 sm:px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-gray-400 text-[8px] sm:text-[9px] font-bold flex items-center gap-2 break-all sm:break-normal">
                                                <ChevronRight size={10} className="text-leagle-accent shrink-0" />
                                                {clause}
                                            </div>
                                        ))
                                    ) : (
                                        <div className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-gray-400 text-[9px] font-bold">
                                            {result.affected_clauses || "None Identified"}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : loading ? (
                        <div className="glass-card h-full p-8 sm:p-16 flex flex-col items-center justify-center text-center space-y-6 sm:space-y-8 animate-in fade-in duration-500">
                            <div className="relative">
                                <div className="w-16 h-16 sm:w-20 sm:h-20 border-4 border-leagle-accent/10 rounded-full" />
                                <div className="absolute inset-0 border-t-4 border-leagle-accent rounded-full animate-spin" />
                            </div>
                            <div className="space-y-1">
                                <h3 className="text-base sm:text-lg font-black text-white tracking-tight uppercase">Audit Engine Initialized</h3>
                                <p className="text-[7px] sm:text-[8px] font-black uppercase tracking-[0.3em] text-leagle-accent animate-pulse">Running NVIDIA NIM Reasoning</p>
                            </div>
                        </div>
                    ) : (
                        <div className="glass-card h-full min-h-[250px] border-dashed border-white/5 bg-transparent flex flex-col items-center justify-center text-center p-8 sm:p-12 opacity-50">
                            <ArrowRight className="text-gray-600 mb-3 sm:mb-4" size={24} />
                            <p className="text-[9px] sm:text-[10px] font-black uppercase tracking-[0.2em] text-gray-600">Decision Outcome Awaited</p>
                        </div>
                    )}
                </div>

                {/* Gaps & Roadmap Column */}
                <div className="lg:col-span-1 h-full">
                    {result ? (
                        <div className="grid grid-cols-1 gap-4 sm:gap-6 h-full">
                            {/* Compliance Gaps */}
                            <div className="glass-card overflow-hidden flex flex-col max-h-[250px]">
                                <div className="p-3 sm:p-4 border-b border-white/5 bg-red-500/5">
                                    <h3 className="text-[8px] sm:text-[9px] font-black uppercase tracking-widest text-red-500 flex items-center gap-2">
                                        <AlertTriangle size={12} />
                                        Critical Deficiencies
                                    </h3>
                                </div>
                                <div className="p-3 sm:p-4 space-y-3 overflow-y-auto custom-scrollbar flex-1">
                                    {Array.isArray(result.compliance_gaps) && result.compliance_gaps.length > 0 ? (
                                        result.compliance_gaps.map((gap, i) => (
                                            <div key={i} className="p-3 sm:p-4 bg-white/2 border border-white/5 rounded-xl flex items-start gap-3 sm:gap-4">
                                                <Image src="/logo.png" alt="Leagle Logo" width={16} height={16} className="mt-1 shrink-0 w-4 h-4" />
                                                <p className="text-[10px] sm:text-xs text-gray-300 leading-relaxed font-medium">{gap}</p>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="text-[10px] sm:text-xs text-gray-500 italic p-2 sm:p-4">No critical legal deficiencies identified.</p>
                                    )}
                                </div>
                            </div>

                            {/* Remediation Roadmap */}
                            <div className="glass-card overflow-hidden flex flex-col max-h-[300px]">
                                <div className="p-3 sm:p-4 border-b border-white/5 bg-leagle-accent/5">
                                    <h3 className="text-[8px] sm:text-[9px] font-black uppercase tracking-widest text-leagle-accent flex items-center gap-2">
                                        <Zap size={12} />
                                        Remediation Backlog
                                    </h3>
                                </div>
                                <div className="p-3 sm:p-4 space-y-3 overflow-y-auto custom-scrollbar flex-1">
                                    {Array.isArray(result.recommended_actions) && result.recommended_actions.map((act, i) => (
                                        <div key={i} className="p-3 sm:p-4 bg-white/2 border border-white/5 rounded-xl space-y-2 group hover:border-leagle-accent/30 transition-colors">
                                            <div className="flex justify-between items-start gap-2">
                                                <span className="text-[6px] sm:text-[7px] font-black text-leagle-accent px-2 py-0.5 bg-leagle-accent/10 rounded uppercase shrink-0">Step {act.step || i + 1}</span>
                                                <span className="text-[6px] sm:text-[7px] font-black text-gray-600 uppercase tracking-widest shrink-0">Due {act.deadline_days}d</span>
                                            </div>
                                            <p className="text-[10px] sm:text-xs text-white font-bold leading-snug">{act.action}</p>
                                            <p className="text-[6px] sm:text-[7px] font-black text-gray-500 uppercase tracking-widest">{act.owner}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="glass-card h-full min-h-[250px] border-dashed border-white/5 bg-transparent flex items-center justify-center opacity-50 p-4">
                            <p className="text-[9px] sm:text-[10px] font-black uppercase tracking-[0.2em] text-gray-600 text-center">Artifacts will populate here</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
