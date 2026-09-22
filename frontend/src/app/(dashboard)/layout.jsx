import Navigation from '../components/Navigation'

// @next-codemod-ignore Cache Components adoption: this segment temporarily allows blocking.
// Remove this opt-out after verifying the segment passes validation without it.
// See: https://nextjs.org/docs/app/guides/migrating-to-cache-components
export const instant = false;

export default function DashboardLayout({ children }) {
    return (
        <>
            <Navigation />
            {/*
              On mobile: Navigation renders a top bar (h-14), so we add pt-14.
              On md+:    Navigation renders a fixed left sidebar (w-[76px]), so we add md:pl-[76px] and remove the top padding.
            */}
            <div className="pt-14 md:pt-0 md:pl-[76px] min-h-dvh flex flex-col">
                <header className="cm-shell-header sticky top-0 z-20 px-4 sm:px-8 flex items-center justify-between border-b border-leagle-accent/10">
                    <div className="flex items-center gap-4">
                        <h1 className="text-lg sm:text-2xl italic font-serif tracking-tight text-white">
                            <span className="text-leagle-accent">Leagle</span>{' '}
                            <span className="text-gray-500 font-light opacity-50">Intelligence</span>
                        </h1>
                    </div>
                    <div className="flex items-center gap-3 bg-white/2 px-3 sm:px-4 py-2 border border-white/5 rounded-sm">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" aria-hidden="true" />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-500/80 italic font-serif hidden sm:block">Awaiting Directives</span>
                    </div>
                </header>
                <div className="h-[2px] w-full bg-leagle-accent/40 sticky top-[68px] z-20 shadow-[0_1px_10px_rgba(197,160,89,0.2)]" aria-hidden="true" />

                <main className="flex-1 p-4 sm:p-8 lg:p-12 overflow-x-hidden">
                    {children}
                </main>
            </div>
        </>
    )
}
