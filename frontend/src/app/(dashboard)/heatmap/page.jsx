'use client'

import React from 'react'
import NeuralIntelligenceMap from '../../components/NeuralIntelligenceMap'
import { ShieldAlert, Globe, Activity, Info, Maximize2, Layers, AlertTriangle } from 'lucide-react'

export default function HeatmapPage() {
    return (
        <div className="relative h-[calc(100vh-100px)] overflow-hidden animate-in fade-in duration-1000 bg-black">

            {/* Background Texture */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none" />

            {/* MINIMALIST HEADER: Top Center - Avoid Corner Collisions */}
            <div className="absolute top-6 left-1/2 -translate-x-1/2 z-30 text-center pointer-events-none">
                <div className="flex flex-col items-center gap-1">
                    <h1 className="text-xl font-black text-white/90 tracking-[0.6em] uppercase italic leading-none drop-shadow-lg">
                        Intelligence Hub
                    </h1>
                    <div className="flex items-center gap-6 mt-2 opacity-50">
                        <div className="flex items-center gap-2">
                            <span className="w-1 h-1 bg-emerald-500 rounded-full animate-pulse shadow-glow" />
                            <span className="text-[7px] font-black text-emerald-500 uppercase tracking-widest">Neural Link: SYNCED</span>
                        </div>
                        <div className="w-6 h-px bg-white/20" />
                        <span className="text-[7px] font-black text-slate-500 uppercase tracking-widest">Protocol: GLOBAL_OVERSIGHT</span>
                    </div>
                </div>
            </div>

            {/* Main Map Visualizer - Takes Full Center Space */}
            <div className="w-full h-full relative z-10">
                <NeuralIntelligenceMap />
            </div>

            {/* COMPACT SIDE HUD: Right - Slimmer + Non-obstructive */}
            <div className="absolute top-1/2 right-6 -translate-y-1/2 z-30 hidden xl:block pointer-events-auto">
                <div className="bg-black/80 backdrop-blur-3xl border border-white/5 p-6 min-w-[280px] shadow-2xl">
                    <h3 className="text-[8px] font-black uppercase tracking-[0.4em] text-slate-600 mb-6 flex justify-between items-center pr-2">
                        VOLATILITY INDEX
                        <Activity size={10} className="text-slate-800" />
                    </h3>

                    <div className="space-y-6">
                        <RegionStripe label="European Union" risk="Critical" perc={82} color="#f87171" />
                        <RegionStripe label="United States" risk="Elevated" perc={54} color="#fbbf24" />
                        <RegionStripe label="Asia Pacific" risk="Stable" perc={31} color="#34d399" />
                        <RegionStripe label="UK Regulator" risk="Moderate" perc={47} color="#fbbf24" />
                    </div>

                    <div className="mt-8 pt-6 border-t border-white/5">
                        <div className="group cursor-pointer p-4 bg-red-400/5 border border-red-500/10 hover:border-red-500/40 transition-all active:scale-95">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="text-red-500/60" size={12} />
                                <span className="text-[8px] font-black text-red-500/70 uppercase tracking-widest">Neural Divergence</span>
                            </div>
                            <p className="text-[9px] text-slate-500 font-medium mt-1 leading-tight group-hover:text-slate-300">
                                GDPR Article 5 Drift detected in Australian Legislative Draft 2026-A.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* MINIMAL FOOTER: Bottom Left - Integrated with Map Style */}
            <div className="absolute bottom-6 left-6 z-30 pointer-events-none opacity-40">
                <p className="text-[7px] font-bold text-slate-500 uppercase tracking-[0.4em] italic">
                    Institutional Synchronization Active • System Ref: L-GN_2026
                </p>
            </div>

        </div>
    )
}

function RegionStripe({ label, risk, perc, color }) {
    return (
        <div className="space-y-2 group">
            <div className="flex justify-between items-center text-[8px] font-black uppercase tracking-widest text-slate-500">
                <span className="group-hover:text-white transition-colors">{label}</span>
                <span style={{ color }} className="text-[7px] italic opacity-60 group-hover:opacity-100 transition-opacity">{risk}</span>
            </div>
            <div className="w-full h-px bg-white/5">
                <div
                    className="h-full transition-all duration-[2000ms] ease-in-out"
                    style={{ width: `${perc}%`, backgroundColor: color, boxShadow: `0 0 10px ${color}44` }}
                />
            </div>
        </div>
    )
}
