'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Scale, Search, Upload, BarChart3, Bell, Target, RefreshCw, Menu, X } from 'lucide-react'
import { UserButton } from '@clerk/nextjs'

const tabs = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Regulations', path: '/regulations', icon: Scale },
    { name: 'Search', path: '/search', icon: Search },
    { name: 'Ingest', path: '/ingest', icon: Upload },
    { name: 'Heatmap', path: '/heatmap', icon: BarChart3 },
    { name: 'Alerts', path: '/alerts', icon: Bell },
    { name: 'Impact', path: '/impact', icon: Target },
]

export default function Navigation() {
    const pathname = usePathname()
    const [syncLoading, setSyncLoading] = useState(false)
    const [syncMessage, setSyncMessage] = useState('')
    const [mobileOpen, setMobileOpen] = useState(false)

    const handleSync = async () => {
        setSyncLoading(true)
        setSyncMessage('Sync in progress...')
        try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            const token = window.Clerk?.session
                ? await window.Clerk.session.getToken()
                : null
            const headers = { 'Content-Type': 'application/json' }
            if (token) headers['Authorization'] = `Bearer ${token}`
            const resp = await fetch(`${API_BASE_URL}/api/regulations/sync/all`, {
                method: 'POST',
                headers,
            })
            const data = await resp.json()
            const total = data.results?.total || 0
            setSyncMessage(`Sync complete: ${total} updated.`)
            setTimeout(() => window.location.reload(), 2000)
        } catch {
            setSyncMessage('Sync failed. Try again.')
        } finally {
            setSyncLoading(false)
        }
    }

    const isActive = (path) =>
        pathname === path || (pathname === '/' && path === '/dashboard')

    // ── Desktop sidebar (visible on md+) ───────────────────────────────────
    const SidebarContent = ({ onLinkClick }) => (
        <>
            <div className="w-full py-[18px] border-b border-white/5 flex justify-center">
                <Link href="/" className="w-8 h-8 flex items-center justify-center" onClick={onLinkClick}>
                    <Image src="/logo.png" alt="Leagle Logo" width={28} height={28} />
                </Link>
            </div>

            <nav className="flex-1 w-full py-2.5 flex flex-col gap-px" aria-label="Dashboard navigation">
                {tabs.map((tab) => {
                    const active = isActive(tab.path)
                    const Icon = tab.icon
                    return (
                        <Link
                            key={tab.path}
                            href={tab.path}
                            title={tab.name}
                            onClick={onLinkClick}
                            aria-label={tab.name}
                            aria-current={active ? 'page' : undefined}
                            className={`cm-nav-item ${active ? 'active' : ''}`}
                        >
                            <Icon
                                size={17}
                                strokeWidth={1.8}
                                className={active ? 'text-leagle-accent' : 'text-slate-500'}
                                aria-hidden="true"
                            />
                            <span className={`text-[9px] font-bold tracking-[0.07em] uppercase ${active ? 'text-leagle-accent' : 'text-slate-500'}`}>
                                {tab.name}
                            </span>
                        </Link>
                    )
                })}
            </nav>

            <div className="w-full py-4 border-t border-white/5 flex flex-col items-center gap-4">
                <button
                    onClick={handleSync}
                    disabled={syncLoading}
                    title="Sync All Jurisdictions"
                    aria-label="Sync all regulatory jurisdictions"
                    className="w-10 h-10 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-slate-200 transition-colors disabled:opacity-50"
                >
                    <RefreshCw size={14} className={syncLoading ? 'animate-spin' : ''} aria-hidden="true" />
                </button>

                <UserButton
                    appearance={{
                        elements: {
                            userButtonAvatarBox: 'w-10 h-10 border border-leagle-accent/20 hover:border-leagle-accent transition-colors',
                        },
                    }}
                />

                <div className="flex flex-col items-center gap-1" aria-hidden="true">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.7)] animate-[cm-pulse_2s_ease-in-out_infinite]" />
                    <span className="text-[7px] font-extrabold uppercase tracking-widest text-green-400/40">Live</span>
                </div>
            </div>
        </>
    )

    return (
        <>
            {/* ── Desktop sidebar: visible md+ ─────────────────────────── */}
            <aside
                className="hidden md:flex fixed left-0 top-0 bottom-0 w-[76px] min-h-screen shrink-0 bg-[rgba(2,9,22,0.98)] border-r border-[rgba(56,189,248,0.09)] z-30 flex-col items-center"
                aria-label="Sidebar"
            >
                <SidebarContent onLinkClick={undefined} />

                {syncMessage && (
                    <p
                        role="status"
                        className="absolute bottom-16 left-[88px] px-3 py-1.5 rounded-lg border border-white/10 bg-[rgba(2,9,22,0.96)] text-[10px] uppercase tracking-widest text-slate-400 whitespace-nowrap"
                    >
                        {syncMessage}
                    </p>
                )}
            </aside>

            {/* ── Mobile top bar: visible below md ─────────────────────── */}
            <div className="md:hidden fixed top-0 left-0 right-0 h-14 bg-[rgba(2,9,22,0.98)] border-b border-[rgba(56,189,248,0.09)] z-30 flex items-center justify-between px-4">
                <Link href="/" className="flex items-center gap-2">
                    <Image src="/logo.png" alt="Leagle Logo" width={24} height={24} />
                    <span className="text-sm font-serif italic text-white">
                        Leagle <span className="text-leagle-accent">Intelligence</span>
                    </span>
                </Link>
                <div className="flex items-center gap-3">
                    <UserButton
                        appearance={{
                            elements: { userButtonAvatarBox: 'w-8 h-8 border border-leagle-accent/20' },
                        }}
                    />
                    <button
                        onClick={() => setMobileOpen((o) => !o)}
                        aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
                        aria-expanded={mobileOpen}
                        aria-controls="mobile-drawer"
                        className="w-10 h-10 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
                    >
                        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>
            </div>

            {/* ── Mobile drawer ─────────────────────────────────────────── */}
            {mobileOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="md:hidden fixed inset-0 bg-black/60 z-40"
                        onClick={() => setMobileOpen(false)}
                        aria-hidden="true"
                    />
                    <nav
                        id="mobile-drawer"
                        aria-label="Dashboard navigation"
                        className="md:hidden fixed left-0 top-14 bottom-0 w-64 bg-[rgba(2,9,22,0.99)] border-r border-white/10 z-50 flex flex-col overflow-y-auto"
                    >
                        <div className="flex-1 py-4 px-3 space-y-1">
                            {tabs.map((tab) => {
                                const active = isActive(tab.path)
                                const Icon = tab.icon
                                return (
                                    <Link
                                        key={tab.path}
                                        href={tab.path}
                                        onClick={() => setMobileOpen(false)}
                                        aria-current={active ? 'page' : undefined}
                                        className={`flex items-center gap-3 px-4 py-3 min-h-[48px] rounded-sm transition-colors ${active ? 'bg-leagle-accent/10 text-leagle-accent border-l-2 border-leagle-accent' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
                                    >
                                        <Icon size={18} strokeWidth={1.8} aria-hidden="true" />
                                        <span className="text-sm font-bold uppercase tracking-wider">{tab.name}</span>
                                    </Link>
                                )
                            })}
                        </div>
                        <div className="p-4 border-t border-white/5">
                            <button
                                onClick={() => { handleSync(); setMobileOpen(false) }}
                                disabled={syncLoading}
                                className="w-full flex items-center gap-3 px-4 py-3 min-h-[48px] text-slate-400 hover:text-white border border-white/10 rounded-sm hover:bg-white/5 transition-colors disabled:opacity-50"
                            >
                                <RefreshCw size={16} className={syncLoading ? 'animate-spin' : ''} aria-hidden="true" />
                                <span className="text-xs font-bold uppercase tracking-widest">Sync All Jurisdictions</span>
                            </button>
                            {syncMessage && (
                                <p role="status" className="mt-2 text-[10px] text-slate-500 uppercase tracking-widest">{syncMessage}</p>
                            )}
                        </div>
                    </nav>
                </>
            )}
        </>
    )
}
