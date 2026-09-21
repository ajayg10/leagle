"use client"

import { useState } from 'react'
import Image from 'next/image'
import { askQuestion } from '../api/client'
import { Search, Loader2, ShieldCheck, MessageSquare, History } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function SemanticSearch() {
    const [query, setQuery] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)

    const handleSearch = async () => {
        if (!query.trim()) return
        setLoading(true)
        try {
            const { data } = await askQuestion(query)
            setResult(data)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="max-w-5xl mx-auto min-h-[85vh] space-y-8 sm:space-y-12 animate-in fade-in duration-1000 pb-20">
            <div className="text-center space-y-4">
                <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-leagle-accent/10 rounded-3xl mb-2 sm:mb-4 text-leagle-accent shadow-[0_0_40px_rgba(56,189,248,0.1)] border border-leagle-accent/20">
                    <Image src="/logo.png" alt="Leagle Logo" width={40} height={40} className="w-8 h-8 sm:w-10 sm:h-10" />
                </div>
                <h2 className="text-3xl sm:text-5xl font-serif text-white tracking-tight italic px-2">
                    Diagnostic <span className="text-leagle-accent underline decoration-leagle-accent/30">Intelligence</span>
                </h2>
                <p className="text-gray-400 max-w-lg mx-auto text-sm sm:text-lg font-medium leading-relaxed px-4">
                    Search regulations and guidance with referenced answers from your indexed sources.
                </p>
            </div>

            <div className="relative group p-px bg-white/5 shadow-2xl mx-2 sm:mx-0">
                <div className="relative flex flex-col sm:flex-row gap-2 sm:gap-4 bg-leagle-bg p-2 rounded-sm border border-white/10">
                    <input
                        className="flex-1 bg-transparent border-0 px-4 sm:px-8 py-4 sm:py-5 text-base sm:text-xl text-white placeholder-gray-600 focus:outline-none placeholder-italic"
                        placeholder="Search regulations..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    />
                    <button
                        onClick={handleSearch}
                        disabled={loading}
                        className="w-full sm:w-auto bg-leagle-accent text-black font-black text-[10px] tracking-[0.2em] uppercase px-6 sm:px-10 py-4 sm:py-5 min-h-[48px] flex items-center justify-center gap-2 sm:gap-3 rounded-sm hover:bg-white transition-all shadow-lg"
                    >
                        {loading ? <Loader2 className="animate-spin" size={20} /> : <Search size={20} />}
                        Search
                    </button>
                </div>
            </div>

            {loading && (
                <div className="flex flex-col items-center justify-center py-12 sm:py-20 space-y-6">
                    <div className="relative">
                        <div className="w-16 h-16 sm:w-20 sm:h-20 border-4 border-white/5 rounded-full" />
                        <div className="absolute inset-0 border-t-4 border-leagle-accent rounded-full animate-spin" />
                    </div>
                    <p className="text-[10px] sm:text-xs font-black uppercase tracking-[0.3em] text-leagle-accent animate-pulse text-center">Retrieving source matches</p>
                </div>
            )}

            {result && !loading && (
                <div className="space-y-8 sm:space-y-10 animate-in slide-in-from-bottom-8 duration-700 px-2 sm:px-0">
                    <div className="glass-card p-6 sm:p-10 relative overflow-hidden rounded-sm border-white/5">
                        <div className="absolute -top-24 -right-24 w-64 h-64 sm:w-96 sm:h-96 bg-leagle-accent/5 blur-3xl rounded-full" />

                        <div className="relative z-10 space-y-6 sm:space-y-8">
                            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-white/5 pb-4 sm:pb-6 gap-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-leagle-accent/10 rounded-lg shrink-0">
                                        <MessageSquare size={16} className="text-leagle-accent" />
                                    </div>
                                    <h3 className="text-[10px] sm:text-xs font-black uppercase tracking-widest text-gray-400">Response Summary</h3>
                                </div>
                                {result.local_ml_risk && (
                                    <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 shrink-0">
                                        <span className="text-[9px] sm:text-[10px] font-black uppercase text-gray-500 tracking-tighter">Risk:</span>
                                        <span className={`text-[9px] sm:text-[10px] font-black uppercase ${result.local_ml_risk === 'High' ? 'text-red-500' :
                                            result.local_ml_risk === 'Medium' ? 'text-orange-400' :
                                                'text-green-400'
                                            }`}>
                                            {result.local_ml_risk}
                                        </span>
                                    </div>
                                )}
                            </div>

                            <div className="prose prose-invert max-w-none">
                                <div className="text-base sm:text-xl text-gray-200 leading-relaxed font-serif italic selection:bg-leagle-accent/30 prose-p:mb-4 sm:prose-p:mb-6 border-l-2 border-leagle-accent/30 pl-4 sm:pl-8 bg-white/2 py-3 sm:py-4 overflow-x-hidden">
                                    <ReactMarkdown>{result.answer}</ReactMarkdown>
                                </div>
                            </div>
                        </div>
                    </div>

                    {result.sources?.length > 0 && (
                        <div className="space-y-4 sm:space-y-6">
                            <h3 className="text-[10px] sm:text-xs font-black uppercase tracking-[0.2em] text-gray-500 px-2 sm:px-4 flex items-center gap-2">
                                <History size={14} className="text-leagle-accent" />
                                Supporting Sources
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
                                {result.sources.map((src, i) => (
                                    <div key={i} className="glass-card p-4 sm:p-6 bg-white/2 hover:bg-white/4 transition-all group rounded-sm border-white/5">
                                        <div className="flex justify-between items-start gap-4 mb-3 sm:mb-4">
                                            <span className="text-[10px] sm:text-[11px] font-black uppercase tracking-widest text-gray-400 line-clamp-2 group-hover:text-leagle-accent transition-colors italic">{src.title}</span>
                                            <span className="text-[8px] sm:text-[9px] font-black tracking-tighter text-leagle-accent bg-leagle-accent/10 px-2 py-1 rounded-sm border border-leagle-accent/20 shrink-0">
                                                {(src.score * 100).toFixed(0)}% MATCH
                                            </span>
                                        </div>
                                        <div className="w-full bg-white/5 rounded-full h-1 overflow-hidden">
                                            <div
                                                className="bg-gradient-to-r from-leagle-accent to-blue-600 h-full transition-all duration-1000 ease-out shadow-[0_0_10px_#38bdf8]"
                                                style={{ width: `${src.score * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
