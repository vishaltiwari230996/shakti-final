import React from 'react';
import { Folder, Users, Tag, Grid } from 'lucide-react';

const SKUGroups = () => {
    return (
        <div className="max-w-5xl mx-auto">
            <div className="card text-center py-16">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-[var(--bg-element)] border-2 border-[var(--border-subtle)] mb-6">
                    <Folder size={36} className="text-[var(--text-secondary)]" />
                </div>
                
                <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-3">
                    SKU Groups
                </h2>
                
                <p className="text-[var(--text-secondary)] mb-6 max-w-md mx-auto">
                    Organize your optimized SKUs into custom groups for better management and tracking.
                </p>

                <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full text-sm font-medium">
                    <Grid size={14} />
                    Coming Soon
                </div>

                <div className="mt-12 grid md:grid-cols-3 gap-6 text-left max-w-3xl mx-auto">
                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <Folder size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            Custom Groups
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Create unlimited groups to organize your SKUs
                        </p>
                    </div>

                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <Tag size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            Color Coding
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Assign colors to groups for visual identification
                        </p>
                    </div>

                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <Users size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            Easy Management
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Drag and drop SKUs between groups
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SKUGroups;
