import LandingNavbar from '../components/LandingNavbar';
import { Target, Search, FileText, ArrowRight } from 'lucide-react';
import Image from 'next/image';

export default function SolutionsPage() {
    return (
        <div className="min-h-dvh bg-[var(--leagle-bg)] text-white">
            <LandingNavbar />

            <main className="pt-24 sm:pt-40">
                {/* Hero section */}
                <section className="relative px-4 sm:px-6 pb-20 sm:pb-32 overflow-hidden">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.03)_0%,transparent_70%)] -z-10" />
                    <div className="max-w-7xl mx-auto">
                        <header className="max-w-3xl mb-12 sm:mb-20 animate-in fade-in slide-in-from-bottom-8 duration-700">
                            <h2 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em] mb-4 sm:mb-6">Strategic Applications</h2>
                            <h1 className="text-4xl sm:text-5xl md:text-7xl font-serif italic mb-6 sm:mb-8 leading-tight">Tailored Intelligence for <span className="text-gradient block sm:inline">Every Department</span></h1>
                            <p className="text-lg sm:text-xl text-gray-500 font-serif italic leading-relaxed">Specific compliance modules architected for the unique pressures of legal counsel, risk officers, and board executives. Leagle scales with your organizational complexity.</p>
                        </header>
                    </div>
                </section>

                {/* Solutions Grid */}
                <section className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5 bg-white/[0.01]">
                    <div className="max-w-7xl mx-auto">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 sm:gap-16">
                            {[
                                { title: "Legal Counsel", desc: "Automate policy-to-reg alignment and remediation roadmap generation. Reduce non-billable research time by 80% with neural-verified citations.", icon: <FileText /> },
                                { title: "Risk & Compliance", desc: "Real-time alert monitoring across institutional data silos. Our engine flags potential regulatory drifts before they become liabilities.", icon: <Search /> },
                                { title: "Executive Audit", desc: "High-level briefings and strategic impact verdicts for board members. Get a weighted risk score for entering new global markets.", icon: <Target /> },
                                { title: "Policy Ingest", desc: "Rapid normalization of internal documents into queryable intelligence. Turn static employee handbooks into dynamic, searchable compliance links.", icon: <ArrowRight /> }
                            ].map((sol, i) => (
                                <div key={i} className="glass-card p-8 sm:p-16 flex flex-col sm:flex-row gap-6 sm:gap-10 hover:border-leagle-accent/30 transition-all rounded-sm group">
                                    <div className="w-12 h-12 sm:w-16 sm:h-16 bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 group-hover:text-leagle-accent group-hover:bg-leagle-accent/5 transition-all shrink-0">
                                        {sol.icon}
                                    </div>
                                    <div className="space-y-3 sm:space-y-4">
                                        <h3 className="text-2xl sm:text-3xl font-serif italic">{sol.title}</h3>
                                        <p className="text-gray-500 font-serif italic leading-relaxed">{sol.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                <section className="py-20 sm:py-40 px-4 sm:px-6 border-t border-white/5 relative overflow-hidden">
                    <div className="max-w-3xl mx-auto text-center space-y-8 sm:space-y-12">
                        <h2 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-[0.3em]">Institutional Trust</h2>
                        <h3 className="text-3xl sm:text-4xl font-serif italic">Beyond Software. Legal Certainty.</h3>
                        <p className="text-base sm:text-lg text-gray-500 font-serif italic leading-relaxed">
                            "Leagle Intelligence gives our firm the horizontal oversight required to manage multi-jurisdictional compliance without expanding our headcount. It is the gold standard for neural legal research."
                        </p>
                        <div className="pt-4 sm:pt-8">
                            <div className="h-px w-16 sm:w-20 bg-leagle-accent mx-auto mb-4 sm:mb-6" />
                            <p className="text-[10px] sm:text-xs font-black uppercase tracking-widest text-white italic">General Counsel, Tier-1 Global Financial Hub</p>
                        </div>
                    </div>
                </section>

                <section className="py-16 sm:py-20 px-4 sm:px-6 border-t border-white/5 bg-white/[0.01]">
                    <div className="max-w-7xl mx-auto text-center space-y-6 sm:space-y-8">
                        <h4 className="text-leagle-accent text-[10px] sm:text-xs font-black uppercase tracking-widest">Global Reach</h4>
                        <h3 className="text-xl sm:text-2xl font-serif italic text-white text-gradient">Jurisdictional Coverage</h3>
                        <div className="flex flex-wrap justify-center gap-6 sm:gap-12 pt-6 sm:pt-8">
                            {['United Kingdom', 'European Union', 'United States', 'MENA Region', 'APAC Cluster'].map((region, i) => (
                                <div key={i} className="text-xs sm:text-sm font-serif italic text-gray-500 border-b border-white/10 pb-2">{region}</div>
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
