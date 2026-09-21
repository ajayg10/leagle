'use client'

import React, { useState, useEffect, useMemo } from 'react'
import dynamic from 'next/dynamic'
import {
    ComposableMap,
    Geographies,
    Geography,
    Sphere,
    Graticule
} from 'react-simple-maps'
import { scaleLinear } from 'd3-scale'
import { Globe as GlobeIcon, Map as MapIcon, Info, AlertTriangle } from 'lucide-react'

// Dynamic import for Globe.gl as it requires browser environment
const Globe = dynamic(() => import('react-globe.gl'), {
    ssr: false,
    loading: () => <div className="w-full h-full flex items-center justify-center text-slate-500 animate-pulse">Initializing Neural Globe...</div>
})

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

export default function DualModeHeatmap() {
    const [mode, setMode] = useState('3d') // '2d' or '3d'
    const [data, setData] = useState({})
    const [loading, setLoading] = useState(true)
    const [hoveredCountry, setHoveredCountry] = useState(null)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
                const resp = await fetch(`${API_BASE_URL}/api/analytics/risk-heatmap`)
                const result = await resp.json()
                setData(result)
            } catch (err) {
                console.error("Failed to fetch heatmap data:", err)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [])

    const globeData = useMemo(() => {
        return Object.values(data).map(d => ({
            ...d,
            // Coordinates for center of countries (simplified)
            lat: d.id === 'US' ? 37 : d.id === 'GB' ? 55 : d.id === 'IN' ? 20 : d.id === 'EU' ? 50 : d.id === 'AU' ? -25 : 0,
            lng: d.id === 'US' ? -95 : d.id === 'GB' ? -2 : d.id === 'IN' ? 78 : d.id === 'EU' ? 10 : d.id === 'AU' ? 133 : 0,
            size: 0.1 + (d.intensity * 0.5),
            color: d.color
        }))
    }, [data])

    if (loading) {
        return (
            <div className="w-full h-[600px] bg-[rgba(2,9,22,0.6)] rounded-3xl border border-white/5 flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-leagle-accent/20 border-t-leagle-accent rounded-full animate-spin" />
                    <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Retrieving Global Intelligence...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="relative w-full h-[700px] bg-[rgba(2,9,22,0.4)] rounded-[40px] border border-white/5 overflow-hidden group">
            {/* HUD Header */}
            <div className="absolute top-8 left-10 z-10 flex flex-col gap-1">
                <h2 className="text-2xl font-semibold text-white tracking-tight flex items-center gap-3">
                    Global Risk Hotspots
                    <span className="px-2 py-0.5 rounded-md bg-leagle-accent/10 border border-leagle-accent/20 text-[10px] font-bold text-leagle-accent uppercase tracking-widest">
                        Last 30 Days
                    </span>
                </h2>
                <p className="text-sm text-slate-500 font-medium tracking-wide">Institutional Regulatory Monitoring Protocol</p>
            </div>

            {/* Mode Toggle */}
            <div className="absolute top-8 right-10 z-10 flex items-center bg-black/40 backdrop-blur-xl p-1.5 rounded-2xl border border-white/10 shadow-2xl">
                <button
                    onClick={() => setMode('2d')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all ${mode === '2d' ? 'bg-leagle-accent text-black shadow-[0_0_20px_rgba(56,189,248,0.4)]' : 'text-slate-400 hover:text-white'}`}
                >
                    <MapIcon size={14} />
                    2D Map
                </button>
                <button
                    onClick={() => setMode('3d')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all ${mode === '3d' ? 'bg-leagle-accent text-black shadow-[0_0_20px_rgba(56,189,248,0.4)]' : 'text-slate-400 hover:text-white'}`}
                >
                    <GlobeIcon size={14} />
                    3D Globe
                </button>
            </div>

            {/* Main Map Content */}
            <div className="w-full h-full flex items-center justify-center">
                {mode === '2d' ? (
                    <ComposableMap projectionConfig={{ rotate: [-10, 0, 0], scale: 147 }} className="w-full h-full max-h-[100%]">
                        <Sphere stroke="rgba(255,255,255,0.05)" strokeWidth={0.5} />
                        <Graticule stroke="rgba(255,255,255,0.03)" strokeWidth={0.5} />
                        <Geographies geography={geoUrl}>
                            {({ geographies }) =>
                                geographies.map((geo) => {
                                    const countryData = data[geo.id] || data[geo.properties.ISO_A2] || data[geo.properties.ISO_A2_EH]
                                    return (
                                        <Geography
                                            key={geo.rsmKey}
                                            geography={geo}
                                            onMouseEnter={() => setHoveredCountry(geo.properties.NAME || geo.properties.name)}
                                            onMouseLeave={() => setHoveredCountry(null)}
                                            style={{
                                                default: {
                                                    fill: countryData ? countryData.color : "rgba(255,255,255,0.03)",
                                                    outline: "none",
                                                    stroke: "rgba(255,255,255,0.08)",
                                                    strokeWidth: 0.5
                                                },
                                                hover: {
                                                    fill: countryData ? countryData.color : "rgba(255,255,255,0.1)",
                                                    outline: "none",
                                                    stroke: "#38bdf8",
                                                    strokeWidth: 1
                                                },
                                                pressed: {
                                                    outline: "none"
                                                }
                                            }}
                                        />
                                    )
                                })
                            }
                        </Geographies>
                    </ComposableMap>
                ) : (
                    <div className="w-full h-full">
                        <Globe
                            globeImageUrl="//unpkg.com/three-globe/example/img/earth-dark.jpg"
                            bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
                            backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
                            pointsData={globeData}
                            pointAltitude="intensity"
                            pointColor="color"
                            pointRadius={0.5}
                            pointsMerge={true}
                            pointLabel={d => `<b>${d.label}</b><br/>Severity: ${Math.round(d.intensity * 10)}/10<br/>Regs: ${d.count}`}
                            hexBinPointsData={globeData}
                            hexBinPointWeight="count"
                            hexAltitude={d => d.sumWeight * 0.05}
                            hexTopColor={d => "#ef4444"}
                            hexSideColor={d => "rgba(239, 68, 68, 0.4)"}
                            hexBinResolution={4}
                            backgroundColor="rgba(0,0,0,0)"
                            width={1000}
                            height={700}
                        />
                    </div>
                )}
            </div>

            {/* Info Legend */}
            <div className="absolute bottom-8 left-10 flex items-center gap-8 bg-black/40 backdrop-blur-xl px-6 py-4 rounded-3xl border border-white/10">
                <div className="flex flex-col gap-1.5">
                    <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Risk Intensity</span>
                    <div className="flex gap-1">
                        <div className="w-8 h-1.5 rounded-full bg-green-500/50" />
                        <div className="w-8 h-1.5 rounded-full bg-amber-500/50" />
                        <div className="w-8 h-1.5 rounded-full bg-red-500/50" />
                    </div>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col gap-1">
                    <span className="text-[9px] font-bold uppercase tracking-widest text-slate-400">Target Jurisdictions</span>
                    <span className="text-sm font-semibold text-white tracking-tight">Active: {Object.keys(data).length}</span>
                </div>
            </div>

            {hoveredCountry && (
                <div className="absolute top-[40%] left-[50%] -translate-x-1/2 bg-black/80 backdrop-blur-2xl px-5 py-3 rounded-2xl border border-leagle-accent/20 shadow-[0_0_40px_rgba(56,189,248,0.1)] pointer-events-none fade-in">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-leagle-accent">{hoveredCountry}</p>
                </div>
            )}
        </div>
    )
}
