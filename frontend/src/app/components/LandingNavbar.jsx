'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Menu, X } from 'lucide-react';
import { Show, UserButton, SignInButton, SignUpButton } from '@clerk/nextjs';

const NAV_LINKS = [
    { href: '/platform', label: 'Platform' },
    { href: '/solutions', label: 'Solutions' },
    { href: '/api', label: 'API' },
    { href: '/enterprise', label: 'Enterprise' },
    { href: '/pricing', label: 'Pricing' },
];

export default function LandingNavbar() {
    const [mobileOpen, setMobileOpen] = useState(false);

    return (
        <header className="fixed top-0 w-full z-50 bg-[var(--leagle-bg)]/80 backdrop-blur-md border-b border-leagle-accent/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 sm:h-20 flex items-center justify-between">
                {/* Logo + desktop nav */}
                <div className="flex items-center gap-8 lg:gap-12">
                    <Link href="/" className="flex items-center gap-2.5 group shrink-0">
                        <Image
                            src="/logo.png"
                            alt="Leagle Logo"
                            width={32}
                            height={32}
                            className="group-hover:scale-110 transition-transform"
                        />
                        <span className="text-lg sm:text-xl font-bold tracking-tight text-white font-serif italic">
                            Leagle <span className="text-leagle-accent">Intelligence</span>
                        </span>
                    </Link>

                    {/* Desktop nav — hidden on mobile */}
                    <nav className="hidden md:flex items-center gap-6 lg:gap-8 text-[11px] font-black uppercase tracking-[0.2em] text-gray-500" aria-label="Main navigation">
                        {NAV_LINKS.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className="hover:text-leagle-accent transition-colors py-1"
                            >
                                {link.label}
                            </Link>
                        ))}
                    </nav>
                </div>

                {/* Right: auth buttons + hamburger */}
                <div className="flex items-center gap-3 sm:gap-4">
                    <Show when="signed-out">
                        <SignInButton>
                            <button className="hidden sm:block text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-white px-3 transition-colors cursor-pointer min-h-[44px]">
                                Sign In
                            </button>
                        </SignInButton>
                        <SignUpButton>
                            <button className="btn-premium px-4 sm:px-6 py-2.5 text-[10px] font-black uppercase tracking-[0.2em] cursor-pointer min-h-[44px]">
                                Access Hub
                            </button>
                        </SignUpButton>
                    </Show>
                    <Show when="signed-in">
                        <Link
                            href="/dashboard"
                            className="hidden sm:block text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-white px-3 transition-colors min-h-[44px] flex items-center"
                        >
                            Control Center
                        </Link>
                        <UserButton
                            appearance={{
                                elements: {
                                    userButtonAvatarBox: 'w-9 h-9 border border-leagle-accent/20',
                                },
                            }}
                        />
                    </Show>

                    {/* Hamburger — visible on mobile only */}
                    <button
                        className="md:hidden flex items-center justify-center w-11 h-11 text-gray-400 hover:text-white transition-colors"
                        onClick={() => setMobileOpen((o) => !o)}
                        aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
                        aria-expanded={mobileOpen}
                        aria-controls="mobile-nav"
                    >
                        {mobileOpen ? <X size={22} /> : <Menu size={22} />}
                    </button>
                </div>
            </div>

            {/* Mobile drawer */}
            {mobileOpen && (
                <nav
                    id="mobile-nav"
                    className="md:hidden bg-[var(--leagle-bg)] border-t border-white/5 px-4 pb-6 pt-4 space-y-1"
                    aria-label="Mobile navigation"
                >
                    {NAV_LINKS.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            onClick={() => setMobileOpen(false)}
                            className="block py-3 px-2 text-sm font-black uppercase tracking-[0.15em] text-gray-400 hover:text-leagle-accent border-b border-white/5 transition-colors min-h-[44px] flex items-center"
                        >
                            {link.label}
                        </Link>
                    ))}
                    <Show when="signed-in">
                        <Link
                            href="/dashboard"
                            onClick={() => setMobileOpen(false)}
                            className="block py-3 px-2 text-sm font-black uppercase tracking-[0.15em] text-leagle-accent min-h-[44px] flex items-center"
                        >
                            Control Center
                        </Link>
                    </Show>
                    <Show when="signed-out">
                        <SignInButton>
                            <button
                                onClick={() => setMobileOpen(false)}
                                className="w-full mt-4 py-3 text-sm font-black uppercase tracking-widest text-gray-400 border border-white/10 hover:text-white transition-colors min-h-[44px]"
                            >
                                Sign In
                            </button>
                        </SignInButton>
                    </Show>
                </nav>
            )}
        </header>
    );
}
