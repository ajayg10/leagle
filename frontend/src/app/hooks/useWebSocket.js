"use client"

import { useEffect } from 'react'
import { useAppStore } from '../store/appStore'
import { getAlerts } from '../api/client'

export function useWebSocket() {
    const { addAlerts, setAlerts, setConnected } = useAppStore()

    useEffect(() => {
        // Initial Fetch
        async function fetchInitial() {
            try {
                const res = await getAlerts()
                setAlerts(res.data || [])
            } catch (err) {
                console.error('Failed to seed alerts:', err)
            }
        }
        fetchInitial()

        const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '')
        const wsUrl = API_BASE_URL.replace(/^http/, 'ws') + '/api/alerts/ws'
        console.log('📡 Attempting WebSocket Connection:', wsUrl)

        // Connect to Raw WebSocket gateway
        const socket = new WebSocket(wsUrl)

        socket.onopen = () => {
            console.log('✅ Connected to Real-time Feed')
            setConnected(true)
        }

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                if (data.type === 'alerts') {
                    console.log('📣 New Real-time Alerts:', data.data)
                    addAlerts(data.data)
                }
            } catch (err) {
                console.error('WS Message Parse Error:', err)
            }
        }

        socket.onerror = (error) => {
            console.error('❌ WebSocket Handshake Error:', error)
        }

        socket.onclose = (event) => {
            console.log('❌ Disconnected from Feed:', event.reason)
            setConnected(false)
        }

        return () => socket.close()
    }, [addAlerts, setAlerts, setConnected])
}
