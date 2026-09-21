'use client'

import React, { useState, useEffect, useMemo, useRef } from 'react'
import dynamic from 'next/dynamic'
import { useRouter } from 'next/navigation'
import { scaleLinear } from 'd3-scale'
import {
    Zap,
    Map as MapIcon,
    Globe as GlobeIcon,
    Activity,
    ShieldCheck,
    AlertCircle,
    Maximize2,
    ChevronRight,
    Crosshair,
    Wifi,
    ZoomIn,
    ZoomOut,
    X,
    TrendingUp,
    FileText,
    ExternalLink,
    Loader2
} from 'lucide-react'
import {
    ComposableMap,
    Geographies,
    Geography,
    Marker,
    Line,
    ZoomableGroup
} from "react-simple-maps"

// Sources optimized for their respective libraries
const TOPO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
const GLOBE_GEO_URL = "https://raw.githubusercontent.com/vasturiano/react-globe.gl/master/example/datasets/ne_110m_admin_0_countries.geojson"

// Dynamic import for Globe.gl
const Globe = dynamic(() => import('react-globe.gl'), {
    ssr: false,
    loading: () => <div className="w-full h-full flex items-center justify-center text-slate-500 font-mono text-[8px] tracking-[0.5em] uppercase">Booting Neural Core...</div>
})

