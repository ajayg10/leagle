"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  const isActive = (path) => pathname === path || pathname.startsWith(path + "/");

  return (
    <nav className="bg-slate-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo/Brand */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-xl font-bold">Compliance</span>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center space-x-8">
            <Link
              href="/"
              className={`px-3 py-2 text-sm font-medium rounded-md ${isActive("/") && pathname === "/"
                  ? "bg-slate-700 text-white"
                  : "hover:bg-slate-700"
                }`}
            >
              Dashboard
            </Link>

            <Link
              href="/regulations"
              className={`px-3 py-2 text-sm font-medium rounded-md ${isActive("/regulations")
                  ? "bg-slate-700 text-white"
                  : "hover:bg-slate-700"
                }`}
            >
              Regulations
            </Link>

            <Link
              href="/policies"
              className={`px-3 py-2 text-sm font-medium rounded-md ${isActive("/policies")
                  ? "bg-slate-700 text-white"
                  : "hover:bg-slate-700"
                }`}
            >
              Policies
            </Link>

            <a
              href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-700"
            >
              API Docs ↗
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
