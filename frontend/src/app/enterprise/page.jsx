import LandingNavbar from '../components/LandingNavbar';
import { Lock, Shield, Globe, ArrowRight } from 'lucide-react';
import Image from 'next/image';

export default function EnterprisePage() {
    return (
        <div className="min-h-dvh bg-[var(--leagle-bg)] text-white">
            <LandingNavbar />

            <main className="pt-24 sm:pt-40">
                {/* Hero section */}
                <section className="relative px-4 sm:px-6 pb-20 sm:pb-32 overflow-hidden">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(197,160,89,0.06)_0%,transparent_70%)] -z-10" />
                    <div className="max-w-7xl mx-auto">
                        <header className="max-w-3xl mb-12 sm:mb-20 animate-in fade-in slide-in-from-bottom-8 duration-700">
                            <h2 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em] mb-4 sm:mb-6">Enterprise Protocol</h2>
                            <h1 className="text-4xl sm:text-5xl md:text-7xl font-serif italic mb-6 sm:mb-8 leading-tight">Sovereign Compliance for <span className="text-gradient block sm:inline">Global Operations</span></h1>
                            <p className="text-lg sm:text-xl text-gray-500 font-serif italic leading-relaxed">Dedicated infrastructure, custom jurisdictional mapping, and Tier-IV security for the world's most demanding legal environments.</p>
                        </header>
                    </div>
                </section>

                <section className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5 bg-white/[0.01]">
                    <div className="max-w-7xl mx-auto">
                        <div className="glass-card p-8 sm:p-12 md:p-24 border-leagle-accent/20 bg-leagle-accent/5 rounded-sm relative overflow-hidden group">
                            <div className="absolute top-0 right-0 py-1.5 sm:py-2 px-4 sm:px-6 bg-leagle-accent text-black text-[8px] sm:text-[10px] font-black uppercase tracking-[0.2em]">High Impact Protocol</div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-20 items-center">
                                <div className="space-y-8 sm:space-y-10">
                                    <div className="space-y-4">
                                        <h3 className="text-3xl sm:text-4xl font-serif italic">VPC Neural Deployment</h3>
                                        <p className="text-gray-500 font-serif italic leading-relaxed text-base sm:text-lg">
                                            Execute the Leagle Intelligence engine entirely within your own firewalled infrastructure. Zero data leakage, full air-gapped compatibility, and multi-tenant isolation.
                                        </p>
                                    </div>
                                    <ul className="space-y-4 sm:space-y-6">
                                        {[
                                            { icon: <Lock size={16} className="shrink-0" />, text: "Custom HSM Key Management" },
                                            { icon: <Shield size={16} className="shrink-0" />, text: "FEDRAMP High / SOC2 Type II Alignment" },
                                            { icon: <Globe size={16} className="shrink-0" />, text: "Jurisdictional Data Residency Selection" }
                                        ].map((item, i) => (
                                            <li key={i} className="flex items-start gap-4 text-[10px] sm:text-xs font-black uppercase tracking-widest text-gray-400">
                                                <div className="text-leagle-accent mt-0.5">{item.icon}</div>
                                                <span className="min-w-0 break-words">{item.text}</span>
                                            </li>
                                        ))}
                                    </ul>
                                    <button className="w-full sm:w-auto min-h-[44px] px-8 sm:px-12 py-4 sm:py-5 bg-leagle-accent text-black text-[10px] font-black uppercase tracking-[0.2em] hover:bg-white transition-all shadow-2xl shadow-leagle-accent/20">
                                        Request Protocol Briefing
                                    </button>
                                </div>
                                <div className="relative">
                                    <div className="aspect-square bg-leagle-accent/10 border border-leagle-accent/20 flex flex-col items-center justify-center p-8 sm:p-12 text-center space-y-6">
                                        <Lock size={48} className="sm:w-[60px] sm:h-[60px] text-leagle-accent opacity-50" />
                                        <p className="text-[10px] font-black uppercase tracking-widest text-gray-500">Security Architecture Visualization</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5">
                    <div className="max-w-4xl mx-auto text-center space-y-8 sm:space-y-12">
                        <h2 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em]">Scalable Solutions</h2>
                        <h3 className="text-3xl sm:text-4xl font-serif italic">Designed for Complexity.</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 sm:gap-12 text-left pt-8 sm:pt-12">
                            {[
                                { title: "On-Premise", desc: "Full hardware-accelerated neural local instances." },
                                { title: "Custom RAG", desc: "Private vector databases tuned to your firm's case history." },
                                { title: "API Fabric", desc: "Direct neural endpoints for integration with internal GRC tools." }
                            ].map((p, i) => (
                                <div key={i} className="space-y-3 sm:space-y-4">
                                    <h4 className="text-white font-serif italic text-lg sm:text-xl border-b border-leagle-accent/20 pb-3 sm:pb-4">{p.title}</h4>
                                    <p className="text-gray-500 text-xs sm:text-sm font-serif italic leading-relaxed">{p.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            </main>

            <footer className="py-12 sm:py-20 border-t border-white/5 px-4 sm:px-6">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="flex items-center gap-2">
                        <Image src="/logo.png" alt="Leagle Logo" width={28} height={28} />
                        <span className="text-lg font-bold font-serif italic">Leagle <span className="text-leagle-accent">Intelligence</span></span>
                    </div>
                    <p className="text-[10px] sm:text-xs font-black uppercase tracking-widest text-gray-600 text-center md:text-right">© 2026 Leagle OS. All protocols active.</p>
                </div>
            </footer>
        </div>
    );
}
