import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    Zap,
    Layers,
    HelpCircle,
    Settings as SettingsIcon,
    Menu,
    X,
    Sparkles,
    Clock,
    FileText,
    Hash,
    Folder,
    CreditCard,
    Palette,
} from 'lucide-react';
import UserProfile from './UserProfile';

const Layout = ({ children }) => {
    const location = useLocation();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const navItems = [
        { path: '/optimize', label: 'Optimize', icon: Zap },
        { path: '/batch', label: 'Batch', icon: Layers },
        { path: '/analyze', label: 'Product Analysis', icon: Sparkles },
        { path: '/history', label: 'History', icon: Clock },
        { path: '/analysis-history', label: 'Analysis History', icon: FileText, badge: 'Soon' },
        { path: '/keywords', label: 'Keywords', icon: Hash, badge: 'Soon' },
        { path: '/sku-groups', label: 'SKU Groups', icon: Folder, badge: 'Soon' },
        { path: '/billing', label: 'Billing', icon: CreditCard },
        { path: '/support', label: 'Support', icon: HelpCircle },
        { path: '/settings', label: 'Settings', icon: SettingsIcon },
        { path: '/test-ui', label: 'Test UI ✦', icon: Palette },
    ];

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    return (
        <div className="min-h-screen bg-[var(--bg-app)] flex flex-col">
            {/* Header */}
            <header className="gradient-blue shadow-md sticky top-0 z-50">
                <div className="flex items-center justify-between px-4 md:px-6 h-16">
                    {/* Mobile Menu Button */}
                    <button
                        onClick={toggleSidebar}
                        className="md:hidden p-2 rounded-lg text-white hover:bg-white/10 transition-colors"
                        aria-label="Toggle menu"
                    >
                        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>

                    {/* Brand */}
                    <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-white/90 flex items-center justify-center shadow-lg">
                            <span className="text-lg font-bold text-gradient-blue">S</span>
                        </div>
                        <div className="hidden sm:flex flex-col">
                            <span className="text-white font-semibold text-lg leading-tight">
                                Shakti 1.2
                            </span>
                            <span className="text-white/80 text-xs leading-tight">
                                SEO Optimizer
                            </span>
                        </div>
                    </div>

                    {/* Right Side - User Profile */}
                    <div className="flex items-center gap-4">
                        <UserProfile />
                    </div>
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar - Responsive */}
                <aside
                    className={`
                        fixed md:static inset-y-0 left-0 z-40 w-64 
                        bg-[var(--bg-sidebar)] border-r border-[var(--border-subtle)]
                        transform transition-transform duration-300 ease-in-out
                        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
                        mt-16 md:mt-0
                    `}
                >
                    <nav className="flex flex-col h-full">
                        <div className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                const isActive = location.pathname === item.path;

                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        onClick={() => setSidebarOpen(false)}
                                        className={`nav-item ${isActive ? 'active' : ''}`}
                                    >
                                        <Icon size={20} className="shrink-0" />
                                        <span className="font-medium flex-1">{item.label}</span>
                                        {item.badge && (
                                            <span className="px-2 py-0.5 text-[10px] font-semibold bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-full">
                                                {item.badge}
                                            </span>
                                        )}
                                    </Link>
                                );
                            })}
                        </div>

                        {/* Sidebar Footer */}
                        <div className="px-4 py-4 border-t border-[var(--border-subtle)]">
                            <div className="p-3 rounded-lg bg-gradient-blue-light border border-[var(--border-subtle)]">
                                <div className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                                    💡 Pro Tip
                                </div>
                                <div className="text-xs text-[var(--text-secondary)]">
                                    Check your usage limits in the user dropdown to track your 72-hour quota.
                                </div>
                            </div>
                        </div>
                    </nav>
                </aside>

                {/* Overlay for mobile */}
                {sidebarOpen && (
                    <div
                        className="fixed inset-0 bg-black/50 z-30 md:hidden mt-16"
                        onClick={() => setSidebarOpen(false)}
                    />
                )}

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
                        {/* Page Header */}
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h1 className="text-2xl md:text-3xl font-semibold text-[var(--text-primary)]">
                                    Welcome!
                                </h1>
                                <p className="text-sm text-[var(--text-secondary)] mt-1">
                                    Optimize your content with AI-powered SEO tools
                                </p>
                            </div>
                            <span className="badge badge-blue">
                                v1.2
                            </span>
                        </div>

                        {/* Content */}
                        <div className="animate-fade-in">
                            {children}
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Layout;