import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../utils/apiConfig';
import './TestUI.css';
import {
    ArrowLeft,
    Search,
    Bell,
    Sun,
    Moon,
    BarChart3,
    TrendingUp,
    Zap,
    ChevronRight,
    Plus,
    MoreHorizontal,
    ArrowUpRight,
    ArrowDownRight,
    Check,
    Clock,
    Filter,
    Download,
    Layers,
    Activity,
    Home,
    FileText,
    Settings as SettingsIcon,
    Sparkles,
    CornerDownLeft,
    Inbox,
    Folder,
    Hash,
    LifeBuoy,
    LogOut,
    X,
    Circle,
    PenTool,
    MessageSquare,
    History as HistoryIcon,
    CreditCard,
    Database,
    Target,
    Loader2,
    RefreshCw,
} from 'lucide-react';

/* ─────────────────────────────────────────────
   NAV — wired to real backend routes
   ───────────────────────────────────────────── */
const sidebarSections = [
    {
        title: 'Workspace',
        items: [
            { id: 'overview', label: 'Overview', icon: Home, path: '/test-ui' },
            { id: 'history', label: 'History', icon: HistoryIcon, path: '/history' },
            { id: 'analysis-history', label: 'Analysis Log', icon: FileText, path: '/analysis-history' },
        ],
    },
    {
        title: 'Optimization',
        items: [
            { id: 'optimize', label: 'Single Optimize', icon: Zap, path: '/optimize' },
            { id: 'batch', label: 'Batch Optimize', icon: Layers, path: '/batch' },
            { id: 'analyze', label: 'Product Analysis', icon: Activity, path: '/analyze' },
        ],
    },
    {
        title: 'Data',
        items: [
            { id: 'keywords', label: 'Keywords', icon: Hash, path: '/keywords' },
            { id: 'sku-groups', label: 'SKU Groups', icon: Folder, path: '/sku-groups' },
        ],
    },
    {
        title: 'Account',
        items: [
            { id: 'billing', label: 'Billing', icon: CreditCard, path: '/billing' },
            { id: 'settings', label: 'Settings', icon: SettingsIcon, path: '/settings' },
        ],
    },
];

const statusLabel = { complete: 'Complete', running: 'Running', queued: 'Queued', single: 'Single', batch: 'Batch' };

/* ─────────────────────────────────────────────
   ANIMATED NUMBER HOOK
   ───────────────────────────────────────────── */
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

/* ─────────────────────────────────────────────
   SPARKLINE
   ───────────────────────────────────────────── */
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

/* ─────────────────────────────────────────────
   COMMAND PALETTE — wired to real navigation
   ───────────────────────────────────────────── */
