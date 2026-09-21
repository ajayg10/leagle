"use client"

import { useState, useEffect, Suspense, useMemo } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { getRegulations, getAvailableJurisdictions } from '../api/client'
import { Search, Tag, Clock, ArrowUpRight, ChevronRight, Filter, Globe, ChevronDown } from 'lucide-react'
import RegulationDetail from './RegulationDetail'

const JURISDICTION_LABELS = {
    'IN': 'India (Bharat)',
    'US': 'United States (Federal)',
    'UK': 'United Kingdom',
    'GB': 'United Kingdom',
    'AU': 'Australia',
    'EU': 'European Union',
    'CA': 'Canada',
    'DE': 'Germany',
    'FR': 'France',
    'JP': 'Japan',
    'CN': 'China',
    'RU': 'Russia',
    'BR': 'Brazil',
    'SG': 'Singapore',
    'KR': 'South Korea',
    'MX': 'Mexico',
    'ZA': 'South Africa',
    'AE': 'UAE'
}

function RegulationListContent() {
    const searchParams = useSearchParams()
    const router = useRouter()

    const [regulations, setRegulations] = useState([])
    const [jurisdictions, setJurisdictions] = useState([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [selectedReg, setSelectedReg] = useState(null)

    // Handle incoming URL parameters (e.g. from Map click)
    useEffect(() => {
        const juris = searchParams.get('jurisdiction')
        if (juris) {
            setSearch(juris.toUpperCase())
        }
    }, [searchParams])

    // Load Data: Aggressive synchronization with normalized codes
    useEffect(() => {
        async function loadData() {
            setLoading(true)
            try {
                const juris = searchParams.get('jurisdiction')
                // Always fetch a broad set, but use backend filtering if requested
                const [regRes, jurisRes] = await Promise.all([
                    getRegulations(juris ? { jurisdiction: juris.toUpperCase() } : {}),
                    getAvailableJurisdictions()
                ])
                setRegulations(regRes.data || [])
                setJurisdictions(jurisRes.data || [])
            } catch (err) {
                console.error('Portfolio synchronization failure', err)
            } finally {
                setLoading(false)
            }
        }
        loadData()
    }, [searchParams])

    const filtered = useMemo(() => {
        if (!search) return regulations

        const term = search.trim()
        const termLower = term.toLowerCase()
        const isShortTerm = term.length <= 2

        return regulations.filter(r => {
            const rJuris = (r.jurisdiction || '').toLowerCase()
            const rTitle = (r.title || '').toLowerCase()

            // 1. Strict Jurisdictional Matching (Standardized + Fuzzy Name Mapping)
            let jurisdictionMatch = rJuris.includes(termLower)

            // Fuzzy mapping for common country names to ISO codes
            const COUNTRY_MAP = {
                'india': 'in', 'bharat': 'in',
                'usa': 'us', 'united states': 'us',
                'uk': 'uk', 'united kingdom': 'uk', 'britain': 'uk',
                'australia': 'au', 'europe': 'eu', 'european union': 'eu'
            }
            if (!jurisdictionMatch && COUNTRY_MAP[termLower] === rJuris) {
                jurisdictionMatch = true
            }

            // 2. Precise Title Matching
            let titleMatch = false
            if (isShortTerm) {
                // Word boundary to avoid "IN" matching "Influenza"
                const regex = new RegExp(`\\b${term}\\b`, 'i')
                titleMatch = regex.test(r.title || '')
            } else {
                titleMatch = rTitle.includes(termLower)
            }

            // 3. Category matching
            const categoryMatch = r.category?.toLowerCase() === termLower

            return titleMatch || jurisdictionMatch || categoryMatch
        })
    }, [regulations, search])

    const handleJurisdictionChange = (id) => {
        if (id === 'all') {
            setSearch('')
            router.push('/regulations')
        } else {
            const standardCode = id.toUpperCase()
            setSearch(standardCode)
            router.push(`/regulations?jurisdiction=${standardCode}`)
        }
    }

    if (loading && regulations.length === 0) return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-6">
            <div className="w-16 h-16 border-2 border-leagle-accent border-t-transparent rounded-full animate-spin"></div>
            <p className="text-gray-500 font-bold tracking-[0.4em] uppercase text-[10px] animate-pulse">Syncing Global Intelligence Layer...</p>
        </div>
    )

    return (
        <div className="max-w-7xl mx-auto space-y-12">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-8">
                <div className="space-y-6">
                    <div className="space-y-2">
                        <h2 className="text-5xl font-serif text-white tracking-tight italic">Jurisdictional Library</h2>
                        <div className="flex items-center gap-4 text-gray-500 font-medium uppercase text-[10px] tracking-widest">
                            <span className="text-leagle-accent">{filtered.length} Local matches</span>
                            <span className="w-1 h-1 rounded-full bg-slate-800" />
                            <span>Portfolio Mass: {regulations.length} Records</span>
                        </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                        <div className="relative group/select">
                            <Globe size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-leagle-accent/60 pointer-events-none group-focus-within/select:text-leagle-accent transition-colors" />
                            <select
                                className="pl-11 pr-12 py-3 bg-[#0a0a0a] border border-white/10 rounded-sm text-[11px] font-black uppercase tracking-widest text-white appearance-none hover:border-leagle-accent transition-all cursor-pointer outline-none ring-1 ring-transparent focus:ring-leagle-accent/20"
                                value={searchParams.get('jurisdiction') || 'all'}
                                onChange={(e) => handleJurisdictionChange(e.target.value)}
                            >
                                <option value="all">Global Oversight (All Regions)</option>
                                {jurisdictions
                                    .filter(j => j.id !== 'all' && j.id !== 'Global Oversight') // Prevent redundancy
                                    .map(j => (
                                        <option key={j.id} value={j.id}>
                                            {JURISDICTION_LABELS[j.id] || j.id} ({j.count})
                                        </option>
                                    ))}
                            </select>
                            <ChevronDown size={14} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-600 group-hover/select:text-leagle-accent pointer-events-none transition-colors" />
                        </div>

                        {search && (
                            <div className="flex items-center gap-3 px-4 py-3 bg-leagle-accent/10 border border-leagle-accent/20 rounded-sm animate-in fade-in zoom-in duration-300">
                                <Filter size={10} className="text-leagle-accent" />
                                <span className="text-[10px] font-black text-white uppercase tracking-widest">{search}</span>
                                <button onClick={() => handleJurisdictionChange('all')} className="ml-2 hover:text-white text-leagle-accent/60 transition-colors">
                                    <ArrowUpRight size={10} className="rotate-45" />
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                <div className="relative w-full lg:w-[450px] group">
                    <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-leagle-accent transition-colors" size={20} />
                    <input
                        type="search"
                        placeholder="Search regulation titles..."
                        className="w-full pl-16 pr-10 py-5 bg-[#0a0a0a] border border-white/10 rounded-sm text-gray-200 placeholder-gray-700 focus:border-leagle-accent transition-all outline-none text-base"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-px bg-white/5 border border-white/5 shadow-2xl">
                {filtered.map((reg) => (
                    <div
                        key={reg.id}
                        onClick={() => setSelectedReg(reg)}
                        className="bg-leagle-bg p-12 group hover:bg-white/[0.03] transition-all duration-300 cursor-pointer relative overflow-hidden flex flex-col justify-between h-full border-b border-r border-white/5 hover:z-10"
                    >
                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-leagle-accent/15 to-transparent flex items-center justify-center translate-x-16 -translate-y-16 group-hover:translate-x-12 group-hover:-translate-y-12 transition-transform duration-500">
                            <ArrowUpRight className="text-leagle-accent opacity-0 group-hover:opacity-100 transition-opacity" size={24} />
                        </div>

                        <div className="space-y-8">
                            <div className="flex items-center gap-4">
                                <span className="px-3 py-1.5 rounded-sm text-[10px] font-black uppercase tracking-[0.4em] shadow-lg bg-leagle-accent/20 text-leagle-accent border border-leagle-accent/30">
                                    {JURISDICTION_LABELS[reg.jurisdiction] || reg.jurisdiction || 'Global Oversight'}
                                </span>
                                <span className="px-3 py-1.5 bg-white/5 border border-white/10 text-gray-400 rounded-sm text-[10px] font-black uppercase tracking-[0.4em]">
                                    {reg.category || 'General'}
                                </span>
                            </div>

                            <h3 className="text-2xl font-serif text-white group-hover:text-leagle-accent transition-colors leading-tight italic tracking-wide">
                                {reg.title}
                            </h3>

                            <p className="text-base text-gray-500 font-medium line-clamp-3 italic leading-relaxed opacity-80">
                                {reg.raw_text?.slice(0, 250)}...
                            </p>
                        </div>

                        <div className="flex items-center justify-between pt-12 border-t border-white/5 mt-12 bg-gradient-to-t from-black/20 to-transparent p-2 -m-2">
                            <div className="flex items-center gap-10">
                                <div className="flex items-center gap-3 text-[11px] font-black uppercase tracking-[0.2em] text-gray-600 group-hover:text-gray-400 transition-colors">
                                    <Tag size={14} className="text-leagle-accent/40" />
                                    {reg.id.slice(0, 8)}
                                </div>
                                <div className="flex items-center gap-3 text-[11px] font-black uppercase tracking-[0.2em] text-gray-600 group-hover:text-gray-400 transition-colors">
                                    <Clock size={14} className="text-leagle-accent/40" />
                                    {new Date(reg.created_at).toLocaleDateString()}
                                </div>
                            </div>
                            <div className="flex items-center gap-3 text-leagle-accent font-black text-[11px] uppercase tracking-[0.3em] opacity-0 group-hover:opacity-100 transition-all translate-x-8 group-hover:translate-x-0">
                                Deep Analysis <ChevronRight size={18} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {selectedReg && (
                <RegulationDetail
                    regulation={selectedReg}
                    onClose={() => setSelectedReg(null)}
                />
            )}

            {filtered.length === 0 && (
                <div className="glass-card py-56 text-center space-y-8 bg-[#0a0a0a] border-white/5">
                    <Search size={64} className="mx-auto text-leagle-accent/10 animate-pulse" />
                    <div className="space-y-4">
                        <p className="text-3xl font-serif text-white italic tracking-widest">No Matches Identified</p>
                        <p className="text-gray-600 font-medium max-w-md mx-auto text-sm italic leading-relaxed uppercase tracking-tighter">
                            The current neural snapshot for <span className="text-leagle-accent">{search}</span> is empty.
                            Standardized synchronization or manual ingestion required.
                        </p>
                    </div>
                    <button
                        onClick={() => handleJurisdictionChange('all')}
                        className="px-8 py-4 bg-white/5 hover:bg-leagle-accent/10 border border-white/10 hover:border-leagle-accent/30 text-white text-[10px] font-black uppercase tracking-[0.4em] transition-all"
                    >
                        Reset Global Oversight
                    </button>
                </div>
            )}
        </div>
    )
}

export default function RegulationList() {
    return (
        <Suspense fallback={<div>Loading Neural Library...</div>}>
            <RegulationListContent />
        </Suspense>
    )
}
