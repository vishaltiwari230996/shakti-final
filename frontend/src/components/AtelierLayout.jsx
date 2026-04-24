import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../pages/TestUI.css';
import {
    Search,
    Bell,
    Sun,
    Moon,
    Zap,
    ChevronRight,
    Plus,
    X,
    CornerDownLeft,
    Activity,
    Home,
    FileText,
    Settings as SettingsIcon,
    Sparkles,
    Layers,
    Hash,
    Folder,
    CreditCard,
    LifeBuoy,
    LogOut,
    History as HistoryIcon,
    PenTool,
    RefreshCw,
} from 'lucide-react';

/* ─────────────────────────────────────────────
   NAV SECTIONS — real routes
   ───────────────────────────────────────────── */
const sidebarSections = [
    {
        title: 'Workspace',
        items: [
            { id: 'overview', label: 'Overview', icon: Home, path: '/' },
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

// Flat map of path → { id, label } for breadcrumb + active state
const navIndex = sidebarSections
    .flatMap(s => s.items)
    .reduce((acc, it) => { acc[it.path] = it; return acc; }, {});

const resolveActive = (pathname) => {
    if (pathname === '/') return navIndex['/'];
    // longest-prefix match
    const keys = Object.keys(navIndex).filter(k => k !== '/').sort((a, b) => b.length - a.length);
    for (const k of keys) {
        if (pathname === k || pathname.startsWith(k + '/')) return navIndex[k];
    }
    return null;
};

/* ─────────────────────────────────────────────
   COMMAND PALETTE
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
   ATELIER LAYOUT — the main app shell
   ───────────────────────────────────────────── */
const DARK_KEY = 'atl_dark_mode';

const AtelierLayout = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user, logout } = useAuth();

    const [darkMode, setDarkMode] = useState(() => {
        try { return localStorage.getItem(DARK_KEY) === '1'; } catch { return false; }
    });
    const [cmdOpen, setCmdOpen] = useState(false);

    useEffect(() => {
        try { localStorage.setItem(DARK_KEY, darkMode ? '1' : '0'); } catch { /* ignore */ }
        if (darkMode) {
            document.documentElement.classList.add('atl-dark-root');
        } else {
            document.documentElement.classList.remove('atl-dark-root');
        }
    }, [darkMode]);

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

    const active = resolveActive(location.pathname);
    const activeId = active?.id || 'overview';
    const activeLabel = active?.label || 'Workspace';

    /* ── User display ── */
    const userName = user?.name || 'there';
    const userEmail = user?.email || '';
    const initials = userName.split(' ').map(n => n[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'U';

    /* ── Commands ── */
    const commands = useMemo(() => [
        { id: 'nav-overview', label: 'Go to Overview', icon: Home, group: 'Navigate', action: () => navigate('/') },
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
        { id: 'act-refresh', label: 'Refresh Page', icon: RefreshCw, group: 'Actions', action: () => window.location.reload() },
        { id: 'dev-schema', label: 'Open Schema Designer (Dev)', icon: PenTool, group: 'Developer', action: () => navigate('/dev/schema') },
        { id: 'pref-theme', label: darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode', icon: darkMode ? Sun : Moon, group: 'Preferences', action: () => setDarkMode(d => !d) },
        { id: 'pref-logout', label: 'Sign Out', icon: LogOut, group: 'Account', action: () => logout() },
    ], [navigate, logout, darkMode]);

    return (
        <div className={`atl-root ${darkMode ? 'atl-dark' : ''}`}>
            <CommandPalette open={cmdOpen} onClose={() => setCmdOpen(false)} commands={commands} />

            <div className="atl-shell">
                {/* ── SIDEBAR ── */}
                <aside className="atl-sidebar">
                    <div className="atl-sidebar-top">
                        <div className="atl-sidebar-brand" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
                            <div className="atl-brand-mark">
                                <PenTool size={14} strokeWidth={2.2} />
                            </div>
                            <div className="atl-brand-text">
                                <div className="atl-brand-name">Shakti</div>
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
                                    const isActive = activeId === item.id;
                                    return (
                                        <button
                                            key={item.id}
                                            className={`atl-nav-item ${isActive ? 'atl-nav-item-active' : ''}`}
                                            onClick={() => navigate(item.path)}
                                        >
                                            <Icon size={15} strokeWidth={1.8} />
                                            <span>{item.label}</span>
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
                            <span>{activeLabel}</span>
                        </div>
                        <div className="atl-topbar-actions">
                            <button className="atl-icon-btn" onClick={() => setDarkMode(!darkMode)} title="Toggle theme">
                                {darkMode ? <Sun size={16} /> : <Moon size={16} />}
                            </button>
                            <button className="atl-icon-btn atl-bell" title="Notifications">
                                <Bell size={16} />
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
                        {children}
                    </main>
                </div>
            </div>
        </div>
    );
};

export default AtelierLayout;
