import React from 'react';
import { FileText, Clock, TrendingUp } from 'lucide-react';

const AnalysisHistory = () => {
    return (
        <div className="max-w-5xl mx-auto">
            <div className="card text-center py-16">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-[var(--bg-element)] border-2 border-[var(--border-subtle)] mb-6">
                    <FileText size={36} className="text-[var(--text-secondary)]" />
                </div>
                
                <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-3">
                    Analysis History
                </h2>
                
                <p className="text-[var(--text-secondary)] mb-6 max-w-md mx-auto">
                    Track your product analysis history with detailed insights and performance metrics.
                </p>

                <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full text-sm font-medium">
                    <Clock size={14} />
                    Coming Soon
                </div>

                <div className="mt-12 grid md:grid-cols-3 gap-6 text-left max-w-3xl mx-auto">
                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <TrendingUp size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            Performance Tracking
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Monitor how your analyzed products perform over time
                        </p>
                    </div>

                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <FileText size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            Detailed Reports
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Access comprehensive analysis reports and recommendations
                        </p>
                    </div>

                    <div className="p-4 bg-[var(--bg-element)] rounded-xl border border-[var(--border-subtle)]">
                        <Clock size={20} className="text-[var(--accent)] mb-2" />
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                            Historical Data
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)]">
                            Compare current and past analysis results
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalysisHistory;
