import { create } from 'zustand'

export const useAppStore = create((set) => ({
    alerts: [],
    unreadCount: 0,
    connected: false,
    addAlerts: (newAlerts) =>
        set((state) => {
            const combined = [...newAlerts, ...state.alerts]
            const unique = combined.reduce((acc, current) => {
                const x = acc.find(item => item.id === current.id);
                if (!x) {
                    return acc.concat([current]);
                } else {
                    return acc;
                }
            }, []);
            return {
                alerts: unique.slice(0, 100),
                unreadCount: state.unreadCount + newAlerts.length,
            }
        }),
    setAlerts: (initialAlerts) =>
        set({
            alerts: initialAlerts,
            unreadCount: initialAlerts.filter(a => !a.is_read).length
        }),
    markRead: () => set({ unreadCount: 0 }),
    setConnected: (connected) => set({ connected }),
}))
