"use client"

import { useState, useEffect } from 'react'
import { getHeatmap, getImpactDetails } from '../api/client'
import { ShieldAlert, BarChart3, Activity, X, Target } from 'lucide-react'

export default function RiskHeatmap() {
    const [data, setData] = useState({ heatmap: {}, total_open_impacts: 0 })
    const [loading, setLoading] = useState(true)
    const [selectedCell, setSelectedCell] = useState(null)
    const [details, setDetails] = useState([])
    const [detailsLoading, setDetailsLoading] = useState(false)

    useEffect(() => {
        async function loadData() {
            try {
                const response = await getHeatmap()
                setData(response.data || { heatmap: {}, total_open_impacts: 0 })
            } catch (err) {
                console.error('Failed to load heatmap data', err)
            } finally {
                setLoading(false)
            }
        }
        loadData()
    }, [])

    useEffect(() => {
        if (!selectedCell) return
        async function fetchDetails() {
            setDetailsLoading(true)
            try {
                const res = await getImpactDetails(selectedCell.dept, selectedCell.cat)
                setDetails(res.data || [])
            } catch (err) {
                console.error('Failed to fetch details', err)
            } finally {
                setDetailsLoading(false)
            }
        }
        fetchDetails()
    }, [selectedCell])

    const closeDetails = () => {
        setSelectedCell(null)
        setDetails([])
    }

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
            <Activity className="animate-spin text-leagle-accent" size={40} />
            <p className="text-gray-500 font-black uppercase tracking-[0.3em] text-[10px] animate-pulse">Loading risk matrix...</p>
        </div>
    )

    const departments = Object.keys(data.heatmap || {})
    const categories = Array.from(new Set(
        departments.flatMap(d => Object.keys(data.heatmap[d]))
    ))

    if (departments.length === 0) {
        return (
            <div className="glass-card p-20 text-center max-w-2xl mx-auto space-y-8">
                <ShieldAlert className="mx-auto text-leagle-accent/20" size={64} />
                <div>
                    <h2 className="text-2xl font-black text-white">Matrix Initialized</h2>
                    <p className="text-gray-500 mt-2 font-medium">No open impacts detected. Ingest regulations to populate the matrix.</p>
                </div>
            </div>
        )
    }

    const getScoreStyle = (score) => {
        switch (score) {
            case 3: return 'bg-red-500/[0.05] text-red-500 border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.05)]'
            case 2: return 'bg-amber-500/[0.05] text-amber-500 border-amber-500/20'
            case 1: return 'bg-emerald-500/[0.05] text-emerald-400 border-emerald-500/20'
            default: return 'bg-transparent text-gray-800 border-white/2 opacity-10 cursor-default shadow-none'
        }
    }

    return (
        <div className="space-y-10 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                <div className="space-y-2">
                    <div className="flex items-center gap-2">
                        <BarChart3 className="text-leagle-accent" size={18} />
                        <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-leagle-accent">Risk Oversight</h2>
                    </div>
                    <h1 className="text-4xl font-serif text-white tracking-tight italic underline decoration-leagle-accent/20 underline-offset-8">Risk Exposure Matrix</h1>
                </div>

                <div className="glass-card px-8 py-4 flex items-center gap-6 border-leagle-accent/10 rounded-sm">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-black text-gray-500 tracking-widest leading-none mb-2">Signals Detected</p>
                        <p className="text-2xl font-serif italic text-white leading-none">{data.total_open_impacts}</p>
                    </div>
                    <div className="h-10 w-px bg-white/5"></div>
                    <div className="w-10 h-10 bg-leagle-accent/5 rounded-sm flex items-center justify-center text-leagle-accent border border-leagle-accent/20">
                        <Activity className="animate-pulse" size={20} />
                    </div>
                </div>
            </div>

            <div className="glass-card p-6 md:p-12 border-white/5 relative overflow-hidden rounded-sm bg-white/1">
                <div className="absolute top-0 right-0 w-96 h-96 bg-leagle-accent/2 blur-3xl rounded-none" />

                <div className="overflow-x-auto custom-scrollbar">
                    <table className="w-full border-separate border-spacing-4">
                        <thead>
                            <tr>
                                <th className="p-4 text-left font-black text-gray-600 uppercase text-[10px] tracking-[0.3em]">Department</th>
                                {categories.map(cat => (
                                    <th key={cat} className="p-4 text-center font-black text-gray-600 uppercase text-[10px] tracking-[0.3em] min-w-[150px]">
                                        {cat.replace(/_/g, ' ')}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {departments.map((dept) => (
                                <tr key={dept}>
                                    <td className="p-4">
                                        <div className="flex items-center gap-4">
                                            <div className="h-8 w-1 bg-leagle-accent opacity-50"></div>
                                            <span className="font-serif italic text-white text-lg tracking-tight underline decoration-white/5 underline-offset-4">{dept}</span>
                                        </div>
                                    </td>
                                    {categories.map(cat => {
                                        const score = data.heatmap[dept]?.[cat] || 0
                                        return (
                                            <td key={cat}>
                                                <button
                                                    onClick={() => score > 0 && setSelectedCell({ dept, cat, score })}
                                                    className={`
                                                        w-full h-16 rounded-sm border transition-all duration-300 flex flex-col items-center justify-center group relative overflow-hidden
                                                        ${getScoreStyle(score)}
                                                        ${score > 0 ? 'hover:bg-white/5 active:scale-95' : ''}
                                                    `}
                                                >
                                                    {score > 0 && (
                                                        <>
                                                            <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                                <ArrowUpRight size={12} />
                                                            </div>
                                                            <span className="text-[10px] font-black tracking-widest uppercase mb-1 font-serif italic">
                                                                {score === 3 ? 'Critical' : score === 2 ? 'Warning' : 'Stable'}
                                                            </span>
                                                            <div className="flex gap-1.5">
                                                                {[...Array(score)].map((_, i) => (
                                                                    <div key={i} className="w-1.5 h-3 bg-current" />
                                                                ))}
                                                            </div>
                                                        </>
                                                    )}
                                                </button>
                                            </td>
                                        )
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Legend */}
                <div className="mt-16 flex flex-wrap gap-10 items-center px-8 py-6 bg-white/2 rounded-sm border border-white/5">
                    {[
                        { label: "Critical", color: "bg-red-500/40" },
                        { label: "Muted Warning", color: "bg-amber-500/40" },
                        { label: "Stable / Verified", color: "bg-emerald-500/20" }
                    ].map((item, i) => (
                        <div key={i} className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-none ${item.color} border border-white/5`} />
                            <span className="text-[9px] font-black text-gray-600 uppercase tracking-[0.2em]">{item.label}</span>
                        </div>
                    ))}
                    <div className="ml-auto text-[9px] font-serif italic text-leagle-accent uppercase tracking-widest">
                        Neural Scoring Subsystem Active
                    </div>
                </div>
            </div>

            {/* Drill Down Overlay */}
            {selectedCell && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-leagle-bg/80 backdrop-blur-xl animate-in fade-in duration-300" onClick={closeDetails}>
                    <div className="glass-card max-w-3xl w-full border-white/10 shadow-[0_0_100px_rgba(0,0,0,0.5)] overflow-hidden animate-in zoom-in-95 duration-300" onClick={e => e.stopPropagation()}>
                        <div className="p-10 border-b border-white/5 bg-white/5 flex justify-between items-start">
                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-leagle-accent/5 rounded-sm text-leagle-accent border border-leagle-accent/20">
                                        <Target size={20} />
                                    </div>
                                    <h3 className="text-xs font-black uppercase tracking-[0.3em] text-leagle-accent italic">Segment Analysis</h3>
                                </div>
                                <h4 className="text-3xl font-serif italic text-white tracking-tight leading-tight underline decoration-leagle-accent/30 underline-offset-8">
                                    {selectedCell.dept} Unit
                                </h4>
                                <p className="text-gray-500 font-black uppercase text-[9px] tracking-[0.2em] mt-4">
                                    Jurisdictional Segment: <span className="text-leagle-accent">{selectedCell.cat?.replace(/_/g, ' ')}</span>
                                </p>
                            </div>
                            <button
                                onClick={closeDetails}
                                className="w-12 h-12 bg-white/5 hover:bg-white/10 rounded-2xl flex items-center justify-center text-gray-500 hover:text-white transition-all border border-white/5"
                            >
                                <X size={24} />
                            </button>
                        </div>

                        <div className="p-10 max-h-[60vh] overflow-y-auto custom-scrollbar space-y-8">
                            {detailsLoading ? (
                                <div className="py-24 flex flex-col items-center gap-4">
                                    <Activity className="animate-spin text-leagle-accent" size={32} />
                                    <p className="text-[10px] font-black uppercase tracking-widest text-leagle-accent animate-pulse">Loading impact evidence...</p>
                                </div>
                            ) : details.length > 0 ? (
                                <div className="space-y-6">
                                    {details.map((m, idx) => (
                                        <div key={idx} className="p-8 bg-white/1 rounded-sm border border-white/5 space-y-6 group hover:bg-white/2 transition-all duration-300">
                                            <div className="flex justify-between items-start">
                                                <div className="space-y-1">
                                                    <p className="text-[9px] font-black text-leagle-accent uppercase tracking-widest italic">Impact Record #{idx + 1}</p>
                                                    <h4 className="text-xl font-serif text-white group-hover:text-leagle-accent transition-colors leading-tight italic">{m.regulation_title}</h4>
                                                </div>
                                                <span className={`px-4 py-1 rounded-sm text-[9px] font-black border uppercase tracking-widest ${m.impact_level === 'HIGH' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                                                    'bg-amber-500/10 text-amber-500 border-amber-500/20'
                                                    }`}>
                                                    {m.impact_level} SEVERITY
                                                </span>
                                            </div>

                                            <div className="relative">
                                                <div className="absolute left-0 top-0 w-1 h-full bg-leagle-accent/20 rounded-full" />
                                                <p className="text-sm text-gray-400 leading-relaxed pl-6 italic font-medium">
                                                    &ldquo;{m.summary}&rdquo;
                                                </p>
                                            </div>

                                            <div className="flex gap-4 pt-2">
                                                <button className="flex-1 py-4 bg-leagle-accent/10 border border-leagle-accent/20 text-leagle-accent font-black uppercase tracking-widest text-[10px] rounded-2xl hover:bg-leagle-accent/20 transition-all active:scale-95 shadow-lg">
                                                    View Evidence
                                                </button>
                                                <button className="flex-1 py-4 bg-white/5 border border-white/10 text-gray-500 font-black uppercase tracking-widest text-[10px] rounded-2xl hover:text-white hover:bg-white/10 transition-all active:scale-95">
                                                    Open Affected Policy
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="py-20 text-center space-y-4">
                                    <div className="text-4xl opacity-20">🛡️</div>
                                    <p className="font-black uppercase tracking-widest text-[10px] text-gray-600">No open impacts in this segment.</p>
                                </div>
                            )}
                        </div>

                        <div className="p-10 bg-white/5 border-t border-white/5 flex justify-end">
                            <button
                                onClick={closeDetails}
                                className="px-10 py-4 bg-white/5 border border-white/10 text-white rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-white/10 transition-all active:scale-95"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

function ArrowUpRight({ size }) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <line x1="7" y1="17" x2="17" y2="7"></line>
            <polyline points="7 7 17 7 17 17"></polyline>
        </svg>
    )
}
