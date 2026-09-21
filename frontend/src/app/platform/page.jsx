import LandingNavbar from '../components/LandingNavbar';
import { Shield, Zap, Globe, Lock, ArrowRight } from 'lucide-react';
import Image from 'next/image';

export default function PlatformPage() {
    return (
        <div className="min-h-dvh bg-[var(--leagle-bg)] text-white">
            <LandingNavbar />

            <main className="pt-24 sm:pt-40">
                {/* Hero section */}
                <section className="relative px-4 sm:px-6 pb-20 sm:pb-32 overflow-hidden">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(197,160,89,0.05)_0%,transparent_70%)] -z-10" />
                    <div className="max-w-7xl mx-auto">
                        <header className="max-w-3xl mb-12 sm:mb-20 animate-in fade-in slide-in-from-bottom-8 duration-700">
                            <h2 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em] mb-4 sm:mb-6">Technical Architecture</h2>
                            <h1 className="text-4xl sm:text-5xl md:text-7xl font-serif italic mb-6 sm:mb-8 leading-tight">Institutional-Grade <span className="text-gradient block sm:inline">Legal Intelligence</span></h1>
                            <p className="text-lg sm:text-xl text-gray-500 font-serif italic leading-relaxed">Leagle OS is a proprietary neural framework designed for continuous regulatory monitoring and high-fidelity legal impact analysis. We provide the infrastructure for autonomous, yet compliant, enterprise operations.</p>
                        </header>
                    </div>
                </section>

                {/* Core Engine */}
                <section className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5 bg-white/[0.01]">
                    <div className="max-w-7xl mx-auto">
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 sm:gap-12">
                            {[
                                { title: "Neural Ingestion", desc: "Multi-modal extraction of regulatory updates across SEC, UK Legislation, and internal policies. Our connectors normalize disparate data streams into queryable neural embeddings.", icon: <Shield /> },
                                { title: "RAG Impact Layer", desc: "Retrieval-Augmented Generation for high-fidelity compliance determination. We ground model outputs in verifiable legal citations to eliminate hallucinations.", icon: <Zap /> },
                                { title: "Semantic Sync", desc: "Real-time synchronization across multiple jurisdictions. Automated deficiency detection ensures your internal policies never diverge from global standards.", icon: <Globe /> }
                            ].map((feature, i) => (
                                <div key={i} className="glass-card p-8 sm:p-12 space-y-6 sm:space-y-8 hover:border-leagle-accent/40 transition-all rounded-sm group">
                                    <div className="w-12 h-12 sm:w-14 sm:h-14 bg-leagle-accent/5 border border-leagle-accent/10 flex items-center justify-center text-leagle-accent group-hover:bg-leagle-accent group-hover:text-black transition-all">
                                        {feature.icon}
                                    </div>
                                    <h3 className="text-xl sm:text-2xl font-serif italic">{feature.title}</h3>
                                    <p className="text-gray-500 text-sm leading-relaxed font-serif italic">{feature.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                <section className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5">
                    <div className="max-w-5xl mx-auto text-center space-y-12 sm:space-y-12">
                        <h2 className="text-2xl sm:text-3xl font-serif italic mb-8 sm:mb-12">Protocol Foundations</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 sm:gap-20 text-left">
                            <div className="space-y-4 sm:space-y-6">
                                <h4 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-widest">Security Protocol</h4>
                                <h3 className="text-lg sm:text-xl font-serif">End-to-End Governance</h3>
                                <p className="text-gray-500 text-sm leading-relaxed font-serif italic">Every analysis is signed with a cryptographic audit trail, ensuring that regulatory decisions are backed by verifiable data provenance and internal policy alignment. We utilize AES-256 encryption for data at rest and TLS 1.3 for all neural links.</p>
                            </div>
                            <div className="space-y-4 sm:space-y-6">
                                <h4 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-widest">Deployment Flex</h4>
                                <h3 className="text-lg sm:text-xl font-serif">Hybrid Cloud & On-Prem</h3>
                                <p className="text-gray-500 text-sm leading-relaxed font-serif italic">Deploy the Leagle neural engine in your secure VPC or utilize our Tier-IV managed infrastructure. Our architecture supports high-availability clusters across Redis, Vector Base, and PostgreSQL to ensure zero-downtime compliance monitoring.</p>
                            </div>
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
