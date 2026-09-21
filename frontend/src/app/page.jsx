'use client';

import Link from 'next/link';
import Image from 'next/image';
import { ChevronRight, Shield, Activity, Search, Globe, Lock, ArrowRight, Check } from 'lucide-react';
import { Show, UserButton, SignInButton, SignUpButton } from '@clerk/nextjs';
import LandingNavbar from './components/LandingNavbar';
import CapabilityCard from './components/CapabilityCard';

export default function Home() {
    return (
        <div className="min-h-dvh bg-[var(--leagle-bg)] text-white font-sans">
            <LandingNavbar />

            <main className="pt-16 sm:pt-20">
                {/* Hero Section */}
                <section className="relative pt-20 sm:pt-32 pb-20 sm:pb-40 px-4 sm:px-6 overflow-hidden">
                    <div className="max-w-7xl mx-auto text-center relative z-10">
                        {/* Subtle Ambient Glow */}
                        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(197,160,89,0.05)_0%,transparent_70%)] -z-10" />

                        <h1 className="text-4xl sm:text-5xl md:text-7xl font-serif font-medium mb-6 sm:mb-8 leading-[1.1] animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
                            Enterprise <span className="text-gradient">Regulatory Intelligence</span> & Compliance
                        </h1>

                        <p className="text-lg sm:text-xl text-gray-500 max-w-2xl mx-auto mb-10 sm:mb-12 leading-relaxed animate-in fade-in slide-in-from-bottom-12 duration-700 delay-200 font-serif italic px-4">
                            Automate regulatory monitoring, risk assessment, and legal impact analysis with a high-fidelity intelligence platform built for global operations.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 animate-in fade-in slide-in-from-bottom-16 duration-700 delay-300 justify-center px-4">
                            <Show when="signed-in">
                                <Link href="/dashboard" className="btn-premium px-8 py-4 text-sm sm:text-base group min-h-[44px] flex items-center justify-center">
                                    Access Control Center
                                    <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
                                </Link>
                            </Show>
                            <Show when="signed-out">
                                <SignUpButton mode="modal">
                                    <button className="btn-premium px-8 py-4 text-sm sm:text-base group cursor-pointer w-full sm:w-auto min-h-[44px]">
                                        Initialize Scanning
                                        <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
                                    </button>
                                </SignUpButton>
                            </Show>
                            <Link href="/enterprise" className="px-8 py-4 text-[10px] sm:text-[11px] font-black uppercase tracking-[0.2em] border border-white/10 hover:bg-white/5 transition-all flex items-center justify-center min-h-[44px] w-full sm:w-auto">
                                Request High-Protocol Demo
                            </Link>
                        </div>
                    </div>
                </section>

                {/* Capabilities Grid */}
                <section className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5 bg-white/[0.01]">
                    <div className="max-w-7xl mx-auto">
                        <div className="mb-12 sm:mb-20 text-center md:text-left">
                            <h2 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em] mb-4">Core Capabilities</h2>
                            <h3 className="text-3xl sm:text-4xl font-serif italic">Precision Governance at Scale</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
                            <CapabilityCard
                                icon={<Search className="w-5 h-5 text-leagle-accent" />}
                                title="Semantic Ingest"
                                description="Advanced neural extraction of regulatory directives across global legal repositories."
                            />
                            <CapabilityCard
                                icon={<Activity className="w-5 h-5 text-leagle-accent" />}
                                title="Exposure Matrix"
                                description="Real-time heatmap of operational risks and compliance gaps in your policy framework."
                            />
                            <CapabilityCard
                                icon={<Lock className="w-5 h-5 text-leagle-accent" />}
                                title="Impact Analysis"
                                description="Predictive benchmarking of regulatory changes against internal company policies."
                            />
                        </div>
                    </div>
                </section>

                {/* Monetization Strategy Section */}
                <section id="pricing" className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5">
                    <div className="max-w-7xl mx-auto text-center">
                        <header className="max-w-3xl mx-auto mb-12 sm:mb-20 space-y-4 px-4">
                            <h2 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em]">Institutional Protocols</h2>
                            <h3 className="text-3xl sm:text-4xl md:text-5xl font-serif italic text-white">Acquire Specialized Intelligence</h3>
                            <p className="text-sm sm:text-base text-gray-500 font-medium">From individual monitoring to institutional risk mitigation.</p>
                        </header>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto text-left">
                            {/* Pulse */}
                            <div className="p-6 sm:p-10 glass-card border-indigo-400/10 bg-white/2 hover:border-indigo-400/30 transition-all flex flex-col rounded-sm">
                                <p className="text-[10px] sm:text-xs font-black text-indigo-400 uppercase tracking-widest mb-2">Pulse Protocol</p>
                                <h4 className="text-xl sm:text-2xl font-serif italic text-white mb-6">$29<span className="text-xs font-sans not-italic text-gray-600">/mo</span></h4>
                                <ul className="space-y-4 mb-8 sm:mb-10 flex-1">
                                    {["Real-time Alerting", "UK Regulation Sync", "Basic Compliance Check"].map((f, i) => (
                                        <li key={i} className="text-xs text-gray-400 flex items-center gap-2"><Check size={12} className="text-indigo-400 shrink-0" /> <span className="min-w-0 break-words">{f}</span></li>
                                    ))}
                                </ul>
                                <button className="w-full py-4 min-h-[44px] bg-white/5 border border-white/10 text-white text-[9px] sm:text-[10px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all">Initialize Pulse</button>
                            </div>

                            {/* Briefings */}
                            <div className="p-6 sm:p-10 glass-card border-leagle-accent/10 bg-white/2 hover:border-leagle-accent/30 transition-all flex flex-col rounded-sm">
                                <p className="text-[10px] sm:text-xs font-black text-leagle-accent uppercase tracking-widest mb-2">Deep-Dive Briefs</p>
                                <h4 className="text-xl sm:text-2xl font-serif italic text-white mb-6">$49<span className="text-xs font-sans not-italic text-gray-600">/ea</span></h4>
                                <ul className="space-y-4 mb-8 sm:mb-10 flex-1">
                                    {["High-Fidelity Analysis", "PDF Remediation Roadmap", "Expert AI Verdict"].map((f, i) => (
                                        <li key={i} className="text-xs text-gray-400 flex items-center gap-2"><Check size={12} className="text-leagle-accent shrink-0" /> <span className="min-w-0 break-words">{f}</span></li>
                                    ))}
                                </ul>
                                <button className="w-full py-4 min-h-[44px] bg-leagle-accent/10 border border-leagle-accent/20 text-leagle-accent text-[9px] sm:text-[10px] font-black uppercase tracking-widest hover:bg-leagle-accent hover:text-black transition-all">Acquire Briefing</button>
                            </div>

                            {/* Risk Shield */}
                            <div className="p-6 sm:p-10 glass-card border-leagle-accent/40 bg-leagle-accent/5 hover:border-leagle-accent transition-all flex flex-col relative rounded-sm">
                                <div className="absolute top-0 right-0 bg-leagle-accent text-black text-[7px] font-black px-3 py-1 uppercase tracking-widest">Insurance Backed</div>
                                <p className="text-[10px] sm:text-xs font-black text-leagle-accent uppercase tracking-widest mb-2">Risk Shield</p>
                                <h4 className="text-xl sm:text-2xl font-serif italic text-white mb-6">$299<span className="text-xs font-sans not-italic text-gray-500">/mo</span></h4>
                                <ul className="space-y-4 mb-8 sm:mb-10 flex-1">
                                    {["Institutional Audits", "Insurance Premium Credit", "Multi-User Governance"].map((f, i) => (
                                        <li key={i} className="text-xs text-gray-100 flex items-center gap-2 font-bold"><Check size={12} className="text-leagle-accent shrink-0" /> <span className="min-w-0 break-words">{f}</span></li>
                                    ))}
                                </ul>
                                <Link href="/pricing" className="flex items-center justify-center w-full py-4 min-h-[44px] bg-leagle-accent text-black text-[9px] sm:text-[10px] font-black uppercase tracking-widest text-center hover:bg-white transition-all shadow-lg shadow-leagle-accent/20">Deploy Shield</Link>
                            </div>

                            {/* Neural Engine */}
                            <div className="p-6 sm:p-10 glass-card border-white/10 bg-white/1 hover:border-white/30 transition-all flex flex-col rounded-sm">
                                <p className="text-[10px] sm:text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Neural Engine</p>
                                <h4 className="text-xl sm:text-2xl font-serif italic text-white mb-6">Custom</h4>
                                <ul className="space-y-4 mb-8 sm:mb-10 flex-1">
                                    {["VPC Deployment", "Direct Agent Controls", "Priority Neural Compute"].map((f, i) => (
                                        <li key={i} className="text-xs text-gray-500 flex items-center gap-2"><Check size={12} className="shrink-0" /> <span className="min-w-0 break-words">{f}</span></li>
                                    ))}
                                </ul>
                                <Link href="/enterprise" className="flex items-center justify-center w-full py-3 min-h-[44px] border border-indigo-400/20 text-indigo-400 text-[9px] sm:text-[10px] font-black uppercase tracking-widest text-center hover:bg-indigo-400 hover:text-white transition-all">License Engine</Link>
                            </div>
                        </div>

                        {/* Developer API Banner */}
                        <div className="mt-12 p-6 sm:p-8 border border-white/5 bg-white/[0.01] rounded-sm flex flex-col md:flex-row items-center justify-between gap-6 sm:gap-8 text-left">
                            <div className="flex flex-col sm:flex-row items-center sm:items-start md:items-center gap-4 sm:gap-6 text-center sm:text-left">
                                <div className="w-12 h-12 shrink-0 bg-white/5 border border-white/10 rounded-sm flex items-center justify-center text-gray-400">
                                    <Globe size={20} />
                                </div>
                                <div>
                                    <h4 className="text-[10px] sm:text-xs font-black text-leagle-accent uppercase tracking-widest mb-1 sm:mb-2">Developer Protocol</h4>
                                    <p className="text-sm text-gray-400 font-serif italic max-w-xl">Build on the Leagle Semantic Index. **Free Sandbox Protocol** (Limited) / High-Throughput API available.</p>
                                </div>
                            </div>
                            <Link href="/api" className="px-6 sm:px-8 py-3 min-h-[44px] bg-white/5 border border-white/10 text-white text-[9px] sm:text-[10px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all flex items-center justify-center whitespace-nowrap w-full md:w-auto">Explore API Docs</Link>
                        </div>

                        <div className="mt-16 sm:mt-20 px-4">
                            <p className="text-gray-500 text-[10px] sm:text-xs font-black uppercase tracking-widest mb-4">Leverage Regulatory Infrastructure?</p>
                            <Link href="/enterprise" className="text-leagle-accent hover:underline text-sm sm:text-base font-serif italic block break-words">Contact Global Institutional Partnerships & API Solutions</Link>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="py-12 sm:py-20 border-t border-white/5 px-4 sm:px-6">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
                    <div className="flex items-center gap-2">
                        <Image src="/logo.png" alt="Leagle Logo" width={32} height={32} />
                        <span className="text-lg sm:text-xl font-bold tracking-tight text-white font-serif italic">Leagle <span className="text-leagle-accent">Intelligence</span></span>
                    </div>
                    <nav className="flex flex-wrap justify-center gap-6 sm:gap-12 text-[10px] sm:text-xs font-black uppercase tracking-widest text-gray-500">
                        <Link href="/platform" className="hover:text-white transition-colors min-h-[44px] flex items-center">Platform</Link>
                        <Link href="/solutions" className="hover:text-white transition-colors min-h-[44px] flex items-center">Solutions</Link>
                        <Link href="/enterprise" className="hover:text-white transition-colors min-h-[44px] flex items-center">Enterprise</Link>
                        <Link href="/pricing" className="hover:text-white transition-colors min-h-[44px] flex items-center">Pricing</Link>
                    </nav>
                    <div className="text-[10px] sm:text-xs text-gray-600 font-bold tracking-widest uppercase text-center md:text-right">
                        &copy; 2026 Leagle Intelligence. All protocols reserved.
                    </div>
                </div>
            </footer>
        </div>
    );
}
