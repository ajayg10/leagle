import LandingNavbar from '../components/LandingNavbar';
import { Zap, Shield, Target, ArrowRight, Check, Globe, Users } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

export default function PricingPage() {
    return (
        <div className="min-h-dvh bg-[var(--leagle-bg)] text-white">
            <LandingNavbar />

            <main className="pt-24 sm:pt-40">
                {/* Hero section */}
                <section className="relative px-4 sm:px-6 pb-20 sm:pb-40 overflow-hidden">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.05)_0%,transparent_70%)] -z-10" />
                    <div className="max-w-7xl mx-auto text-center">
                        <header className="max-w-3xl mx-auto space-y-4 sm:space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
                            <h2 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em] font-sans">Institutional Protocols</h2>
                            <h1 className="text-4xl sm:text-5xl md:text-7xl font-serif italic mb-6 sm:mb-8 leading-tight">Scalable Intelligence for <span className="text-gradient">Risk Ecosystems</span></h1>
                            <p className="text-lg sm:text-xl text-gray-500 font-serif italic leading-relaxed font-medium px-4">From individual monitoring to institutional-grade risk shield and API infrastructure.</p>
                        </header>
                    </div>
                </section>

                <section className="py-16 sm:py-20 px-4 sm:px-6 border-t border-white/5 bg-white/[0.01]">
                    <div className="max-w-7xl mx-auto">
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8 items-stretch">
                            {/* Pulse Subscription */}
                            <div className="p-6 sm:p-10 glass-card border-indigo-400/10 bg-white/2 rounded-sm flex flex-col items-center group hover:border-indigo-400/40 transition-all text-center">
                                <div className="w-12 h-12 bg-indigo-500/10 border border-indigo-400/20 rounded-full flex items-center justify-center mb-6 sm:mb-8 text-indigo-400">
                                    <Shield size={20} />
                                </div>
                                <h3 className="text-lg sm:text-xl font-bold uppercase tracking-widest mb-2 font-black text-white">Pulse Protocol</h3>
                                <p className="text-gray-500 text-[10px] sm:text-xs mb-8 sm:mb-10 font-black uppercase tracking-widest italic">Base Intelligence</p>
                                <div className="text-3xl sm:text-4xl font-serif italic mb-8 sm:mb-10">$29<span className="text-xs sm:text-sm text-gray-600 font-sans not-italic">/mo</span></div>
                                <ul className="text-left space-y-4 sm:space-y-5 mb-8 sm:mb-12 flex-1 w-full">
                                    {["Real-time Alerting (1 Region)", "Premium Global Search", "UK Regulation Sync", "AI Context Persistence"].map((item, i) => (
                                        <li key={i} className="flex items-start gap-3 text-xs text-gray-400 font-medium">
                                            <Check size={14} className="text-indigo-400 shrink-0 mt-0.5" /> <span className="min-w-0 break-words">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                                <button className="w-full py-4 sm:py-5 min-h-[44px] border border-indigo-400/20 text-white text-[10px] sm:text-[11px] font-black uppercase tracking-widest hover:bg-indigo-400 hover:text-black transition-all">Initialize Pulse</button>
                            </div>

                            {/* Usage-Based Briefings */}
                            <div className="p-6 sm:p-10 glass-card border-leagle-accent/10 bg-white/2 rounded-sm flex flex-col items-center group hover:border-leagle-accent/40 transition-all text-center">
                                <div className="w-12 h-12 bg-leagle-accent/10 border border-leagle-accent/20 rounded-full flex items-center justify-center mb-6 sm:mb-8 text-leagle-accent">
                                    <Zap size={20} />
                                </div>
                                <h3 className="text-lg sm:text-xl font-bold uppercase tracking-widest mb-2 font-black text-white">Strategic Briefs</h3>
                                <p className="text-gray-500 text-[10px] sm:text-xs mb-8 sm:mb-10 font-black uppercase tracking-widest text-leagle-accent italic">Deep-Dive Analysis</p>
                                <div className="text-3xl sm:text-4xl font-serif italic mb-8 sm:mb-10">$49<span className="text-xs sm:text-sm text-gray-600 font-sans not-italic">/ea</span></div>
                                <ul className="text-left space-y-4 sm:space-y-5 mb-8 sm:mb-12 flex-1 w-full">
                                    {["Neural Gap Analysis", "Institutional Compliance Score", "Remediation Documentation", "PDF Executive Summary", "Audit Trail Preservation"].map((item, i) => (
                                        <li key={i} className="flex items-start gap-3 text-xs text-gray-400 font-medium">
                                            <Check size={14} className="text-leagle-accent shrink-0 mt-0.5" /> <span className="min-w-0 break-words">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                                <button className="w-full py-4 sm:py-5 min-h-[44px] border border-leagle-accent/20 text-white text-[10px] sm:text-[11px] font-black uppercase tracking-widest hover:bg-leagle-accent hover:text-black transition-all">Acquire Briefing</button>
                            </div>

                            {/* Risk Shield (Institutional) */}
                            <div className="p-6 sm:p-10 glass-card border-leagle-accent/40 bg-leagle-accent/5 rounded-sm flex flex-col items-center relative overflow-hidden group text-center">
                                <div className="absolute top-0 right-0 py-1.5 sm:py-2 px-3 sm:px-5 bg-leagle-accent text-black text-[7px] sm:text-[8px] font-black uppercase tracking-[0.2em]">Risk Neutral</div>
                                <div className="w-12 h-12 bg-leagle-accent/20 border border-leagle-accent/40 rounded-full flex items-center justify-center mb-6 sm:mb-8 text-leagle-accent">
                                    <Target size={20} />
                                </div>
                                <h3 className="text-lg sm:text-xl font-bold uppercase tracking-widest mb-2 font-black text-white">Risk Shield</h3>
                                <p className="text-gray-500 text-[10px] sm:text-xs mb-8 sm:mb-10 font-black uppercase tracking-widest text-leagle-accent italic">Institutional Suite</p>
                                <div className="text-3xl sm:text-4xl font-serif italic mb-8 sm:mb-10">$299<span className="text-xs sm:text-sm text-gray-600 font-sans not-italic">/mo</span></div>
                                <ul className="text-left space-y-4 sm:space-y-5 mb-8 sm:mb-12 flex-1 w-full">
                                    {["Certified Insurance Reporting", "Professional Liability Credit", "Shared Remiation Hub", "Admin Governance Protocol", "Institutional Multi-Region Sync"].map((item, i) => (
                                        <li key={i} className="flex items-start gap-3 text-xs text-gray-100 font-bold">
                                            <Check size={14} className="text-leagle-accent shrink-0 mt-0.5" /> <span className="min-w-0 break-words">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                                <button className="w-full py-4 sm:py-5 min-h-[44px] bg-leagle-accent text-black text-[10px] sm:text-[11px] font-black uppercase tracking-widest hover:bg-white transition-all shadow-xl shadow-leagle-accent/20">Deploy Shield</button>
                            </div>

                            {/* Neural Engine (API/Licensing) */}
                            <div className="p-6 sm:p-10 glass-card border-white/5 bg-white/1 rounded-sm flex flex-col items-center group hover:border-white/20 transition-all text-center">
                                <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mb-6 sm:mb-8">
                                    <Globe className="text-gray-500" size={20} />
                                </div>
                                <h3 className="text-lg sm:text-xl font-bold uppercase tracking-widest mb-2 font-black text-white">Neural Engine</h3>
                                <p className="text-gray-600 text-[10px] sm:text-xs mb-8 sm:mb-10 font-black uppercase tracking-widest italic text-indigo-400">Infrastructure Layer</p>
                                <div className="text-3xl sm:text-4xl font-serif italic mb-8 sm:mb-10">Custom</div>
                                <ul className="text-left space-y-4 sm:space-y-5 mb-8 sm:mb-12 flex-1 w-full">
                                    {["VPC Neural Deployment", "Regulatory API Licensing", "Portfolio Compliance Aggregators", "Unlimited Engine Inference", "SLA-Backed Performance"].map((item, i) => (
                                        <li key={i} className="flex items-start gap-3 text-xs text-gray-500 font-medium">
                                            <Check size={14} className="text-gray-600 shrink-0 mt-0.5" /> <span className="min-w-0 break-words">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                                <Link href="/enterprise" className="w-full py-4 sm:py-5 min-h-[44px] border border-white/10 text-gray-500 text-[10px] sm:text-[11px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all flex items-center justify-center">Request License</Link>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5 relative overflow-hidden">
                    <div className="max-w-7xl mx-auto">
                        <div className="mb-12 sm:mb-20 text-center md:text-left">
                            <h4 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em] mb-4">Developer Protocols</h4>
                            <h5 className="text-3xl sm:text-4xl font-serif italic text-white leading-tight">Build on the Semantic Layer</h5>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 mb-16 sm:mb-20">
                            <div className="p-8 sm:p-12 border border-white/5 bg-white/2 rounded-sm text-left group hover:border-white/20 transition-all">
                                <h6 className="text-xs sm:text-sm font-black uppercase tracking-widest text-gray-500 mb-4 sm:mb-6 font-sans">Sandbox Protocol</h6>
                                <div className="text-2xl sm:text-3xl font-serif italic text-white mb-6">Free</div>
                                <ul className="space-y-4 mb-8 sm:mb-10">
                                    {["100 API Credits /mo", "Standard Latency", "Public Regulatory Set", "Community Support"].map((f, i) => (
                                        <li key={i} className="text-xs text-gray-400 flex items-start gap-2"><Check size={12} className="text-gray-500 shrink-0 mt-0.5" /> <span className="min-w-0 break-words">{f}</span></li>
                                    ))}
                                </ul>
                                <button className="px-6 sm:px-8 py-3 sm:py-4 min-h-[44px] w-full sm:w-auto border border-white/10 text-gray-500 text-[10px] sm:text-[11px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all">Register Access</button>
                            </div>

                            <div className="p-8 sm:p-12 border border-leagle-accent/20 bg-leagle-accent/5 rounded-sm text-left group hover:border-leagle-accent/40 transition-all relative overflow-hidden">
                                <div className="absolute top-0 right-0 py-1.5 sm:py-2 px-3 sm:px-5 bg-leagle-accent text-black text-[7px] sm:text-[8px] font-black uppercase tracking-[0.2em]">High Throughput</div>
                                <h6 className="text-xs sm:text-sm font-black uppercase tracking-widest text-leagle-accent mb-4 sm:mb-6 font-sans">Heavy Usage</h6>
                                <div className="text-2xl sm:text-3xl font-serif italic text-white mb-6">$0.05<span className="text-xs sm:text-sm font-sans not-italic text-gray-500">/request</span></div>
                                <ul className="space-y-4 mb-8 sm:mb-10">
                                    {["Unlimited Throughput", "Priority Compute Queue", "Full Jurisdictional Sync", "Dedicated Dev Support"].map((f, i) => (
                                        <li key={i} className="text-xs text-gray-200 flex items-start gap-2"><Check size={12} className="text-leagle-accent shrink-0 mt-0.5" /> <span className="min-w-0 break-words">{f}</span></li>
                                    ))}
                                </ul>
                                <button className="px-6 sm:px-8 py-3 sm:py-4 min-h-[44px] w-full sm:w-auto bg-leagle-accent text-black text-[10px] sm:text-[11px] font-black uppercase tracking-widest hover:bg-white transition-all">Generate API Key</button>
                            </div>
                        </div>

                        <div className="p-8 sm:p-16 border border-white/5 bg-white/2 rounded-sm flex flex-col md:flex-row items-center gap-8 sm:gap-12 justify-between text-left relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-1.5 md:w-1.5 md:h-full bg-indigo-500/50" />
                            <div className="space-y-4 sm:space-y-6 pt-4 md:pt-0">
                                <h4 className="text-[10px] sm:text-xs font-black text-indigo-400 uppercase tracking-widest text-center md:text-left">Global Protocol Integration</h4>
                                <h5 className="text-3xl sm:text-4xl font-serif italic text-white leading-tight text-center md:text-left">Complex Institutional Ecosystems</h5>
                                <p className="text-base sm:text-lg text-gray-500 font-serif italic text-center md:text-left max-w-2xl">Deploy the Leagle Neural Engine directly within your VPC for maximum sovereignty and portfolio-wide regulatory intelligence.</p>
                            </div>
                            <Link href="/enterprise" className="w-full md:w-auto shrink-0 px-8 sm:px-10 py-4 sm:py-5 min-h-[44px] bg-white text-black text-[10px] sm:text-[11px] font-black uppercase tracking-widest hover:bg-indigo-400 transition-all text-center shadow-2xl flex items-center justify-center">Partner Consultation</Link>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="py-12 sm:py-20 border-t border-white/5 px-4 sm:px-6">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
                    <div className="flex items-center gap-2">
                        <Image src="/logo.png" alt="Leagle Logo" width={28} height={28} />
                        <span className="text-lg sm:text-xl font-bold font-serif italic">Leagle <span className="text-leagle-accent">Intelligence</span></span>
                    </div>
                    <p className="text-[10px] sm:text-xs font-black uppercase tracking-widest text-gray-600 text-center md:text-right">© 2026 Leagle OS. All protocols active.</p>
                </div>
            </footer>
        </div>
    );
}
