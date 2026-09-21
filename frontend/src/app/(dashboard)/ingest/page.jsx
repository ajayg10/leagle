'use client'

import Ingest from '../../components/Ingest'
import { Upload } from 'lucide-react'

export default function IngestPage() {
    return (
        <div className="glass-card p-8 border border-white/10">
            <h2 className="text-2xl font-black text-white mb-6 flex items-center gap-3">
                <span className="bg-leagle-accent/10 text-leagle-accent w-8 h-8 rounded-lg flex items-center justify-center border border-leagle-accent/20">
                    <Upload size={16} />
                </span>
                Document Ingestion
            </h2>
            <Ingest />
        </div>
    )
}
