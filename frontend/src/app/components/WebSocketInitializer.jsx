"use client"

import { useWebSocket } from '../hooks/useWebSocket'

export default function WebSocketInitializer() {
    useWebSocket()
    return null // This component doesn't render anything
}
