import React from 'react';
import { Hash, Download, Database, Search } from 'lucide-react';

const KeywordDatabase = () => {
    return (
        <div className="max-w-5xl mx-auto">
            <div className="card text-center py-16">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-[var(--bg-element)] border-2 border-[var(--border-subtle)] mb-6">
                    <Hash size={36} className="text-[var(--text-secondary)]" />
                </div>
                
                <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-3">
                    Keyword Database
                </h2>
                
                <p className="text-[var(--text-secondary)] mb-6 max-w-md mx-auto">
                    Organize and manage your keywords by category with short-tail, medium-tail, and long-tail classifications.
                </p>

                <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full text-sm font-medium">
                    <Database size={14} />
                    Coming Soon
                </div>

                <div className="mt-12 grid md:grid-cols-3 gap-6 text-left max-w-3xl mx-auto">
                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <Search size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            Smart Organization
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Categorize keywords by product type and search intent
                        </p>
                    </div>

                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <Hash size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            Tail Classification
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Separate short, medium, and long-tail keywords
                        </p>
                    </div>

                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <Download size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            CSV Export
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Export your keyword database for external use
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default KeywordDatabase;
