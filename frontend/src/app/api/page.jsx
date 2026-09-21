'use client';

import LandingNavbar from '../components/LandingNavbar';
import { Show, SignInButton } from '@clerk/nextjs';
import { Terminal, BookOpen, Key, Link as LinkIcon, Shield, Zap, Check, Plus, Copy, RefreshCw, Search, ArrowRight, Play, Trash2, Lock, Code, Cpu, Activity, Globe, Database } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE = '/api/v1/neural';
const PUBLIC_API_BASE = 'https://leagle-xi.vercel.app/api/v1/neural';

export default function APIPage() {
    const [keys, setKeys] = useState([]);
    const [selectedKey, setSelectedKey] = useState('LGL_PROTOCOL_DEFAULT_SANDBOX');
    const [query, setQuery] = useState('UK financial compliance 2026');
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isFetchingKeys, setIsFetchingKeys] = useState(true);
    const [copied, setCopied] = useState(null);
    const [newKeyName, setNewKeyName] = useState('');
    const [showKeyModal, setShowKeyModal] = useState(false);
    const [manualKey, setManualKey] = useState('');
    const [useManualKey, setUseManualKey] = useState(false);
    const [activeSection, setActiveSection] = useState('docs');
    const [docSection, setDocSection] = useState('overview');

    useEffect(() => {
        fetchKeys();
    }, []);

    const navigateToDoc = (section) => {
        setActiveSection('docs');
        setDocSection(section);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const fetchKeys = async () => {
        setIsFetchingKeys(true);
        try {
            const response = await axios.get(`${API_BASE}/keys`);
            setKeys(response.data);
        } catch (error) {
            console.error('Failed to fetch keys:', error);
        } finally {
            setIsFetchingKeys(false);
        }
    };

    const handleGenerateKey = async () => {
        if (!newKeyName) return;
        try {
            const response = await axios.post(`${API_BASE}/keys`, { name: newKeyName });
            setKeys([response.data, ...keys]);
            setNewKeyName('');
            setShowKeyModal(false);
        } catch (error) {
            console.error('Failed to generate key:', error);
        }
    };

    const handleDeleteKey = async (id) => {
        try {
            await axios.delete(`${API_BASE}/keys/${id}`);
            setKeys(keys.filter(k => k.id !== id));
            if (activeKey === keys.find(k => k.id === id)?.key) {
                setUseManualKey(false);
                setSelectedKey('LGL_PROTOCOL_DEFAULT_SANDBOX');
            }
        } catch (error) {
            console.error('Failed to delete key:', error);
        }
    };

    const handleCopy = (text) => {
        navigator.clipboard.writeText(text);
        setCopied(text);
        setTimeout(() => setCopied(null), 2000);
    };

    const activeKey = useManualKey ? manualKey : selectedKey;

    const runNeuralTest = async () => {
        if (!activeKey) return;
        setIsLoading(true);
        try {
            const response = await axios.get(`${API_BASE}/search?query=${encodeURIComponent(query)}&limit=3`, {
                headers: { 'X-Protocol-Key': activeKey }
            });
            setResults(response.data);
        } catch (error) {
            setResults(error.response?.data || { error: 'Neutral Link Failure' });
        } finally {
            setIsLoading(false);
        }
    };

    const getSnippets = () => {
        const keyToUse = activeKey || 'YOUR_PROTOCOL_KEY';
        const searchUrl = `${PUBLIC_API_BASE}/search?query=${encodeURIComponent(query)}`;
        return {
            curl: `curl -H "X-Protocol-Key: ${keyToUse}" "${searchUrl}"`,
            python: `import requests\n\nurl = "${searchUrl}"\nheaders = {"X-Protocol-Key": "${keyToUse}"}\n\nresponse = requests.get(url, headers=headers)\nprint(response.json())`,
            javascript: `const response = await fetch("${searchUrl}", {\n  headers: { "X-Protocol-Key": "${keyToUse}" }\n});\nconst data = await response.json();\nconsole.log(data);`
        };
    };

    const categories = [
        {
            title: 'Introduction',
            items: [
                { id: 'overview', label: 'Overview' },
                { id: 'architecture', label: 'Architecture' },
                { id: 'concepts', label: 'Core Concepts' }
            ]
        },
        {
            title: 'Getting Started',
            items: [
                { id: 'quickstart', label: 'Quickstart Tutorial' },
                { id: 'auth-security', label: 'Auth & Security' },
                { id: 'first-search', label: 'Your First Search' }
            ]
        },
        {
            title: 'Advanced Guides',
            items: [
                { id: 'neural-search-deep', label: 'Neural Search Deep-Dive' },
                { id: 'key-lifecycle', label: 'Key Lifecycle' },
                { id: 'compliance-audit', label: 'Compliance Audit' }
            ]
        },
        {
            title: 'Reference',
            items: [
                { id: 'api-reference', label: 'API Reference' },
                { id: 'json-schema', label: 'JSON Schema' },
                { id: 'error-codes', label: 'Error Codes' },
                { id: 'rate-limits', label: 'Rate Limits' }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-[#050505] text-gray-300 selection:bg-leagle-accent/30 selection:text-white pb-32">
            <LandingNavbar />

            {/* Content Layout */}
            <div className="max-w-[1400px] mx-auto px-6 pt-32 grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-16">

                {/* STICKY SIDEBAR - High Density */}
                <aside className="hidden lg:block space-y-10 h-fit sticky top-32 overflow-y-auto max-h-[calc(100vh-160px)] pr-4 scrollbar-hide">
                    {categories.map((cat, idx) => (
                        <section key={idx} className="space-y-4">
                            <h3 className="text-[9px] font-black uppercase tracking-[0.25em] text-white/30 border-b border-white/5 pb-2">{cat.title}</h3>
                            <nav className="flex flex-col gap-1">
                                {cat.items.map(item => (
                                    <button
                                        key={item.id}
                                        onClick={() => navigateToDoc(item.id)}
                                        className={`text-sm font-serif italic text-left py-2 px-3 rounded-sm transition-all duration-300 border-l-2 ${activeSection === 'docs' && docSection === item.id ? 'text-white border-leagle-accent bg-white/[0.03] translate-x-1' : 'text-gray-500 border-transparent hover:text-white hover:bg-white/[0.01]'}`}
                                    >
                                        {item.label}
                                    </button>
                                ))}
                            </nav>
                            {cat.title === 'Reference' && (
                                <div className="pt-8 mt-8 border-t border-white/5">
                                    <h3 className="text-[9px] font-black uppercase tracking-[0.25em] text-leagle-accent flex items-center gap-2 mb-4">
                                        <Activity size={12} /> Interactive
                                    </h3>
                                    <nav className="flex flex-col gap-1">
                                        <button onClick={() => setActiveSection('console')} className={`text-sm font-serif italic text-left py-2 px-3 border-l-2 transition-all ${activeSection === 'console' ? 'text-white border-leagle-accent bg-leagle-accent/5 translate-x-1' : 'text-gray-500 border-transparent hover:text-white hover:bg-white/[0.01]'}`}>Developer Console</button>
                                        <button onClick={() => { setActiveSection('docs'); setDocSection('overview'); }} className={`text-sm font-serif italic text-left py-2 px-3 border-l-2 transition-all ${activeSection === 'docs' ? 'text-white border-leagle-accent bg-white/[0.03] translate-x-1' : 'text-gray-500 border-transparent hover:text-white hover:bg-white/[0.01]'}`}>API Reference</button>
                                    </nav>
                                </div>
                            )}
                        </section>
                    ))}
                </aside>

                {/* MAIN CONTENT AREA */}
                <article className="space-y-32">

                    {activeSection === 'docs' ? (
                        <div className="space-y-40 pb-40">
                            {/* INTRODUCTION CATEGORY */}
                            {docSection === 'overview' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-6">
                                        <div className="flex items-center gap-2 text-leagle-accent">
                                            <Globe size={16} />
                                            <span className="text-[10px] font-black uppercase tracking-widest">Protocol v4.2.0</span>
                                        </div>
                                        <h1 className="text-7xl font-serif italic text-white leading-[0.85] tracking-tighter">The Neural <span className="text-gradient">Interface</span></h1>
                                        <p className="text-xl text-gray-400 font-serif italic leading-relaxed max-w-2xl">
                                            A high-fidelity, institutional-grade protocol for programmatic regulatory inference and dynamic compliance automation.
                                        </p>
                                    </header>
                                    <div className="space-y-8 pt-16 border-t border-white/5">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                                            <div className="space-y-4">
                                                <h3 className="text-xl font-serif italic text-white">Mission Statement</h3>
                                                <p className="text-gray-500 font-serif italic leading-relaxed text-sm">
                                                    Leagle bridges the gap between static legal frameworks and active AI operations. Our protocol ensures that every automated decision is grounded in verifiable, multi-jurisdictional compliance data. We believe that AI autonomy should never come at the cost of legal certainty.
                                                </p>
                                            </div>
                                            <div className="space-y-4">
                                                <h3 className="text-xl font-serif italic text-white">Institutional Grade</h3>
                                                <p className="text-gray-500 font-serif italic leading-relaxed text-sm">
                                                    Built for scale, security, and precision. We provide isolated vector environments and immutable audit trails for every inference request, ensuring that your data remains sovereign and your decisions remain defensible.
                                                </p>
                                            </div>
                                        </div>
                                        <div className="p-10 bg-white/[0.02] border border-white/5 rounded-sm space-y-6">
                                            <h3 className="text-xl font-serif italic text-white">Technical Philosophy</h3>
                                            <p className="text-gray-500 font-serif italic leading-relaxed text-sm">
                                                The Leagle Protocol is designed on three core pillars: **Precision**, **Provenance**, and **Privacy**. Unlike generic LLMs that may hallucinate legal advice, our Neural Interface utilizes high-precision retrieval mechanisms to ensure that every response is derived directly from authoritative regulatory sources.
                                            </p>
                                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-4">
                                                <div className="space-y-2">
                                                    <div className="text-leagle-accent text-[10px] font-black uppercase tracking-widest">Precision</div>
                                                    <div className="text-xs text-gray-400 font-serif italic">Sub-millisecond semantic matching against active legislation.</div>
                                                </div>
                                                <div className="space-y-2">
                                                    <div className="text-leagle-accent text-[10px] font-black uppercase tracking-widest">Provenance</div>
                                                    <div className="text-xs text-gray-400 font-serif italic">Every claim backed by a cryptographically signed source citation.</div>
                                                </div>
                                                <div className="space-y-2">
                                                    <div className="text-leagle-accent text-[10px] font-black uppercase tracking-widest">Privacy</div>
                                                    <div className="text-xs text-gray-400 font-serif italic">Zero-data retention for sensitive institutional queries.</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {docSection === 'architecture' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Cpu size={14} /> System Design
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white">Neural Core</h2>
                                    </header>
                                    <div className="space-y-16 pt-12 border-t border-white/5">
                                        <div className="space-y-6">
                                            <p className="text-gray-400 font-serif italic leading-relaxed">
                                                The Leagle architecture is centered around a multi-layered Neural Link that prioritizes citation accuracy over generative creativity. Our engine operates on a stateless, vector-first model designed for massive horizontal scaling.
                                            </p>
                                            <div className="p-10 bg-white/[0.02] border border-white/5 rounded-sm">
                                                <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                                                    <div className="text-center space-y-2">
                                                        <div className="text-leagle-accent text-xs font-black">REGULATORY FEED</div>
                                                        <div className="text-[10px] text-gray-600 font-mono">Real-time Ingestion</div>
                                                    </div>
                                                    <ArrowRight className="text-white/10 hidden md:block" />
                                                    <div className="text-center space-y-2 px-8 py-4 border border-leagle-accent/20 bg-leagle-accent/5 rounded-sm">
                                                        <div className="text-white text-xs font-black">VECTOR SYNC</div>
                                                        <div className="text-[10px] text-gray-400 font-mono italic whitespace-nowrap">Qdrant Neural Engine</div>
                                                    </div>
                                                    <ArrowRight className="text-white/10 hidden md:block" />
                                                    <div className="text-center space-y-2">
                                                        <div className="text-emerald-400 text-xs font-black">NEURAL API</div>
                                                        <div className="text-[10px] text-gray-600 font-mono">JSON/gRPC Out</div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                                            <div className="space-y-4">
                                                <h3 className="text-xl font-serif italic text-white">RAG Strategy</h3>
                                                <p className="text-gray-500 font-serif italic text-sm leading-relaxed">
                                                    Every search request triggers a semantic retrieval from the active compliance vector space. We use advanced Retrieval-Augmented Generation (RAG) to ground every model response in ground-truth legal documents. The results are filtered through an institutional context mask, ensuring that only relevant, high-confidence citations are surfaced.
                                                </p>
                                            </div>
                                            <div className="space-y-4">
                                                <h3 className="text-xl font-serif italic text-white">Edge Caching</h3>
                                                <p className="text-gray-500 font-serif italic text-sm leading-relaxed">
                                                    To provide sub-100ms response times for global deployments, the Leagle protocol utilizes a distributed edge caching layer for frequent regulatory lookups, while maintaining strict consistency with the primary vector shard.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {docSection === 'concepts' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <BookOpen size={14} /> Fundamental
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white">Core Concepts</h2>
                                    </header>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-12 border-t border-white/5">
                                        {[
                                            { t: 'Neural Link', d: 'The bidirectional, authenticated connection between your institutional tenant and our compliance vector engines. It facilitates real-time data sync and inference exchange.' },
                                            { t: 'Protocol Key', d: 'A high-entropy institutional credential required to access specialized regulatory datasets. These keys are scoped to specific workspaces and jurisdictions.' },
                                            { t: 'Active Vector', d: 'A live-updated regulatory embedding representing a specific jurisdiction (e.g., UK FCA) or legal topic. Active vectors are continuously re-indexed as laws change.' },
                                            { t: 'Audit Trail', d: 'An immutable, cryptographically hashed log of every API interaction. It provides full data sovereignty and ensures decisions are always auditable by regulators.' },
                                            { t: 'Workspace Scope', d: 'A logical isolation boundary within your tenant that segregates data, keys, and audit trails for different departments or legal entities.' },
                                            { t: 'Inference Quota', d: 'The allocated computational budget for neural searches, measured in Request Units (RU) to ensure fair resource distribution across partners.' }
                                        ].map((c, i) => (
                                            <div key={i} className="p-8 bg-white/[0.01] border border-white/5 rounded-sm space-y-3 group hover:border-leagle-accent/20 transition-all">
                                                <h4 className="text-white font-serif italic font-bold group-hover:text-leagle-accent transition-colors">{c.t}</h4>
                                                <p className="text-gray-500 text-sm font-serif italic leading-relaxed">{c.d}</p>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                            )}

                            {/* GETTING STARTED CATEGORY */}
                            {docSection === 'quickstart' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Zap size={14} /> Get Up & Running
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white leading-tight">Quickstart <span className="text-gradient">Tutorial</span></h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Follow this three-step guide to establish your first Neural Link and begin querying the global regulatory vector space.</p>
                                    </header>
                                    <div className="space-y-20 pt-12 border-t border-white/5">
                                        <div className="flex gap-10">
                                            <div className="w-12 h-12 rounded-full border border-leagle-accent/30 flex items-center justify-center text-xs font-black text-leagle-accent shrink-0 mt-2">01</div>
                                            <div className="space-y-6">
                                                <div className="space-y-2">
                                                    <h3 className="text-2xl font-serif italic text-white">Issue Your Institutional Key</h3>
                                                    <p className="text-gray-500 font-serif italic leading-relaxed">
                                                        Access the <button onClick={() => setActiveSection('console')} className="text-leagle-accent underline">Developer Console</button> and generate a new Protocol Key. This key serves as your institutional identity and is required for all authenticated requests. Ensure that keys are scoped appropriately for your development environment.
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex gap-10">
                                            <div className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center text-xs font-black text-gray-500 shrink-0 mt-2">02</div>
                                            <div className="space-y-6 w-full">
                                                <div className="space-y-2">
                                                    <h3 className="text-2xl font-serif italic text-white">Initialize Your First Link</h3>
                                                    <p className="text-gray-500 font-serif italic leading-relaxed">
                                                        Execute a semantic search against our UK Financial Compliance 2026 dataset. Unlike traditional keyword search, this query is processed using our neural engine to find contextually relevant regulatory requirements.
                                                    </p>
                                                </div>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    <div className="p-6 bg-black border border-white/5 rounded-sm relative group">
                                                        <div className="text-[8px] font-black uppercase text-gray-600 mb-4 tracking-widest">cURL Request</div>
                                                        <code className="text-[10px] font-mono text-indigo-400 whitespace-pre leading-relaxed">
                                                            curl -H "X-Protocol-Key: YOUR_KEY" \<br />
                                                            "https://leagle-xi.vercel.app/api/v1/neural/search?query=2026%20compliance"
                                                        </code>
                                                        <button onClick={() => handleCopy('curl -H "X-Protocol-Key: YOUR_KEY" "https://leagle-xi.vercel.app/api/v1/neural/search?query=2026%20compliance"')} className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                                            <Copy size={14} className="text-gray-600 hover:text-white" />
                                                        </button>
                                                    </div>
                                                    <div className="p-6 bg-black border border-white/5 rounded-sm relative group">
                                                        <div className="text-[8px] font-black uppercase text-gray-600 mb-4 tracking-widest">Python SDK</div>
                                                        <code className="text-[10px] font-mono text-indigo-400 whitespace-pre leading-relaxed">
                                                            import requests<br />
                                                            url = "https://leagle-xi.vercel.app/api/v1/neural/search"<br />
                                                            headers = &#123;"X-Protocol-Key": "YOUR_KEY"&#125;<br />
                                                            params = &#123;"query": "2026 compliance"&#125;<br />
                                                            res = requests.get(url, headers=headers, params=params)
                                                        </code>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex gap-10">
                                            <div className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center text-xs font-black text-gray-500 shrink-0 mt-2">03</div>
                                            <div className="space-y-6">
                                                <div className="space-y-2">
                                                    <h3 className="text-2xl font-serif italic text-white">Parse Neural Data</h3>
                                                    <p className="text-gray-500 font-serif italic leading-relaxed">
                                                        Process the structured JSON response. Each search result includes a `score` field (semantic confidence) and `metadata` containing source citations. Use these to automate compliance determinations within your internal systems.
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {docSection === 'auth-security' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Lock size={14} /> Protection
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white">Auth & Security</h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">The Leagle protocol implements multi-layer defense strategies to ensure institutional data isolation and cryptographic auditability.</p>
                                    </header>
                                    <div className="space-y-12 pt-12 border-t border-white/5">
                                        <div className="space-y-6">
                                            <h3 className="text-xl font-serif italic text-white">Header Authentication</h3>
                                            <p className="text-gray-400 font-serif italic leading-relaxed">
                                                All requests to the Neural Interface MUST include the <code className="text-indigo-400 px-1.5 py-0.5 rounded bg-indigo-400/10">X-Protocol-Key</code> header. We do not support Bearer tokens at this layer to maintain stateless institutional isolation and prevent traditional session-based vulnerabilities.
                                            </p>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                <div className="p-6 bg-white/[0.02] border border-white/5 rounded-sm space-y-2">
                                                    <div className="text-white text-xs font-black uppercase tracking-widest">Key Prefix</div>
                                                    <p className="text-gray-500 text-xs font-serif italic">Keys always start with `LGL_` followed by the environment identifier (e.g., `LGL_PRD_`).</p>
                                                </div>
                                                <div className="p-6 bg-white/[0.02] border border-white/5 rounded-sm space-y-2">
                                                    <div className="text-white text-xs font-black uppercase tracking-widest">Rate Calculation</div>
                                                    <p className="text-gray-500 text-xs font-serif italic">Authentication events are logged for billing and security auditing in near real-time.</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="p-8 bg-amber-500/[0.03] border border-amber-500/20 rounded-sm flex gap-6">
                                            <Shield size={24} className="text-amber-500 shrink-0" />
                                            <div className="space-y-2">
                                                <h5 className="text-amber-500 text-[10px] font-black uppercase tracking-widest">Security Advisory</h5>
                                                <p className="text-gray-500 text-xs font-serif italic leading-relaxed">
                                                    NEVER hardcode Protocol Keys in frontend applications. Use environment variables and server-side proxies to protect your credentials. We recommend rotating production keys every 90 days.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {docSection === 'first-search' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Search size={14} /> Validation
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white">Your First Search</h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Validate your link connectivity and explore the structure of neural-verified compliance data.</p>
                                    </header>
                                    <div className="space-y-12 pt-12 border-t border-white/5">
                                        <p className="text-gray-400 font-serif italic leading-relaxed">
                                            Let's run a test query to verify your Neural Link connectivity. Use the sample below to retrieve the latest regulatory updates. Note the returned `latency` and `score` fields which are critical for institutional performance monitoring.
                                        </p>
                                        <div className="space-y-6">
                                            <div className="flex justify-between items-center px-4 py-2 bg-white/[0.02] border-x border-t border-white/5 rounded-t-sm">
                                                <span className="text-[10px] font-black uppercase text-gray-600 tracking-widest">Template: Search Req</span>
                                                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50 blink-slow" />
                                            </div>
                                            <div className="p-10 bg-[#0a0a0a] border border-white/5 rounded-b-sm">
                                                <pre className="text-xs font-mono text-indigo-400 leading-relaxed">
                                                    {`GET /api/v1/neural/search?query=FinReg%202026&limit=1 HTTP/1.1\nHost: leagle-xi.vercel.app\nX-Protocol-Key: LGL_PROTOCOL_SANDBOX`}
                                                </pre>
                                            </div>
                                        </div>
                                        <div className="space-y-6">
                                            <h3 className="text-xl font-serif italic text-white">Expected Schema</h3>
                                            <p className="text-gray-500 text-sm font-serif italic leading-relaxed">
                                                The response will always follow the institutional JSON schema, including an `audit_trail_id` which must be stored for future compliance reviews.
                                            </p>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {/* ADVANCED GUIDES CATEGORY */}
                            {docSection === 'neural-search-deep' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Activity size={14} /> High Precision
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white leading-tight">Neural <span className="text-gradient">Deep-Dive</span></h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Explore the underlying mechanics of our semantic retrieval engine and how it achieves institutional-grade accuracy.</p>
                                    </header>
                                    <div className="space-y-16 pt-12 border-t border-white/5">
                                        <div className="space-y-6">
                                            <h3 className="text-2xl font-serif italic text-white text-gradient">Precision vs. Generative Creativity</h3>
                                            <p className="text-gray-500 font-serif italic leading-relaxed">
                                                Unlike standard LLMs that generate responses based on probabilistic token prediction, the Leagle Neural Engine operates on a strict **Retrieval-Grounding** model. We prioritize the retrieval of exact regulatory matches over the generation of "natural" sounding but potentially inaccurate summaries.
                                            </p>
                                        </div>
                                        <div className="space-y-6">
                                            <h4 className="text-xl font-serif italic text-white">Understanding Relevance Scores</h4>
                                            <p className="text-gray-500 font-serif italic leading-relaxed">
                                                Matches returned by the Neural Engine include a precision score from 0.0 to 1.0. This score represents the semantic cosine similarity between the query embedding and the regulatory document fragment.
                                            </p>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="p-8 bg-white/[0.02] border border-white/5 rounded-sm space-y-4">
                                                <div className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">0.85 - 1.0</div>
                                                <div className="text-sm font-serif italic font-medium text-white">Direct Compliance Match</div>
                                                <p className="text-gray-600 text-xs font-serif italic leading-relaxed">Explicit reference to the queried regulation or framework. High confidence for automated remediation.</p>
                                            </div>
                                            <div className="p-8 bg-white/[0.02] border border-white/5 rounded-sm space-y-4">
                                                <div className="text-[10px] font-black text-amber-400 uppercase tracking-widest">0.60 - 0.84</div>
                                                <div className="text-sm font-serif italic font-medium text-white">Contextual Association</div>
                                                <p className="text-gray-600 text-xs font-serif italic leading-relaxed">Relates to the core concept but may involve cross-jurisdictional nuances. Requires human-in-the-loop verification.</p>
                                            </div>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {docSection === 'key-lifecycle' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <RefreshCw size={14} /> Maintenance
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white">Key Lifecycle</h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Manage the rotation and revocation of institutional credentials to maintain a resilient security posture.</p>
                                    </header>
                                    <div className="space-y-12 pt-12 border-t border-white/5">
                                        <div className="space-y-4">
                                            <h3 className="text-xl font-serif italic text-white italic">Rotation Strategy</h3>
                                            <p className="text-gray-400 font-serif italic leading-relaxed">
                                                Institutional keys are valid for a maximum of 90 days. We recommend a staggered rotation strategy: generate a new key 7 days before the old one expires, update your internal service configurations, and verify the new link before revoking the legacy key.
                                            </p>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="p-6 bg-white/[0.02] border border-white/5 rounded-sm space-y-2">
                                                <div className="text-white text-xs font-black uppercase tracking-widest">Grace Periods</div>
                                                <p className="text-gray-600 text-xs font-serif italic">Revoked keys maintain a 24-hour "cooling off" period where they return `403 REVOKED` with a reminder to update endpoints.</p>
                                            </div>
                                            <div className="p-6 bg-white/[0.02] border border-white/5 rounded-sm space-y-2">
                                                <div className="text-white text-xs font-black uppercase tracking-widest">Automation</div>
                                                <p className="text-gray-600 text-xs font-serif italic">Use our Management API to programmatically cycle keys via secure vault integrations like HashiCorp or AWS Secrets Manager.</p>
                                            </div>
                                        </div>
                                        <div className="p-6 bg-blue-500/[0.03] border border-blue-500/20 rounded-sm">
                                            <p className="text-gray-500 text-xs font-serif italic font-bold uppercase tracking-widest">Production Note: Revocation is instantaneous across all global shards once confirmed.</p>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {docSection === 'compliance-audit' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Shield size={14} /> Sovereignty
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white leading-tight">Compliance Audit</h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Immutable logging and data provenance for regulatory accountability.</p>
                                    </header>
                                    <div className="space-y-12 pt-12 border-t border-white/5">
                                        <p className="text-gray-400 font-serif italic leading-relaxed">
                                            Leagle ensures full observability into your AI-driven decision tree. Every request is immutably logged with a unique `audit_trail_id`, allowing you to reconstruct the exact regulatory context used for any given inference.
                                        </p>
                                        <div className="space-y-8">
                                            <h3 className="text-xl font-serif italic text-white">Recorded Signal Metadata</h3>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {[
                                                    { l: 'Timestamp (ISO 8601)', v: 'Nanosecond precision for high-frequency trading compliance.' },
                                                    { l: 'Tenant Signature', v: 'Cryptographic binding to your institutional ID.' },
                                                    { l: 'Vector Workspace', v: 'The exact subset of legislation queried.' },
                                                    { l: 'Inference Latency', v: 'End-to-end processing time for SLA monitoring.' },
                                                    { l: 'Semantic Hash', v: 'A deterministic hash of the retrieved regulatory snippets.' }
                                                ].map((item, i) => (
                                                    <div key={i} className="flex gap-4 p-4 border border-white/5 bg-white/[0.01]">
                                                        <Check size={14} className="text-emerald-500 shrink-0 mt-1" />
                                                        <div className="space-y-1">
                                                            <div className="text-xs font-bold text-white">{item.l}</div>
                                                            <div className="text-[10px] text-gray-500 font-serif italic">{item.v}</div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {/* REFERENCE CATEGORY */}
                            {docSection === 'api-reference' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <LinkIcon size={14} /> Endpoints
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white">API Reference</h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Exhaustive technical specification for the Neural Search endpoint.</p>
                                    </header>
                                    <div className="space-y-16 pt-12 border-t border-white/5">
                                        <div className="space-y-8">
                                            <div className="flex items-center gap-4 group">
                                                <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-black rounded-sm">GET</span>
                                                <code className="text-lg font-mono text-white group-hover:text-leagle-accent transition-colors">/api/v1/neural/search</code>
                                            </div>
                                            <div className="space-y-4">
                                                <h4 className="text-[10px] font-black uppercase text-gray-600 tracking-widest">Query Parameters</h4>
                                                <table className="w-full text-sm font-serif italic">
                                                    <thead className="border-b border-white/5">
                                                        <tr className="text-[10px] text-gray-600 uppercase font-black tracking-widest">
                                                            <th className="py-4 text-left">Key</th>
                                                            <th className="py-4 text-left">Description</th>
                                                            <th className="py-4 text-left">Rules</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody className="divide-y divide-white/5">
                                                        <tr><td className="py-4 text-white">query</td><td className="py-4 text-gray-500">Semantic search query string (URL encoded).</td><td className="py-4 text-indigo-400">Required</td></tr>
                                                        <tr><td className="py-4 text-white">limit</td><td className="py-4 text-gray-500">Number of results to return.</td><td className="py-4 text-gray-600">Max 50 (Default: 5)</td></tr>
                                                        <tr><td className="py-4 text-white">offset</td><td className="py-4 text-gray-500">Number of results to skip for pagination.</td><td className="py-4 text-gray-600">Min 0</td></tr>
                                                        <tr><td className="py-4 text-white">workspace</td><td className="py-4 text-gray-500">The legislative workspace to target.</td><td className="py-4 text-gray-600">Default: `global`</td></tr>
                                                    </tbody>
                                                </table>
                                            </div>
                                            <div className="space-y-4">
                                                <h4 className="text-[10px] font-black uppercase text-gray-600 tracking-widest">Required Headers</h4>
                                                <div className="p-6 bg-white/[0.01] border border-white/5 space-y-4">
                                                    <div className="flex justify-between items-center border-b border-white/5 pb-2">
                                                        <code className="text-indigo-400 text-xs">X-Protocol-Key</code>
                                                        <span className="text-[8px] font-black text-gray-600 uppercase tracking-widest">Required</span>
                                                    </div>
                                                    <p className="text-gray-500 text-xs font-serif italic">Your institutional credential issued via the developer console.</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {docSection === 'json-schema' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Database size={14} /> Data Model
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white leading-tight">JSON Schema</h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Standardized output format for multi-jurisdictional compliance data.</p>
                                    </header>
                                    <div className="space-y-12 pt-12 border-t border-white/5">
                                        <div className="p-10 bg-[#0a0a0a] border border-white/5 rounded-sm overflow-hidden">
                                            <div className="flex justify-between items-center text-[8px] font-black text-gray-700 uppercase tracking-[0.3em] mb-8">
                                                <span>SearchResponse.json</span>
                                                <span className="text-emerald-500/50">VALID SCHEMA</span>
                                            </div>
                                            <pre className="text-xs font-mono text-indigo-400 leading-relaxed overflow-x-auto">
                                                {`{
  "protocol": "NEURAL_V4",
  "results": [
    {
      "id": "uuid",
      "content": "Regulatory snippet content...",
      "score": 0.982,
      "metadata": {
        "source": "UK_FIN_2026",
        "chapter": "Compliance 12",
        "section": "Item 4.b",
        "verified_at": "2026-04-21T12:00:00Z"
      }
    }
  ],
  "performance": {
    "latency_ms": 142,
    "vector_hops": 3
  },
  "audit_trail_id": "aud_123_abc",
  "jurisdiction_scope": ["UK"]
}`}
                                            </pre>
                                        </div>
                                    </div>
                                </section>
                            )}

                            {docSection === 'error-codes' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Shield size={14} /> Fault Tolerance
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white">Error Codes</h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Handle edge cases and link failures with institutional grace.</p>
                                    </header>
                                    <div className="space-y-8 pt-12 border-t border-white/5 italic">
                                        {[
                                            { c: '401', m: 'UNAUTHORIZED_LINK', d: 'Protocol Key is missing, invalid, or expired.', r: 'Verify key status in Console.' },
                                            { c: '403', m: 'INSTITUTIONAL_BLOCK', d: 'Endpoint restricted for current tenant scope.', r: 'Contact account manager for tier upgrade.' },
                                            { c: '429', m: 'THROTTLING_ACTIVE', d: 'Resource threshold exceeded.', r: 'Implement exponential backoff.' },
                                            { c: '503', m: 'NEURAL_LINK_FAILURE', d: 'Upstream vector engine unavailable.', r: 'Retry with a 500ms jitter.' }
                                        ].map((err, i) => (
                                            <div key={i} className="flex gap-8 group py-4 border-b border-white/5 last:border-0">
                                                <div className="w-16 font-mono text-red-500 font-bold group-hover:scale-110 transition-transform">{err.c}</div>
                                                <div className="space-y-2 flex-1">
                                                    <div className="text-white text-sm font-black tracking-widest uppercase">{err.m}</div>
                                                    <p className="text-gray-500 text-xs font-serif leading-relaxed">{err.d}</p>
                                                    <p className="text-[10px] text-leagle-accent font-black uppercase tracking-widest">Recommended: {err.r}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                            )}

                            {docSection === 'rate-limits' && (
                                <section className="space-y-12 max-w-4xl animate-in fade-in duration-700">
                                    <header className="space-y-4">
                                        <div className="flex items-center gap-2 text-leagle-accent text-[10px] font-black uppercase tracking-widest">
                                            <Zap size={14} /> Resource Quotas
                                        </div>
                                        <h2 className="text-5xl font-serif italic text-white">Rate Limits</h2>
                                        <p className="text-gray-500 font-serif italic max-w-2xl">Ensure protocol stability with fair-use quotas based on institutional demand.</p>
                                    </header>
                                    <div className="space-y-12 pt-12 border-t border-white/5 flex flex-col font-serif italic">
                                        <p className="text-gray-400 font-serif italic leading-relaxed">
                                            Leagle implements a token-bucket algorithm for rate limiting. Quotas are calculated at the tenant level across all active Protocol Keys.
                                        </p>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                            {[
                                                { t: 'Sandbox', l: '100 requests / day', d: 'Ideal for initial POC and internal development.', c: 'border-white/5 grayscale' },
                                                { t: 'Institutional', l: '50 req / second', d: 'Production-ready for scale compliance monitoring.', c: 'border-leagle-accent/20 bg-leagle-accent/5' },
                                                { t: 'Enterprise', l: 'Unlimited Linkage', d: 'Dedicated infra shards for private vector search.', c: 'border-emerald-500/20 bg-emerald-500/5' }
                                            ].map((tier, i) => (
                                                <div key={i} className={`p-8 border rounded-sm space-y-4 ${tier.c}`}>
                                                    <h5 className="text-sm font-black uppercase tracking-widest text-white">{tier.t}</h5>
                                                    <div className="text-[10px] text-gray-500 mb-2">{tier.l}</div>
                                                    <p className="text-[10px] leading-relaxed text-gray-600 font-serif italic">{tier.d}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </section>
                            )}
                        </div>
                    ) : (
                        /* INTERACTIVE CONSOLE SECTION */
                        <section className="space-y-24">
                            <Show when="signed-in">
                                <div className="space-y-16">
                                    <header>
                                        <h1 className="text-4xl font-serif italic text-white flex items-center gap-4">
                                            <Cpu className="text-leagle-accent" size={32} />
                                            Protocol <span className="text-gradient">Console</span>
                                        </h1>
                                        <p className="text-gray-500 font-serif italic mt-2">Interactive testing and credential management.</p>
                                    </header>

                                    {/* KEY TABLE - Minimalist */}
                                    <div className="bg-[#0a0a0a] border border-white/5 rounded-sm overflow-hidden">
                                        <div className="px-8 py-4 border-b border-white/5 flex justify-between items-center bg-white/[0.01]">
                                            <span className="text-[9px] font-black uppercase tracking-widest text-gray-500">Active Credentials</span>
                                            <button onClick={() => setShowKeyModal(true)} className="text-[9px] font-black uppercase tracking-widest text-leagle-accent hover:text-white transition-colors flex items-center gap-2">
                                                <Plus size={12} /> New Protocol
                                            </button>
                                        </div>
                                        <table className="w-full">
                                            <tbody className="divide-y divide-white/5">
                                                <tr className={`group ${selectedKey === 'LGL_PROTOCOL_DEFAULT_SANDBOX' ? 'bg-leagle-accent/5' : ''}`}>
                                                    <td className="px-8 py-6">
                                                        <div className="text-sm font-serif italic text-white">Public Sandbox</div>
                                                        <div className="text-[8px] text-gray-600 font-black tracking-widest mt-1">READ-ONLY ACCESS</div>
                                                    </td>
                                                    <td className="px-8 py-6 text-right space-x-4 opacity-40 group-hover:opacity-100 transition-opacity">
                                                        <button onClick={() => setSelectedKey('LGL_PROTOCOL_DEFAULT_SANDBOX')} className={`text-[8px] font-black uppercase tracking-widest ${selectedKey === 'LGL_PROTOCOL_DEFAULT_SANDBOX' ? 'text-leagle-accent' : 'text-gray-500 hover:text-white'}`}>
                                                            {selectedKey === 'LGL_PROTOCOL_DEFAULT_SANDBOX' ? 'Active' : 'Select'}
                                                        </button>
                                                        <button onClick={() => handleCopy('LGL_PROTOCOL_DEFAULT_SANDBOX')} className="text-gray-500 hover:text-white">
                                                            {copied === 'LGL_PROTOCOL_DEFAULT_SANDBOX' ? <Check size={14} /> : <Copy size={14} />}
                                                        </button>
                                                    </td>
                                                </tr>
                                                {keys.map(k => (
                                                    <tr key={k.id} className={`group ${selectedKey === k.key ? 'bg-leagle-accent/5' : ''}`}>
                                                        <td className="px-8 py-6">
                                                            <div className="text-sm font-serif italic text-white">{k.name}</div>
                                                            <div className="text-[8px] text-gray-600 font-black tracking-widest mt-1">INSTITUTIONAL</div>
                                                        </td>
                                                        <td className="px-8 py-6 text-right space-x-4 opacity-40 group-hover:opacity-100 transition-opacity">
                                                            <button onClick={() => setSelectedKey(k.key)} className={`text-[8px] font-black uppercase tracking-widest ${selectedKey === k.key ? 'text-leagle-accent' : 'text-gray-500 hover:text-white'}`}>
                                                                {selectedKey === k.key ? 'Active' : 'Select'}
                                                            </button>
                                                            <button onClick={() => handleCopy(k.key)} className="text-gray-500 hover:text-white">
                                                                {copied === k.key ? <Check size={14} /> : <Copy size={14} />}
                                                            </button>
                                                            <button onClick={() => handleDeleteKey(k.id)} className="text-gray-500 hover:text-red-400">
                                                                <Trash2 size={14} />
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>

                                    {/* MODAL SIMULATED */}
                                    {showKeyModal && (
                                        <div className="p-8 border border-leagle-accent/30 bg-leagle-accent/5 rounded-sm flex items-center gap-6 animate-in slide-in-from-top-4">
                                            <input value={newKeyName} onChange={e => setNewKeyName(e.target.value)} placeholder="Key Identifier..." className="flex-1 bg-black/40 border border-white/10 rounded-sm py-3 px-4 text-sm font-serif italic focus:outline-none focus:border-leagle-accent" />
                                            <button onClick={handleGenerateKey} className="px-8 py-3 bg-white text-black text-[9px] font-black uppercase tracking-widest hover:bg-leagle-accent transition-all">Issue Key</button>
                                            <button onClick={() => setShowKeyModal(false)} className="text-[9px] font-black uppercase text-gray-500 hover:text-white">Cancel</button>
                                        </div>
                                    )}

                                    {/* PLAYGROUND - Cleaner */}
                                    <div className="space-y-8">
                                        <div className="relative group max-w-4xl">
                                            <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-gray-600 group-focus-within:text-leagle-accent transition-colors" size={20} />
                                            <input value={query} onChange={e => setQuery(e.target.value)} className="w-full bg-[#0a0a0a] border-b border-white/10 py-8 pl-18 pr-40 text-2xl font-serif italic focus:outline-none focus:border-leagle-accent transition-all" placeholder="Neural Search..." />
                                            <button onClick={runNeuralTest} disabled={isLoading} className="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-2 text-leagle-accent hover:text-white transition-colors">
                                                {isLoading ? <RefreshCw className="animate-spin" size={20} /> : <Play size={20} />}
                                                <span className="text-[10px] font-black uppercase tracking-widest">Execute</span>
                                            </button>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                            {Object.entries(getSnippets()).map(([lang, code]) => (
                                                <div key={lang} className="p-6 bg-[#0a0a0a] border border-white/5 rounded-sm space-y-4">
                                                    <div className="flex justify-between items-center text-[8px] font-black uppercase tracking-widest text-gray-600">
                                                        <span>{lang} Integration</span>
                                                        <button onClick={() => handleCopy(code)} className="hover:text-white transition-colors">{copied === code ? 'Copied' : 'Copy'}</button>
                                                    </div>
                                                    <pre className="text-[10px] font-mono text-indigo-400 overflow-x-auto whitespace-pre-wrap">{code}</pre>
                                                </div>
                                            ))}
                                        </div>

                                        <div className="bg-black border border-white/5 min-h-[300px] p-10 rounded-sm relative">
                                            <div className="absolute top-4 left-4 flex items-center gap-2 text-[8px] font-black text-gray-700 uppercase tracking-widest">
                                                <Terminal size={10} /> Output Console
                                            </div>
                                            {results ? (
                                                <pre className="text-sm font-mono text-emerald-400/80 leading-relaxed whitespace-pre-wrap">
                                                    {JSON.stringify(results, null, 2)}
                                                </pre>
                                            ) : (
                                                <div className="h-full flex items-center justify-center grayscale opacity-10 py-20">
                                                    <Database size={64} />
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </Show>

                            <Show when="signed-out">
                                <div className="p-20 border border-white/5 bg-white/[0.01] rounded-sm flex flex-col items-center text-center space-y-8 max-w-2xl mx-auto grayscale group hover:grayscale-0 transition-all duration-1000">
                                    <Lock size={48} className="text-leagle-accent" />
                                    <div className="space-y-4">
                                        <h2 className="text-3xl font-serif italic text-white tracking-tight">Interactive Console Restricted</h2>
                                        <p className="text-gray-500 font-serif italic leading-relaxed">
                                            The core retrieval engine utilizing a Neural Vector Base for regulatory indexing.
                                        </p>
                                    </div>
                                    <SignInButton mode="modal">
                                        <button className="px-10 py-4 border border-white/10 text-white text-[10px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all">Establish Session</button>
                                    </SignInButton>
                                </div>
                            </Show>
                        </section>
                    )}

                    {/* FOOTER NAV (Only for Docs Mode) */}
                    {activeSection === 'docs' && (
                        <nav className="pt-20 border-t border-white/5 flex justify-between items-center max-w-3xl">
                            <div className="grayscale opacity-30">Previous: Solutions</div>
                            <button onClick={() => setActiveSection('console')} className="group flex items-center gap-4 text-white text-right">
                                <div className="space-y-1">
                                    <div className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Next Up</div>
                                    <div className="text-xl font-serif italic group-hover:text-leagle-accent transition-colors">Developer Console</div>
                                </div>
                                <ArrowRight className="group-hover:translate-x-2 transition-transform" />
                            </button>
                        </nav>
                    )}
                </article>
            </div>
        </div>
    );
}
