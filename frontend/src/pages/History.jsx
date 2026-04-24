import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { Clock, ArrowRight, RefreshCcw, ExternalLink } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { sanitizeRichHtml } from '../utils/sanitizeHtml';

const chipClass = 'px-2 py-1 rounded-full text-xs font-medium bg-[var(--bg-element)] border border-[var(--border-subtle)] text-[var(--text-secondary)]';

const History = () => {
    const { token } = useAuth();
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchHistory = useCallback(async () => {
        if (!token) return;
        try {
            setLoading(true);
            setError('');
            const response = await axios.get('/api/optimize/history', {
                headers: { Authorization: `Bearer ${token}` },
            });
            setEntries(response.data.entries || []);
        } catch (err) {
            setError(err.response?.data?.detail || 'Unable to load history');
        } finally {
            setLoading(false);
        }
    }, [token]);

    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);

    if (!token) {
        return (
            <div className="card text-center">
                <p className="text-[var(--text-secondary)]">Please sign in to view your optimization history.</p>
            </div>
        );
    }

    const renderKeywords = (keywords = []) => (
        <div className="flex flex-wrap gap-2">
            {(keywords || []).slice(0, 6).map((kw, idx) => (
                <span key={`${kw}-${idx}`} className={chipClass}>{kw}</span>
            ))}
            {(keywords || []).length > 6 && (
                <span className={chipClass}>+{keywords.length - 6} more</span>
            )}
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-[var(--text-primary)]">Optimization History</h2>
                    <p className="text-sm text-[var(--text-secondary)]">Review every listing you've refined with Shakti.</p>
                </div>
                <button
                    onClick={fetchHistory}
                    className="btn btn-secondary w-full md:w-auto"
                    disabled={loading}
                >
                    <RefreshCcw size={16} className={loading ? 'animate-spin' : ''} /> Refresh
                </button>
            </div>

            {loading && (
                <div className="card">
                    <p className="text-sm text-[var(--text-secondary)]">Loading your history...</p>
                </div>
            )}

            {!loading && error && (
                <div className="p-4 bg-[var(--error-bg)] border border-[var(--error)]/30 text-[var(--error)] rounded-lg text-sm">
                    {error}
                </div>
            )}

            {!loading && !error && entries.length === 0 && (
                <div className="card text-center space-y-3">
                    <div className="w-14 h-14 mx-auto rounded-full bg-[var(--bg-element)] flex items-center justify-center">
                        <Clock size={26} className="text-[var(--text-tertiary)]" />
                    </div>
                    <h3 className="font-semibold text-[var(--text-primary)]">No history yet</h3>
                    <p className="text-sm text-[var(--text-secondary)]">Run an optimization to start building your review panel.</p>
                </div>
            )}

            <div className="space-y-4">
                {entries.map((entry) => {
                    const finalListing = entry.final;
                    return (
                        <div key={entry.entry_id} className="card space-y-4">
                            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                                <div>
                                    <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-[var(--text-secondary)]">
                                        <span className="badge badge-blue">
                                            {entry.mode === 'batch' ? 'Batch' : 'Single'}
                                        </span>
                                        <span>Saved {new Date(entry.created_at).toLocaleString()}</span>
                                        {entry.row_id && (
                                            <span className="text-[var(--text-tertiary)]">Row #{entry.row_id}</span>
                                        )}
                                    </div>
                                    <h3 className="text-lg font-semibold text-[var(--text-primary)] mt-2">
                                        {finalListing?.new_title || entry.prev_title || 'Untitled'}
                                    </h3>
                                    {entry.product_link && (
                                        <a
                                            href={entry.product_link}
                                            className="inline-flex items-center gap-1 text-xs text-[var(--accent)] hover:underline"
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            View source <ExternalLink size={12} />
                                        </a>
                                    )}
                                </div>
                                {finalListing && (
                                    <button
                                        className="btn btn-primary w-full md:w-auto"
                                        onClick={() => {
                                            navigator.clipboard.writeText(finalListing.new_title + '\n' + (finalListing.new_description || ''));
                                        }}
                                    >
                                        Copy Listing <ArrowRight size={16} />
                                    </button>
                                )}
                            </div>

                            {finalListing?.new_description && (
                                <div className="bg-[var(--bg-element)] border border-[var(--border-subtle)] rounded-lg p-4 text-sm text-[var(--text-secondary)]">
                                    <div dangerouslySetInnerHTML={{ __html: sanitizeRichHtml(finalListing.new_description) }} />
                                </div>
                            )}

                            {finalListing && (
                                <div className="grid gap-4 md:grid-cols-3">
                                    <div>
                                        <p className="text-xs uppercase tracking-wide text-[var(--text-secondary)] mb-2">Short Keywords</p>
                                        {renderKeywords(finalListing.keywords_short)}
                                    </div>
                                    <div>
                                        <p className="text-xs uppercase tracking-wide text-[var(--text-secondary)] mb-2">Mid Keywords</p>
                                        {renderKeywords(finalListing.keywords_mid)}
                                    </div>
                                    <div>
                                        <p className="text-xs uppercase tracking-wide text-[var(--text-secondary)] mb-2">Long Keywords</p>
                                        {renderKeywords(finalListing.keywords_long)}
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default History;
