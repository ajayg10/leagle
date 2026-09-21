import { useEffect } from 'react'
import { useAppStore } from '../store/appStore'
import { Bell, AlertTriangle, Activity, Zap } from 'lucide-react'

export default function AlertsPanel() {
    const { alerts, unreadCount, markRead, connected } = useAppStore()

    useEffect(() => {
        if (unreadCount > 0) {
            markRead()
        }
    }, [unreadCount, markRead])

    const getSeverityStyles = (severity) => {
        switch (severity) {
            case 'HIGH': return 'border-red-500/30 text-red-400'
            case 'MEDIUM': return 'border-amber-500/30 text-amber-400'
            default: return 'border-leagle-accent/30 text-leagle-accent'
        }
    }

    return (
        <div className="glass-card overflow-hidden h-full flex flex-col border-white/5 shadow-2xl rounded-sm">
            <div className="p-5 border-b border-white/5 bg-white/[0.02] flex justify-between items-center shrink-0">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-leagle-accent/5 rounded-sm flex items-center justify-center text-leagle-accent border border-leagle-accent/10">
                        <Bell size={16} />
                    </div>
                    <div>
                        <h2 className="text-sm font-serif text-white italic tracking-tight">Intelligence Stream</h2>
                        <p className="text-[7px] font-black text-leagle-accent/50 uppercase tracking-[0.25em]">Directives</p>
                    </div>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {alerts.length === 0 ? (
                    <div className="p-16 text-center opacity-30">
                        <p className="text-[9px] font-black uppercase tracking-widest text-gray-500 italic">No Active Intel</p>
                    </div>
                ) : (
                    <div className="divide-y divide-white/[0.02]">
                        {alerts.map((alert, idx) => (
                            <div
                                key={alert.id || idx}
                                className={`p-4 flex gap-4 transition-all hover:bg-white/[0.01] group border-l-2 ${getSeverityStyles(alert.severity).split(' ')[0]}`}
                            >
                                <div className="mt-0.5 shrink-0">
                                    {alert.severity === 'HIGH' ? <Zap size={12} className="text-red-500/70" /> : <AlertTriangle size={12} className="text-amber-500/70" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-center mb-1">
                                        <span className={`text-[7px] font-black tracking-[0.15em] uppercase ${getSeverityStyles(alert.severity).split(' ')[1]}`}>
                                            {alert.severity}
                                        </span>
                                        <span className="text-[7px] text-gray-600 font-mono opacity-50 tracking-tighter">UTC // LIVE</span>
                                    </div>
                                    <p className="text-[11px] text-gray-400 font-medium leading-relaxed group-hover:text-gray-200 transition-colors">
                                        {alert.message}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="p-3 px-5 bg-white/[0.01] border-t border-white/5 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-2">
                    <div className={`w-1 h-1 rounded-full ${connected ? 'bg-leagle-accent shadow-[0_0_8px_rgba(33,234,166,0.4)]' : 'bg-red-500/40'} `}></div>
                    <span className="text-[7px] font-black text-gray-500 uppercase tracking-widest">
                        Status: {connected ? 'Active' : 'Offline'}
                    </span>
                </div>
                <Activity size={8} className="text-leagle-accent/20" />
            </div>
        </div>
    )
}