export default function NeuralIntelligenceMap() {
    const router = useRouter()
    const globeRef = useRef()
    const [mode, setMode] = useState('3d')
    const [data, setData] = useState({ heatmap: {}, connections: [], summary: {} })
    const [loading, setLoading] = useState(true)
    const [zoom, setZoom] = useState(1)
    const [selectedCountry, setSelectedCountry] = useState(null)
    const [globeFeatures, setGlobeFeatures] = useState([])
    const [isAnalyzing, setIsAnalyzing] = useState(false)

    const coords = {
        'US': { lat: 37.0902, lng: -95.7129, iso2: 'US' },
        'GB': { lat: 55.3781, lng: -3.4360, iso2: 'GB' },
        'UK': { lat: 55.3781, lng: -3.4360, iso2: 'GB' },
        'EU': { lat: 50.8503, lng: 4.3517, iso2: 'EU' },
        'IN': { lat: 20.5937, lng: 78.9629, iso2: 'IN' },
        'AU': { lat: -25.2744, lng: 133.7751, iso2: 'AU' },
        'CA': { lat: 56.1304, lng: -106.3468, iso2: 'CA' },
        'DE': { lat: 51.1657, lng: 10.4515, iso2: 'DE' },
        'FR': { lat: 46.2276, lng: 2.2137, iso2: 'FR' },
        'JP': { lat: 36.2048, lng: 138.2529, iso2: 'JP' },
        'CN': { lat: 35.8617, lng: 104.1954, iso2: 'CN' },
        'RU': { lat: 61.5240, lng: 105.3188, iso2: 'RU' },
        'BR': { lat: -14.2350, lng: -51.9253, iso2: 'BR' },
        'SG': { lat: 1.3521, lng: 103.8198, iso2: 'SG' },
        'KR': { lat: 35.9078, lng: 127.7669, iso2: 'KR' },
        'MX': { lat: 23.6345, lng: -102.5528, iso2: 'MX' },
        'ZA': { lat: -30.5595, lng: 22.9375, iso2: 'ZA' },
        'AE': { lat: 23.4241, lng: 53.8478, iso2: 'AE' }
    }

    useEffect(() => {
        fetch(GLOBE_GEO_URL).then(res => res.json()).then(res => setGlobeFeatures(res.features))

        const fetchData = async () => {
            try {
                const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
                const resp = await fetch(`${API_BASE_URL}/api/analytics/risk-heatmap`)
                const result = await resp.json()
                setData(result)
            } catch (err) {
                console.error("Neural Map Sync Failed:", err)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
        const interval = setInterval(fetchData, 30000)
        return () => clearInterval(interval)
    }, [])

    const globeData = useMemo(() => {
        if (!data.heatmap) return []
        return Object.values(data.heatmap)
            .filter(d => coords[d.id])
            .map(d => ({
                ...d,
                lat: coords[d.id].lat,
                lng: coords[d.id].lng,
                color: d.color
            }))
    }, [data.heatmap])

    const arcsData = useMemo(() => {
        if (!data.connections) return []
        return data.connections
            .filter(conn => coords[conn.startId] && coords[conn.endId])
            .map(conn => ({
                startLat: coords[conn.startId].lat,
                startLng: coords[conn.startId].lng,
                endLat: coords[conn.endId].lat,
                endLng: coords[conn.endId].lng,
                color: ['#0ea5e9', '#6366f1', '#22c55e'][Math.floor(Math.random() * 3)],
                name: conn.label
            }))
    }, [data.connections])

    const map2DToISO = (geo) => {
        const name = geo.properties.name
        if (name === "United States of America" || name === "USA" || name === "United States") return "US"
        if (name === "United Kingdom") return "GB"
        if (name === "India") return "IN"
        if (name === "Australia") return "AU"
        if (name === "Canada") return "CA"
        if (name === "Japan") return "JP"
        if (name === "China") return "CN"
        if (name === "Germany") return "DE"
        if (name === "France") return "FR"
        if (name === "Russia") return "RU"
        if (name === "Brazil") return "BR"
        if (name === "Singapore") return "SG"
        if (name === "South Korea") return "KR"
        if (name === "Mexico") return "MX"
        if (name === "South Africa") return "ZA"
        if (name === "United Arab Emirates" || name === "UAE") return "AE"
        if (name === "Belgium" || name === "European Union") return "EU"
        return null
    }

    const handleCountryClick = (stats_id, fallback_name) => {
        const backend_stats = data.heatmap[stats_id] || {}
        const stats = {
            id: stats_id,
            name: backend_stats.name || fallback_name || stats_id || "Unknown Node",
            count: backend_stats.count || 0,
            avg_risk: backend_stats.avg_risk || 0,
            color: backend_stats.color || "#333"
        }
        setSelectedCountry(stats)
    }

    const handleDeepAnalysis = (e) => {
        e.stopPropagation()
        setIsAnalyzing(true)

        // Simulate neural process before redirection
        setTimeout(() => {
            router.push(`/regulations?jurisdiction=${selectedCountry.id}`)
        }, 800)
    }

    if (loading) return (
        <div className="w-full h-full min-h-[700px] flex items-center justify-center bg-black/40 border border-white/5">
            <div className="flex flex-col items-center gap-4">
                <Activity className="animate-pulse text-leagle-accent" size={24} />
                <p className="text-[8px] font-black uppercase tracking-[0.5em] text-slate-500">Synchronizing Global Parallels</p>
            </div>
        </div>
    )

    return (
        <div className="relative w-full h-full min-h-[800px] bg-leagle-bg overflow-hidden transition-all duration-700">

            {/* MODE TOGGLE */}
            <div className="absolute top-6 right-6 z-40 flex bg-black/60 backdrop-blur-md border border-white/10 p-0.5 shadow-2xl">
                <button
                    onClick={() => setMode('2d')}
                    className={`flex items-center gap-1.5 px-4 py-1.5 text-[8px] font-black uppercase tracking-[0.2em] transition-all ${mode === '2d' ? 'bg-leagle-accent text-black font-black' : 'text-slate-500 hover:text-white'}`}
                >
                    <MapIcon size={10} /> 2D Flat
                </button>
                <button
                    onClick={() => setMode('3d')}
                    className={`flex items-center gap-1.5 px-4 py-1.5 text-[8px] font-black uppercase tracking-[0.2em] transition-all ${mode === '3d' ? 'bg-leagle-accent text-black font-black' : 'text-slate-500 hover:text-white'}`}
                >
                    <GlobeIcon size={10} /> 3D Globe
                </button>
            </div>

            {/* Primary Visualizer */}
            <div className="w-full h-full flex items-center justify-center">
                {mode === '3d' ? (
                    <Globe
                        ref={globeRef}
                        backgroundColor="rgba(0,0,0,0)"
                        globeImageUrl="//unpkg.com/three-globe/example/img/earth-dark.jpg"
                        bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"

                        polygonsData={globeFeatures}
                        polygonCapColor={() => 'rgba(255, 255, 255, 0.05)'}
                        polygonSideColor={() => 'rgba(0, 0, 0, 0)'}
                        polygonStrokeColor={() => 'rgba(255, 255, 255, 0.1)'}
                        polygonLabel={({ properties: d }) => `<b>${d.NAME}</b>`}
                        onPolygonClick={(poly) => {
                            const iso = poly.properties.ISO_A2 || poly.properties.iso_a2
                            handleCountryClick(iso, poly.properties.NAME)
                        }}

                        pointsData={globeData}
                        pointLat="lat"
                        pointLng="lng"
                        pointColor="color"
                        pointAltitude={0.01}
                        pointRadius={0.8}

                        arcsData={arcsData}
                        arcStartLat="startLat"
                        arcStartLng="startLng"
                        arcEndLat="endLat"
                        arcEndLng="endLng"
                        arcColor={() => 'rgba(14, 165, 233, 0.4)'} // Consistent teal/blue
                        arcDashLength={0.4}
                        arcDashGap={4}
                        arcDashAnimateTime={8000} // Slower, calmer
                        arcStroke={0.2} // Thinner arcs

                        showAtmosphere={true}
                        atmosphereColor="#0ea5e9"
                        atmosphereAltitude={0.15}

                        width={1600}
                        height={900}
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center animate-in duration-500 bg-black/5">
                        <ComposableMap projectionConfig={{ scale: 120 }}>
                            <ZoomableGroup zoom={zoom} onMoveEnd={({ zoom }) => setZoom(zoom)} center={[0, 0]}>
                                <Geographies geography={TOPO_URL}>
                                    {({ geographies }) =>
                                        geographies.map((geo) => (
                                            <Geography
                                                key={geo.rsmKey}
                                                geography={geo}
                                                fill="#050505"
                                                stroke="#222"
                                                strokeWidth={0.5}
                                                onClick={() => {
                                                    const iso = map2DToISO(geo)
                                                    if (iso) handleCountryClick(iso, geo.properties.name)
                                                }}
                                                style={{
                                                    default: { outline: "none" },
                                                    hover: { fill: "#111", stroke: "#leagle-accent", outline: "none", cursor: "pointer" },
                                                    pressed: { fill: "#leagle-accent", outline: "none" },
                                                }}
                                            />
                                        ))
                                    }
                                </Geographies>
                                {arcsData.map((arc, i) => (
                                    <Line
                                        key={i}
                                        from={[arc.startLng, arc.startLat]}
                                        to={[arc.endLng, arc.endLat]}
                                        stroke={arc.color}
                                        strokeWidth={1}
                                        strokeOpacity={0.4}
                                        strokeLinecap="round"
                                        className="neural-arc-2d"
                                    />
                                ))}
                                {globeData.map((d, i) => (
                                    <Marker key={i} coordinates={[d.lng, d.lat]}>
                                        <circle r={3} fill={d.color} stroke="#000" strokeWidth={0.5} />
                                        <circle r={7} fill={d.color} opacity={0.15} className="animate-pulse" />
                                    </Marker>
                                ))}
                            </ZoomableGroup>
                        </ComposableMap>
                        <style jsx global>{`
              .neural-arc-2d { stroke-dasharray: 6, 10; animation: arcFlow 25s linear infinite; }
              @keyframes arcFlow { from { stroke-dashoffset: 300; } to { stroke-dashoffset: 0; } }
            `}</style>
                    </div>
                )}
            </div>

            {/* MODAL SYSTEM - HARDENED INTERACTIVITY */}
            {selectedCountry && (
                <div className="absolute inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-md animate-in fade-in duration-300">
                    <div className="bg-[#050505] border border-white/10 p-10 min-w-[380px] shadow-[0_0_150px_rgba(0,0,0,1)] relative select-none ring-1 ring-white/5">

                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                setSelectedCountry(null);
                            }}
                            className="absolute top-4 right-4 p-4 text-slate-500 hover:text-white hover:bg-white/5 transition-all rounded-full z-[110]"
                        >
                            <X size={24} strokeWidth={3} />
                        </button>

                        <div className="flex items-center gap-6 mb-10">
                            <div className="w-2 h-16 shadow-glow" style={{ backgroundColor: selectedCountry.color }} />
                            <div className="space-y-1">
                                <h2 className="text-3xl font-black text-white tracking-tighter uppercase italic leading-none">
                                    {selectedCountry.name}
                                </h2>
                                <div className="flex items-center gap-2">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em]">Node Reference: {selectedCountry.id}</span>
                                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-10">
                            <div className="grid grid-cols-2 gap-10">
                                <div className="space-y-3">
                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none">Intelligence Mass</p>
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-4xl font-black text-white leading-none">{selectedCountry.count || 0}</span>
                                        <span className="text-[8px] font-bold text-slate-600 uppercase tracking-widest">Points</span>
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none">Neural Divergence</p>
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-4xl font-black leading-none" style={{ color: selectedCountry.color }}>
                                            {Math.round(selectedCountry.avg_risk || 0)}%
                                        </span>
                                        <TrendingUp size={14} style={{ color: selectedCountry.color }} />
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white/5 p-4 border-l-2 border-slate-700">
                                <p className="text-[11px] text-slate-400 font-medium italic leading-relaxed">
                                    Autonomous tracking for <span className="text-white not-italic font-bold">{selectedCountry.name}</span> active. Semantic synthesis detects high divergence in localized regulatory frameworks.
                                </p>
                            </div>

                            <button
                                onClick={handleDeepAnalysis}
                                disabled={isAnalyzing}
                                className="group w-full py-5 bg-leagle-accent text-black text-[11px] font-black uppercase tracking-[0.5em] hover:bg-white disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed transition-all shadow-glow flex items-center justify-center gap-3 active:scale-[0.98]"
                            >
                                {isAnalyzing ? (
                                    <>
                                        <Loader2 size={14} className="animate-spin" />
                                        Analyzing Regional Parallels...
                                    </>
                                ) : (
                                    <>
                                        <ExternalLink size={14} />
                                        Execute Deep Analysis
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* COMPACT HUD */}
            <div className="absolute top-6 left-6 z-50 select-none">
                <div className="bg-black/80 backdrop-blur-2xl px-5 py-4 border border-white/10 space-y-3 min-w-[200px]">
                    <div className="flex items-center gap-2.5">
                        <div className="w-1 h-5 bg-leagle-accent shadow-glow" />
                        <h2 className="text-[13px] font-black text-white tracking-[0.2em] uppercase italic leading-none">Neural Core</h2>
                    </div>
                    <div className="grid grid-cols-2 gap-4 pt-3 border-t border-white/5">
                        <div className="flex flex-col gap-0.5">
                            <span className="text-[7px] font-bold text-slate-600 uppercase">Mass</span>
                            <span className="text-[14px] font-black text-white">{data.summary?.cross_border_parallels || 0}</span>
                        </div>
                        <div className="flex flex-col gap-0.5">
                            <span className="text-[7px] font-bold text-slate-600 uppercase">Sync</span>
                            <span className="text-[14px] font-black text-emerald-500 uppercase tracking-tighter">Live</span>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    )
}
