import { ClerkProvider } from '@clerk/nextjs'
import QueryProvider from './components/QueryProvider'
import WebSocketInitializer from './components/WebSocketInitializer'
import './globals.css'

export const metadata = {
    title: 'Leagle Compliance Operations',
    description: 'Regulation analysis and policy impact assessment',
}

export const viewport = {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
}

export default function RootLayout({ children }) {
    return (
        <ClerkProvider>
            <html lang="en">
                <head>
                    <link rel="icon" href="/logo.png" />
                    <link rel="preconnect" href="https://fonts.googleapis.com" />
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800;900&family=Source+Serif+4:ital,opsz,wght@0,8..60,200..900;1,8..60,200..900&display=swap" rel="stylesheet" />
                </head>
                <body className="antialiased min-h-dvh selection:bg-leagle-accent/30 cm-shell-bg">
                    <QueryProvider>
                        <WebSocketInitializer />
                        {children}
                    </QueryProvider>
                </body>
            </html>
        </ClerkProvider>
    )
}
