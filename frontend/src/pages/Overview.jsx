import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../utils/apiConfig';
import {
    ArrowUpRight,
    ArrowDownRight,
    Activity,
    BarChart3,
    Zap,
    Layers,
    Target,
    Plus,
    MoreHorizontal,
    RefreshCw,
    ChevronRight,
    Clock,
    Inbox,
    Loader2,
    Circle,
    Sparkles,
    Hash,
    Settings as SettingsIcon,
} from 'lucide-react';

/* ─── Helpers ─── */
const statusLabel = { complete: 'Complete', running: 'Running', queued: 'Queued' };

function useAnimatedNumber(target, duration = 1100) {
    const [value, setValue] = useState(0);
    useEffect(() => {
        let start = null;
        const step = (ts) => {
            if (!start) start = ts;
            const progress = Math.min((ts - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            setValue(target * eased);
            if (progress < 1) requestAnimationFrame(step);
        };
        const raf = requestAnimationFrame(step);
        return () => cancelAnimationFrame(raf);
    }, [target, duration]);
    return value;
}

function formatNumber(n, decimals = 0) {
    if (decimals > 0) return n.toFixed(decimals);
    return Math.round(n).toLocaleString();
}

function timeAgo(iso) {
    if (!iso) return '—';
    const then = new Date(iso).getTime();
    if (isNaN(then)) return iso;
    const s = Math.floor((Date.now() - then) / 1000);
    if (s < 60) return `${s}s ago`;
    if (s < 3600) return `${Math.floor(s / 60)}m ago`;
    if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
    return `${Math.floor(s / 86400)}d ago`;
}

const Sparkline = ({ data, up }) => {
    const w = 80, h = 28;
    const safe = data && data.length ? data : [0, 0];
    const max = Math.max(...safe), min = Math.min(...safe);
    const range = max - min || 1;
    const points = safe.map((v, i) => {
        const x = (i / (safe.length - 1 || 1)) * w;
        const y = h - ((v - min) / range) * h;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
    const areaPoints = `0,${h} ${points} ${w},${h}`;
    const color = up ? 'var(--ink-success)' : 'var(--ink-accent)';
    return (
        <svg className="atl-sparkline" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
            <polygon points={areaPoints} fill={color} opacity="0.08" />
            <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
};

const MetricValue = ({ value, prefix, suffix, decimals }) => {
    const animated = useAnimatedNumber(value);
    return (
        <div className="atl-metric-value">
            {prefix && <span className="atl-metric-prefix">{prefix}</span>}
            <span className="atl-metric-num">{formatNumber(animated, decimals)}</span>
            {suffix && <span className="atl-metric-suffix">{suffix}</span>}
        </div>
    );
};

/* ─── Overview Page ─── */
const Overview = () => {
    const navigate = useNavigate();
    const { user, token, userStats, fetchUserStats } = useAuth();

    const [activeTab, setActiveTab] = useState('all');
    const [history, setHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [historyError, setHistoryError] = useState(null);
    const [refreshTick, setRefreshTick] = useState(0);

    const loadHistory = useCallback(async () => {
        if (!token) return;
        setHistoryLoading(true);
        setHistoryError(null);
        try {
            const res = await fetch(buildApiUrl('/optimize/history'), {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setHistory(data?.entries || []);
        } catch (err) {
            setHistoryError(err.message || 'Failed to load history');
            setHistory([]);
        } finally {
            setHistoryLoading(false);
        }
    }, [token]);

    useEffect(() => { loadHistory(); }, [loadHistory, refreshTick]);
    useEffect(() => { if (token) fetchUserStats(token); }, [token, fetchUserStats, refreshTick]);

    const optimizeUsage = userStats?.usage?.optimize || { used: 0, limit: 100, remaining: 100 };
    const analysisUsage = userStats?.usage?.product_analysis || userStats?.usage?.analysis || { used: 0, limit: 50, remaining: 50 };
    const batchUsage = userStats?.usage?.batch || { used: 0, limit: 20, remaining: 20 };

    const totalRuns = history.length;
    const singleRuns = history.filter(h => h.mode === 'single').length;
    const batchRuns = history.filter(h => h.mode === 'batch').length;

    const chartData = useMemo(() => {
        const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
        const buckets = Array(7).fill(0);
        const now = new Date();
        history.forEach(h => {
            const t = new Date(h.created_at).getTime();
            if (isNaN(t)) return;
            const ageDays = Math.floor((now.getTime() - t) / 86400000);
            if (ageDays >= 0 && ageDays < 7) {
                buckets[6 - ageDays] += 1;
            }
        });
        const startDay = new Date();
        startDay.setDate(startDay.getDate() - 6);
        const labels = [];
        for (let i = 0; i < 7; i++) {
            const d = new Date(startDay);
            d.setDate(startDay.getDate() + i);
            labels.push(days[d.getDay()]);
        }
        return buckets.map((value, i) => ({ day: labels[i], value }));
    }, [history]);

    const chartTotal = chartData.reduce((a, b) => a + b.value, 0);
    const chartMax = Math.max(...chartData.map(d => d.value), 1);
    const chartAvg = (chartTotal / 7).toFixed(1);
    const chartPeak = Math.max(...chartData.map(d => d.value));

    const metrics = useMemo(() => {
        const usagePct = (used, limit) => (!limit ? 0 : Math.min(100, Math.round((used / limit) * 100)));
        const sparkFromHistory = (mode) => {
            const buckets = Array(10).fill(0);
            const now = Date.now();
            history.forEach(h => {
                if (mode && h.mode !== mode) return;
                const t = new Date(h.created_at).getTime();
                if (isNaN(t)) return;
                const ageHrs = (now - t) / 3600000;
                const slot = 9 - Math.min(9, Math.floor(ageHrs / 6));
                if (slot >= 0 && slot < 10) buckets[slot] += 1;
            });
            return buckets;
        };
        return [
            {
                label: 'Total Optimizations', value: totalRuns, suffix: '',
                change: totalRuns > 0 ? `${totalRuns} runs` : 'No data',
                up: true, icon: BarChart3, sparkline: sparkFromHistory(null),
            },
            {
                label: 'Single Optimize', value: optimizeUsage.used || singleRuns,
                suffix: ` / ${optimizeUsage.limit || '∞'}`,
                change: `${usagePct(optimizeUsage.used, optimizeUsage.limit)}% used`,
                up: optimizeUsage.remaining > 5, icon: Zap, sparkline: sparkFromHistory('single'),
            },
            {
                label: 'Batch Runs', value: batchUsage.used || batchRuns,
                suffix: ` / ${batchUsage.limit || '∞'}`,
                change: `${usagePct(batchUsage.used, batchUsage.limit)}% used`,
                up: batchUsage.remaining > 2, icon: Layers, sparkline: sparkFromHistory('batch'),
            },
            {
                label: 'Product Analyses', value: analysisUsage.used || 0,
                suffix: ` / ${analysisUsage.limit || '∞'}`,
                change: `${usagePct(analysisUsage.used, analysisUsage.limit)}% used`,
                up: (analysisUsage.remaining ?? 1) > 2, icon: Target,
                sparkline: [0, 0, 0, 0, 0, 0, 0, 0, 0, analysisUsage.used || 0],
            },
        ];
    }, [totalRuns, singleRuns, batchRuns, optimizeUsage, batchUsage, analysisUsage, history]);

    const tabs = [
        { id: 'all', label: 'All', count: history.length },
        { id: 'single', label: 'Single', count: singleRuns },
        { id: 'batch', label: 'Batch', count: batchRuns },
    ];
    const filteredItems = activeTab === 'all' ? history : history.filter(h => h.mode === activeTab);

    const projects = useMemo(() => [
        {
            name: 'Single Optimization',
            progress: optimizeUsage.limit ? Math.min(100, Math.round((optimizeUsage.used / optimizeUsage.limit) * 100)) : 0,
            tasks: optimizeUsage.used || 0, color: '#1f1f1f',
            meta: `${optimizeUsage.remaining ?? 0} remaining`,
        },
        {
            name: 'Batch Processing',
            progress: batchUsage.limit ? Math.min(100, Math.round((batchUsage.used / batchUsage.limit) * 100)) : 0,
            tasks: batchUsage.used || 0, color: '#3a3a3a',
            meta: `${batchUsage.remaining ?? 0} remaining`,
        },
        {
            name: 'Product Analysis',
            progress: analysisUsage.limit ? Math.min(100, Math.round((analysisUsage.used / analysisUsage.limit) * 100)) : 0,
            tasks: analysisUsage.used || 0, color: '#5a5a5a',
            meta: `${analysisUsage.remaining ?? 0} remaining`,
        },
    ], [optimizeUsage, batchUsage, analysisUsage]);

    const userName = user?.name || 'there';
    const firstName = userName.split(' ')[0];
    const greeting = (() => {
        const h = new Date().getHours();
        if (h < 12) return 'Good morning';
        if (h < 17) return 'Good afternoon';
        return 'Good evening';
    })();

    return (
        <>
            {/* Hero */}
            <section className="atl-hero">
                <div>
                    <p className="atl-hero-eyebrow">
                        <Circle size={6} fill="currentColor" />
                        {historyLoading ? 'Loading workspace…' : `Live · ${totalRuns} optimizations on record`}
                    </p>
                    <h1 className="atl-hero-title">
                        {greeting}, <em>{firstName}</em>
                    </h1>
                    <p className="atl-hero-desc">
                        {totalRuns > 0
                            ? `You've run ${totalRuns} optimization${totalRuns === 1 ? '' : 's'} so far. Pick up where you left off, or start something new.`
                            : `Your workspace is ready. Start by running a single optimization or analyzing a product page.`}
                    </p>
                </div>
                <div className="atl-hero-stat">
                    <div className="atl-hero-stat-label">This Week</div>
                    <div className="atl-hero-stat-value">{chartTotal}</div>
                    <div className="atl-hero-stat-trend">
                        <ArrowUpRight size={12} /> {chartTotal > 0 ? `${chartTotal} runs` : 'Get started'}
                    </div>
                </div>
            </section>

            {/* Metrics */}
            <section className="atl-metrics">
                {metrics.map((m, i) => {
                    const Icon = m.icon;
                    return (
                        <div key={i} className="atl-metric" style={{ animationDelay: `${i * 70}ms` }}>
                            <div className="atl-metric-head">
                                <div className="atl-metric-label-wrap">
                                    <Icon size={13} className="atl-metric-icon" strokeWidth={1.8} />
                                    <span className="atl-metric-label">{m.label}</span>
                                </div>
                                <button className="atl-metric-more"><MoreHorizontal size={14} /></button>
                            </div>
                            <MetricValue value={m.value} suffix={m.suffix} decimals={0} />
                            <div className="atl-metric-foot">
                                <span className={`atl-metric-change ${m.up ? 'atl-up' : 'atl-down'}`}>
                                    {m.up ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                                    {m.change}
                                </span>
                                <Sparkline data={m.sparkline} up={m.up} />
                            </div>
                        </div>
                    );
                })}
            </section>

            {/* Bento Grid */}
            <section className="atl-bento">
                <article className="atl-card atl-bento-activity">
                    <div className="atl-card-head">
                        <div>
                            <h2 className="atl-card-title">Recent Activity</h2>
                            <p className="atl-card-sub">
                                {historyLoading ? 'Loading…' : historyError ? `Error: ${historyError}` : `Last ${history.length} optimizations`}
                            </p>
                        </div>
                        <div className="atl-card-actions">
                            <button className="atl-btn-ghost-xs" onClick={() => setRefreshTick(t => t + 1)}>
                                <RefreshCw size={12} /> Refresh
                            </button>
                            <button className="atl-btn-ghost-xs" onClick={() => navigate('/history')}>
                                <ChevronRight size={12} /> View all
                            </button>
                        </div>
                    </div>

                    <div className="atl-tabs">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                className={`atl-tab ${activeTab === tab.id ? 'atl-tab-active' : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                {tab.label}
                                <span className="atl-tab-count">{tab.count}</span>
                            </button>
                        ))}
                    </div>

                    <div className="atl-list">
                        {historyLoading && (
                            <div className="atl-list-empty">
                                <Loader2 size={22} className="atl-spin" />
                                <p>Loading history…</p>
                            </div>
                        )}
                        {!historyLoading && filteredItems.slice(0, 8).map((item, i) => {
                            const title = item.final?.new_title || item.prev_title || `Optimization ${item.entry_id?.slice(0, 8) || ''}`;
                            const status = item.final ? 'complete' : 'queued';
                            return (
                                <div
                                    key={item.entry_id || i}
                                    className="atl-list-item"
                                    style={{ animationDelay: `${i * 40}ms` }}
                                    onClick={() => navigate('/history')}
                                >
                                    <div className="atl-list-left">
                                        <div className={`atl-status-dot atl-${status}`} />
                                        <div className="atl-list-text">
                                            <span className="atl-list-title">{title}</span>
                                            <span className="atl-list-meta">
                                                <span className="atl-list-author">{item.mode === 'batch' ? `Batch · row ${item.row_id ?? '—'}` : 'Single'}</span>
                                                <span className="atl-list-dot">·</span>
                                                <Clock size={11} />
                                                {timeAgo(item.created_at)}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="atl-list-right">
                                        <span className={`atl-status-pill atl-${status}`}>
                                            {statusLabel[status]}
                                        </span>
                                        <button className="atl-list-go"><ChevronRight size={14} /></button>
                                    </div>
                                </div>
                            );
                        })}
                        {!historyLoading && filteredItems.length === 0 && (
                            <div className="atl-list-empty">
                                <Inbox size={28} strokeWidth={1.4} />
                                <p>{historyError ? 'Could not load history' : 'No optimizations yet — run your first one'}</p>
                                {!historyError && (
                                    <button className="atl-btn-primary-sm" onClick={() => navigate('/optimize')} style={{ marginTop: 8 }}>
                                        <Sparkles size={13} /> Get started
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                </article>

                <article className="atl-card atl-bento-chart">
                    <div className="atl-card-head">
                        <div>
                            <h2 className="atl-card-title">Last 7 Days</h2>
                            <p className="atl-card-sub">Daily optimization volume</p>
                        </div>
                        <span className="atl-chart-total">
                            {chartTotal} runs <ArrowUpRight size={11} />
                        </span>
                    </div>
                    <div className="atl-chart">
                        {chartData.map((d, i) => (
                            <div key={i} className="atl-chart-col">
                                <div className="atl-chart-bar-wrap">
                                    <div
                                        className="atl-chart-bar"
                                        style={{ height: `${(d.value / chartMax) * 100}%`, animationDelay: `${i * 70}ms` }}
                                        title={`${d.value} runs`}
                                    />
                                </div>
                                <span className="atl-chart-label">{d.day}</span>
                            </div>
                        ))}
                    </div>
                    <div className="atl-chart-stats">
                        <div>
                            <div className="atl-chart-stat-label">Average / day</div>
                            <div className="atl-chart-stat-value">{chartAvg}</div>
                        </div>
                        <div className="atl-chart-divider" />
                        <div>
                            <div className="atl-chart-stat-label">Peak day</div>
                            <div className="atl-chart-stat-value">{chartPeak}</div>
                        </div>
                    </div>
                </article>

                <article className="atl-card atl-bento-projects">
                    <div className="atl-card-head">
                        <div>
                            <h2 className="atl-card-title">Plan Usage</h2>
                            <p className="atl-card-sub">Quota across services</p>
                        </div>
                        <button className="atl-add-btn" title="Manage billing" onClick={() => navigate('/billing')}>
                            <Plus size={14} />
                        </button>
                    </div>
                    <div className="atl-projects">
                        {projects.map((p, i) => (
                            <div key={i} className="atl-project" onClick={() => navigate('/billing')}>
                                <div className="atl-project-row">
                                    <div className="atl-project-color" style={{ background: p.color }} />
                                    <span className="atl-project-name">{p.name}</span>
                                    <span className="atl-project-pct">{p.progress}%</span>
                                </div>
                                <div className="atl-progress">
                                    <div
                                        className="atl-progress-fill"
                                        style={{ width: `${p.progress}%`, background: p.color, animationDelay: `${i * 80}ms` }}
                                    />
                                </div>
                                <div className="atl-project-meta">
                                    <span>{p.tasks} used</span>
                                    <span>{p.meta}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </article>

                <article className="atl-card atl-bento-cta">
                    <div className="atl-cta-art" aria-hidden="true">
                        <svg viewBox="0 0 200 200">
                            <circle cx="100" cy="100" r="60" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.15" />
                            <circle cx="100" cy="100" r="40" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.25" />
                            <circle cx="100" cy="100" r="20" fill="currentColor" opacity="0.08" />
                        </svg>
                    </div>
                    <div className="atl-cta-content">
                        <h3 className="atl-cta-title">Need more capacity?</h3>
                        <p className="atl-cta-desc">
                            Upgrade your plan for higher quotas on optimization, batch jobs, and analysis.
                        </p>
                        <button className="atl-cta-btn" onClick={() => navigate('/billing')}>
                            See plans <ArrowUpRight size={13} />
                        </button>
                    </div>
                </article>
            </section>

            {/* Quick Actions */}
            <section className="atl-card atl-form-card">
                <div className="atl-card-head">
                    <div>
                        <h2 className="atl-card-title">Quick Actions</h2>
                        <p className="atl-card-sub">Jump straight into a workflow</p>
                    </div>
                </div>
                <div className="atl-form">
                    <div className="atl-field">
                        <label className="atl-label">Single Optimize</label>
                        <button className="atl-btn-ghost-sm" style={{ justifyContent: 'flex-start', height: 38 }} onClick={() => navigate('/optimize')}>
                            <Zap size={14} /> Optimize one listing
                        </button>
                    </div>
                    <div className="atl-field">
                        <label className="atl-label">Batch Optimize</label>
                        <button className="atl-btn-ghost-sm" style={{ justifyContent: 'flex-start', height: 38 }} onClick={() => navigate('/batch')}>
                            <Layers size={14} /> Upload CSV / DOCX
                        </button>
                    </div>
                    <div className="atl-field">
                        <label className="atl-label">Product Analysis</label>
                        <button className="atl-btn-ghost-sm" style={{ justifyContent: 'flex-start', height: 38 }} onClick={() => navigate('/analyze')}>
                            <Activity size={14} /> Deep-analyze a URL
                        </button>
                    </div>
                    <div className="atl-field">
                        <label className="atl-label">Keyword Database</label>
                        <button className="atl-btn-ghost-sm" style={{ justifyContent: 'flex-start', height: 38 }} onClick={() => navigate('/keywords')}>
                            <Hash size={14} /> Browse extracted keywords
                        </button>
                    </div>
                    <div className="atl-form-actions">
                        <span className="atl-form-hint">
                            Press <kbd className="atl-kbd-mini">⌘K</kbd> anywhere to open the command palette
                        </span>
                        <div className="atl-form-buttons">
                            <button className="atl-btn-ghost-sm" onClick={() => navigate('/settings')}>
                                <SettingsIcon size={13} /> Settings
                            </button>
                            <button className="atl-btn-primary-sm" onClick={() => navigate('/optimize')}>
                                <Sparkles size={13} /> Start
                            </button>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
};

export default Overview;
