export default function CapabilityCard({ icon, title, description }) {
    return (
        <div className="glass-card p-6 sm:p-10 flex flex-col gap-6 hover:border-leagle-accent/40 transition-all group cursor-default rounded-sm">
            <div className="w-14 h-14 rounded-sm bg-leagle-accent/5 border border-leagle-accent/10 flex items-center justify-center group-hover:bg-leagle-accent/10 transition-colors">
                <div className="text-leagle-accent">{icon}</div>
            </div>
            <div>
                <h3 className="text-xl sm:text-2xl font-serif italic mb-3">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed font-serif italic">{description}</p>
            </div>
        </div>
    );
}