const CommandPalette = ({ open, onClose, commands }) => {
    const [query, setQuery] = useState('');
    const [activeIdx, setActiveIdx] = useState(0);
    const inputRef = useRef(null);

    useEffect(() => {
        if (open) {
            setQuery('');
            setActiveIdx(0);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    }, [open]);

    const filtered = useMemo(() => {
        const q = query.toLowerCase().trim();
        return q ? commands.filter(c => c.label.toLowerCase().includes(q)) : commands;
    }, [query, commands]);

    useEffect(() => {
        const handler = (e) => {
            if (!open) return;
            if (e.key === 'Escape') onClose();
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setActiveIdx(i => Math.min(i + 1, filtered.length - 1));
            }
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                setActiveIdx(i => Math.max(i - 1, 0));
            }
            if (e.key === 'Enter') {
                e.preventDefault();
                const cmd = filtered[activeIdx];
                if (cmd?.action) cmd.action();
                onClose();
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [open, filtered, activeIdx, onClose]);

    if (!open) return null;

    const grouped = filtered.reduce((acc, item) => {
        (acc[item.group] = acc[item.group] || []).push(item);
        return acc;
    }, {});

    let runningIdx = -1;

    return (
        <div className="atl-cmd-overlay" onClick={onClose}>
            <div className="atl-cmd-panel" onClick={(e) => e.stopPropagation()}>
                <div className="atl-cmd-input-row">
                    <Search size={16} className="atl-cmd-icon" />
                    <input
                        ref={inputRef}
                        value={query}
                        onChange={e => { setQuery(e.target.value); setActiveIdx(0); }}
                        placeholder="Type a command or search..."
                        className="atl-cmd-input"
                    />
                    <button className="atl-cmd-close" onClick={onClose}>
                        <X size={14} />
                    </button>
                </div>
                <div className="atl-cmd-list">
                    {Object.entries(grouped).map(([group, items]) => (
                        <div key={group} className="atl-cmd-group">
                            <div className="atl-cmd-group-label">{group}</div>
                            {items.map(item => {
                                runningIdx++;
                                const isActive = runningIdx === activeIdx;
                                const Icon = item.icon;
                                return (
                                    <button
                                        key={item.id}
                                        className={`atl-cmd-item ${isActive ? 'atl-cmd-item-active' : ''}`}
                                        onMouseEnter={() => setActiveIdx(runningIdx)}
                                        onClick={() => { item.action && item.action(); onClose(); }}
                                    >
                                        <Icon size={15} />
                                        <span>{item.label}</span>
                                        {isActive && <CornerDownLeft size={12} className="atl-cmd-enter" />}
                                    </button>
                                );
                            })}
                        </div>
                    ))}
                    {filtered.length === 0 && (
                        <div className="atl-cmd-empty">No results for "{query}"</div>
                    )}
                </div>
                <div className="atl-cmd-footer">
                    <span><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
                    <span><kbd>↵</kbd> Select</span>
                    <span><kbd>Esc</kbd> Close</span>
                </div>
            </div>
        </div>
    );
};

/* ─────────────────────────────────────────────
   MAIN COMPONENT
   ───────────────────────────────────────────── */
const TestUI = () => {
    const navigate = useNavigate();
    const { user, token, userStats, fetchUserStats, logout } = useAuth();

    const [darkMode, setDarkMode] = useState(false);
    const [activeNav, setActiveNav] = useState('overview');
    const [activeTab, setActiveTab] = useState('all');
    const [cmdOpen, setCmdOpen] = useState(false);
    const [history, setHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [historyError, setHistoryError] = useState(null);
    const [refreshTick, setRefreshTick] = useState(0);

    /* ── Fetch backend history ── */
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

    /* ── ⌘K listener ── */
    useEffect(() => {
        const handler = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                setCmdOpen(o => !o);
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, []);

    /* ── Derived: real metrics from userStats + history ── */
    const optimizeUsage = userStats?.usage?.optimize || { used: 0, limit: 100, remaining: 100 };
    const analysisUsage = userStats?.usage?.product_analysis || userStats?.usage?.analysis || { used: 0, limit: 50, remaining: 50 };
    const batchUsage = userStats?.usage?.batch || { used: 0, limit: 20, remaining: 20 };

    const totalRuns = history.length;
    const singleRuns = history.filter(h => h.mode === 'single').length;
    const batchRuns = history.filter(h => h.mode === 'batch').length;

    // Build a 7-day activity chart from history.created_at
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

    // Real metric cards
    const metrics = useMemo(() => {
        const usagePct = (used, limit) => {
            if (!limit) return 0;
            return Math.min(100, Math.round((used / limit) * 100));
        };
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
                label: 'Total Optimizations',
                value: totalRuns,
                prefix: '',
                suffix: '',
                change: totalRuns > 0 ? `${totalRuns} runs` : 'No data',
                up: true,
                icon: BarChart3,
                sparkline: sparkFromHistory(null),
            },
            {
                label: 'Single Optimize',
                value: optimizeUsage.used || singleRuns,
                prefix: '',
                suffix: ` / ${optimizeUsage.limit || '∞'}`,
                change: `${usagePct(optimizeUsage.used, optimizeUsage.limit)}% used`,
                up: optimizeUsage.remaining > 5,
                icon: Zap,
                sparkline: sparkFromHistory('single'),
            },
            {
                label: 'Batch Runs',
                value: batchUsage.used || batchRuns,
                prefix: '',
                suffix: ` / ${batchUsage.limit || '∞'}`,
                change: `${usagePct(batchUsage.used, batchUsage.limit)}% used`,
                up: batchUsage.remaining > 2,
                icon: Layers,
                sparkline: sparkFromHistory('batch'),
            },
            {
                label: 'Product Analyses',
                value: analysisUsage.used || 0,
                prefix: '',
                suffix: ` / ${analysisUsage.limit || '∞'}`,
                change: `${usagePct(analysisUsage.used, analysisUsage.limit)}% used`,
                up: (analysisUsage.remaining ?? 1) > 2,
                icon: Target,
                sparkline: [0, 0, 0, 0, 0, 0, 0, 0, 0, analysisUsage.used || 0],
            },
        ];
    }, [totalRuns, singleRuns, batchRuns, optimizeUsage, batchUsage, analysisUsage, history]);

    // Tabs based on real history modes
    const tabs = [
        { id: 'all', label: 'All', count: history.length },
        { id: 'single', label: 'Single', count: history.filter(h => h.mode === 'single').length },
        { id: 'batch', label: 'Batch', count: history.filter(h => h.mode === 'batch').length },
    ];
    const filteredItems = activeTab === 'all'
        ? history
        : history.filter(h => h.mode === activeTab);

    // Project-style breakdown by mode usage
    const projects = useMemo(() => {
        const items = [
            {
                name: 'Single Optimization',
                progress: optimizeUsage.limit ? Math.min(100, Math.round((optimizeUsage.used / optimizeUsage.limit) * 100)) : 0,
                tasks: optimizeUsage.used || 0,
                color: '#1f1f1f',
                meta: `${optimizeUsage.remaining ?? 0} remaining`,
            },
            {
                name: 'Batch Processing',
                progress: batchUsage.limit ? Math.min(100, Math.round((batchUsage.used / batchUsage.limit) * 100)) : 0,
                tasks: batchUsage.used || 0,
                color: '#3a3a3a',
                meta: `${batchUsage.remaining ?? 0} remaining`,
            },
            {
                name: 'Product Analysis',
                progress: analysisUsage.limit ? Math.min(100, Math.round((analysisUsage.used / analysisUsage.limit) * 100)) : 0,
                tasks: analysisUsage.used || 0,
                color: '#5a5a5a',
                meta: `${analysisUsage.remaining ?? 0} remaining`,
            },
        ];
        return items;
    }, [optimizeUsage, batchUsage, analysisUsage]);

    // Command palette commands wired to real actions
    const commands = useMemo(() => [
        { id: 'nav-optimize', label: 'Go to Single Optimize', icon: Zap, group: 'Navigate', action: () => navigate('/optimize') },
        { id: 'nav-batch', label: 'Go to Batch Optimize', icon: Layers, group: 'Navigate', action: () => navigate('/batch') },
        { id: 'nav-analyze', label: 'Go to Product Analysis', icon: Activity, group: 'Navigate', action: () => navigate('/analyze') },
        { id: 'nav-history', label: 'Open History', icon: HistoryIcon, group: 'Navigate', action: () => navigate('/history') },
        { id: 'nav-analysis-history', label: 'Open Analysis Log', icon: FileText, group: 'Navigate', action: () => navigate('/analysis-history') },
        { id: 'nav-keywords', label: 'Open Keyword Database', icon: Hash, group: 'Navigate', action: () => navigate('/keywords') },
        { id: 'nav-sku', label: 'Open SKU Groups', icon: Folder, group: 'Navigate', action: () => navigate('/sku-groups') },
        { id: 'nav-billing', label: 'Open Billing', icon: CreditCard, group: 'Navigate', action: () => navigate('/billing') },
        { id: 'nav-settings', label: 'Open Settings', icon: SettingsIcon, group: 'Navigate', action: () => navigate('/settings') },
        { id: 'nav-support', label: 'Help & Support', icon: LifeBuoy, group: 'Navigate', action: () => navigate('/support') },
        { id: 'act-new-opt', label: 'New Single Optimization', icon: Plus, group: 'Actions', action: () => navigate('/optimize') },
        { id: 'act-new-batch', label: 'New Batch Job', icon: Plus, group: 'Actions', action: () => navigate('/batch') },
        { id: 'act-new-analysis', label: 'New Product Analysis', icon: Plus, group: 'Actions', action: () => navigate('/analyze') },
        { id: 'act-refresh', label: 'Refresh Data', icon: RefreshCw, group: 'Actions', action: () => setRefreshTick(t => t + 1) },
        { id: 'pref-theme', label: darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode', icon: darkMode ? Sun : Moon, group: 'Preferences', action: () => setDarkMode(d => !d) },
        { id: 'pref-logout', label: 'Sign Out', icon: LogOut, group: 'Account', action: () => logout() },
    ], [navigate, logout, darkMode]);

    /* ── User-derived display values ── */
    const userName = user?.name || 'there';
    const firstName = userName.split(' ')[0];
    const userEmail = user?.email || '';
    const initials = userName.split(' ').map(n => n[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'U';
    const greeting = (() => {
        const h = new Date().getHours();
        if (h < 12) return 'Good morning';
        if (h < 17) return 'Good afternoon';
        return 'Good evening';
    })();

    const handleNavClick = (item) => {
        setActiveNav(item.id);
        if (item.path && item.id !== 'overview') navigate(item.path);
    };

    return (
        <div className={`atl-root ${darkMode ? 'atl-dark' : ''}`}>
            <CommandPalette open={cmdOpen} onClose={() => setCmdOpen(false)} commands={commands} />

            <div className="atl-shell">
                {/* ── SIDEBAR ── */}
                <aside className="atl-sidebar">
                    <div className="atl-sidebar-top">
                        <Link to="/optimize" className="atl-sidebar-back" title="Back to app">
                            <ArrowLeft size={16} />
                        </Link>
                        <div className="atl-sidebar-brand">
                            <div className="atl-brand-mark">
                                <PenTool size={14} strokeWidth={2.2} />
                            </div>
                            <div className="atl-brand-text">
                                <div className="atl-brand-name">Atelier</div>
                                <div className="atl-brand-org">{user?.email ? user.email.split('@')[1] : 'Workspace'}</div>
                            </div>
                        </div>
                    </div>

                    <button className="atl-sidebar-search" onClick={() => setCmdOpen(true)}>
                        <Search size={14} />
                        <span>Search</span>
                        <kbd className="atl-kbd-mini">⌘K</kbd>
                    </button>

                    <nav className="atl-nav">
                        {sidebarSections.map((section) => (
                            <div key={section.title} className="atl-nav-section">
                                <div className="atl-nav-section-title">{section.title}</div>
                                {section.items.map(item => {
                                    const Icon = item.icon;
                                    const isActive = activeNav === item.id;
                                    return (
                                        <button
                                            key={item.id}
                                            className={`atl-nav-item ${isActive ? 'atl-nav-item-active' : ''}`}
                                            onClick={() => handleNavClick(item)}
                                        >
                                            <Icon size={15} strokeWidth={1.8} />
                                            <span>{item.label}</span>
                                            {item.badge && <span className="atl-nav-badge">{item.badge}</span>}
                                        </button>
                                    );
                                })}
                            </div>
                        ))}
                    </nav>

                    <div className="atl-sidebar-bottom">
                        <button className="atl-nav-item" onClick={() => navigate('/support')}>
                            <LifeBuoy size={15} strokeWidth={1.8} />
                            <span>Support</span>
                        </button>
                        <div className="atl-user-card">
                            {user?.picture ? (
                                <img src={user.picture} alt="" className="atl-user-avatar" style={{ objectFit: 'cover' }} referrerPolicy="no-referrer" />
                            ) : (
                                <div className="atl-user-avatar">{initials}</div>
                            )}
                            <div className="atl-user-info">
                                <div className="atl-user-name">{userName}</div>
                                <div className="atl-user-email">{userEmail}</div>
                            </div>
                            <button className="atl-user-action" onClick={logout} title="Sign out">
                                <LogOut size={13} />
                            </button>
                        </div>
                    </div>
                </aside>

                {/* ── MAIN ── */}
                <div className="atl-main-wrap">
                    <header className="atl-topbar">
                        <div className="atl-breadcrumb">
                            <span className="atl-crumb-muted">Workspace</span>
                            <ChevronRight size={13} className="atl-crumb-sep" />
                            <span>Overview</span>
                        </div>
                        <div className="atl-topbar-actions">
                            <button className="atl-icon-btn" onClick={() => setRefreshTick(t => t + 1)} title="Refresh">
                                <RefreshCw size={15} />
                            </button>
                            <button className="atl-icon-btn" onClick={() => setDarkMode(!darkMode)} title="Theme">
                                {darkMode ? <Sun size={16} /> : <Moon size={16} />}
                            </button>
                            <button className="atl-icon-btn atl-bell" title="Notifications">
                                <Bell size={16} />
                                {historyError && <span className="atl-notif-pip" />}
                            </button>
                            <div className="atl-topbar-divider" />
                            <button className="atl-btn-ghost-sm" onClick={() => navigate('/analyze')}>
                                <Activity size={14} />
                                Analyze
                            </button>
                            <button className="atl-btn-primary-sm" onClick={() => navigate('/optimize')}>
                                <Sparkles size={14} />
                                New Optimization
                            </button>
                        </div>
                    </header>

                    <main className="atl-main">
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
                                const decimals = 0;
                                return (
                                    <div key={i} className="atl-metric" style={{ animationDelay: `${i * 70}ms` }}>
                                        <div className="atl-metric-head">
                                            <div className="atl-metric-label-wrap">
                                                <Icon size={13} className="atl-metric-icon" strokeWidth={1.8} />
                                                <span className="atl-metric-label">{m.label}</span>
                                            </div>
                                            <button className="atl-metric-more">
                                                <MoreHorizontal size={14} />
                                            </button>
                                        </div>
                                        <MetricValue value={m.value} prefix={m.prefix} suffix={m.suffix} decimals={decimals} />
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
                            {/* Activity (real history) */}
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
                                                    <button className="atl-list-go">
                                                        <ChevronRight size={14} />
                                                    </button>
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

                            {/* 7-day chart from real data */}
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
                                                    style={{
                                                        height: `${(d.value / chartMax) * 100}%`,
                                                        animationDelay: `${i * 70}ms`,
                                                    }}
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

                            {/* Quota / "projects" — real usage breakdown */}
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
                                                    style={{
                                                        width: `${p.progress}%`,
                                                        background: p.color,
                                                        animationDelay: `${i * 80}ms`,
                                                    }}
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

                            {/* CTA */}
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
                                    <button
                                        className="atl-btn-ghost-sm"
                                        style={{ justifyContent: 'flex-start', height: 38 }}
                                        onClick={() => navigate('/optimize')}
                                    >
                                        <Zap size={14} /> Optimize one listing
                                    </button>
                                </div>
                                <div className="atl-field">
                                    <label className="atl-label">Batch Optimize</label>
                                    <button
                                        className="atl-btn-ghost-sm"
                                        style={{ justifyContent: 'flex-start', height: 38 }}
                                        onClick={() => navigate('/batch')}
                                    >
                                        <Layers size={14} /> Upload CSV / DOCX
                                    </button>
                                </div>
                                <div className="atl-field">
                                    <label className="atl-label">Product Analysis</label>
                                    <button
                                        className="atl-btn-ghost-sm"
                                        style={{ justifyContent: 'flex-start', height: 38 }}
                                        onClick={() => navigate('/analyze')}
                                    >
                                        <Activity size={14} /> Deep-analyze a URL
                                    </button>
                                </div>
                                <div className="atl-field">
                                    <label className="atl-label">Keyword Database</label>
                                    <button
                                        className="atl-btn-ghost-sm"
                                        style={{ justifyContent: 'flex-start', height: 38 }}
                                        onClick={() => navigate('/keywords')}
                                    >
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

                        <footer className="atl-footer">
                            <div className="atl-footer-line" />
                            <p>Less, but better.</p>
                            <span>Atelier · {user?.email || 'Workspace'}</span>
                        </footer>
                    </main>
                </div>
            </div>
        </div>
    );
};

export default TestUI;
