"use client"

import { useState, useEffect } from 'react'
import { getRegulationIntel } from '../api/client'
import { X, ShieldAlert, BrainCircuit, Target, BookOpen } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function RegulationDetail({ regulation, onClose }) {
    const [intel, setIntel] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadIntel() {
            try {
                const { data } = await getRegulationIntel(regulation.id)
                setIntel(data)
            } catch (err) {
                console.error('Failed to load regulation analysis', err)
            } finally {
                setLoading(false)
            }
        }
        loadIntel()
    }, [regulation.id])

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-8 bg-leagle-bg/80 backdrop-blur-2xl animate-in fade-in duration-300" onClick={onClose}>
            <div className="glass-card w-full max-w-5xl max-h-[90vh] border-leagle-accent/20 bg-leagle-bg shadow-[0_40px_100px_rgba(0,0,0,0.8)] relative overflow-hidden flex flex-col rounded-sm" onClick={e => e.stopPropagation()}>
                {/* Visual Accent */}
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-leagle-accent/5 rounded-none blur-[120px] -mr-64 -mt-64" />

                <div className="p-10 pb-6 flex justify-between items-start relative z-10">
                    <div className="space-y-4 flex-1">
                        <div className="flex items-center gap-3">
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-leagle-accent bg-leagle-accent/5 px-4 py-1.5 rounded-sm border border-leagle-accent/20">
                                Regulation Analysis
                            </span>
                            {regulation.jurisdiction && (
                                <span className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 bg-white/2 px-4 py-1.5 rounded-sm border border-white/10">
                                    Region: {regulation.jurisdiction}
                                </span>
                            )}
                        </div>
                        <h2 className="text-4xl font-serif text-white tracking-tight italic leading-tight pr-12 underline decoration-leagle-accent/20 underline-offset-8">
                            {regulation.title}
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-12 h-12 bg-white/2 hover:bg-white/5 rounded-sm flex items-center justify-center text-gray-500 hover:text-leagle-accent transition-all border border-white/5"
                    >
                        <X size={24} />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-10 pt-4 relative z-10 custom-scrollbar">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-32 gap-6">
                            <div className="w-16 h-16 border-4 border-leagle-accent border-t-transparent rounded-full animate-spin shadow-[0_0_15px_#38bdf8]" />
                            <p className="text-leagle-accent font-black uppercase tracking-[0.3em] text-[10px] animate-pulse">Loading analysis details...</p>
                        </div>
                    ) : (
                        <div className="space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
                            {/* Analytics Row */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="glass-card p-10 bg-white/2 border-white/5 group hover:bg-white/4 transition-all rounded-sm">
                                    <div className="flex items-center gap-4 mb-8">
                                        <div className="p-3 bg-red-500/10 text-red-500 rounded-sm border border-red-500/20">
                                            <ShieldAlert size={24} />
                                        </div>
                                        <h3 className="font-serif text-xl text-white italic">Risk Exposure</h3>
                                    </div>
                                    <div className="space-y-4">
                                        <div className="flex items-end justify-between">
                                            <span className={`text-6xl font-black tracking-tighter ${intel.risk_score >= 70 ? 'text-red-500 shadow-red-500/10' :
                                                intel.risk_score >= 40 ? 'text-amber-500' : 'text-emerald-400'
                                                }`}>
                                                {intel.risk_score}%
                                            </span>
                                            <span className="text-[10px] font-black uppercase tracking-widest text-gray-600 mb-2">Severity Index</span>
                                        </div>
                                        <div className="w-full bg-white/5 rounded-full h-2 overflow-hidden">
                                            <div
                                                className={`h-full transition-all duration-1000 ease-out shadow-[0_0_10px_currentColor] ${intel.risk_score >= 70 ? 'bg-red-500' :
                                                    intel.risk_score >= 40 ? 'bg-amber-500' : 'bg-emerald-400'
                                                    }`}
                                                style={{ width: `${intel.risk_score}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="glass-card p-10 bg-white/2 border-white/5 rounded-sm">
                                    <div className="flex items-center gap-4 mb-8">
                                        <div className="p-3 bg-leagle-accent/5 text-leagle-accent rounded-sm border border-leagle-accent/20">
                                            <Target size={24} />
                                        </div>
                                        <h3 className="font-serif text-xl text-white italic">Impact Vectors</h3>
                                    </div>
                                    <div className="flex flex-wrap gap-3">
                                        {intel.impact_areas?.map((area, i) => (
                                            <span key={i} className="px-4 py-2 bg-leagle-accent/5 border border-leagle-accent/10 rounded-sm text-[10px] font-black text-leagle-accent uppercase tracking-widest">
                                                {area}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Executive Summary */}
                            <div className="glass-card p-12 bg-white/2 border-white/5 rounded-sm">
                                <div className="flex items-center gap-4 mb-8">
                                    <BrainCircuit className="text-leagle-accent" size={28} />
                                    <h3 className="text-2xl font-serif text-white italic tracking-tight underline decoration-leagle-accent/20 underline-offset-8">Executive Summary</h3>
                                </div>
                                <div className="relative">
                                    <div className="absolute -left-6 top-0 w-1 h-full bg-leagle-accent/30" />
                                    <p className="text-xl text-gray-300 leading-relaxed font-serif italic pl-4">
                                        &ldquo;{intel.explanation}&rdquo;
                                    </p>
                                </div>
                            </div>

                            {/* Comprehensive Comparison */}
                            <div className="space-y-8">
                                <div className="flex items-center gap-4 px-4">
                                    <BookOpen className="text-indigo-400" size={28} />
                                    <h3 className="text-2xl font-black text-white tracking-tight">Legislative Cross-reference</h3>
                                </div>
                                <div className="glass-card p-12 bg-white/2 border-white/5 prose prose-invert max-w-none shadow-inner">
                                    <div className="text-lg text-gray-300 leading-relaxed font-medium selection:bg-leagle-accent/30 space-y-6">
                                        <ReactMarkdown>{intel.comparison}</ReactMarkdown>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-10 pt-6 border-t border-white/5 bg-white/5 relative z-10 flex justify-end">
                    <button
                        onClick={onClose}
                        className="btn-premium px-12 py-4"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    )
}
