import React, { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react';

const THEME_STORAGE_KEY = 'shakti_theme';

const THEME_LIBRARY = {
    aurora: {
        label: 'Aurora Light',
        description: 'Airy whites with electric blues for crisp clarity.',
        preview: ['#f8fafc', '#2563eb', '#dc2626'],
        tokens: {
            '--bg-app': '#f8fafc',
            '--bg-panel': '#ffffff',
            '--bg-element': '#f1f5f9',
            '--bg-sidebar': '#ffffff',
            '--bg-header': '#2563eb',
            '--text-primary': '#1e293b',
            '--text-secondary': '#64748b',
            '--text-tertiary': '#94a3b8',
            '--text-on-blue': '#ffffff',
            '--accent': '#2563eb',
            '--accent-hover': '#1e40af',
            '--accent-light': '#3b82f6',
            '--accent-bg': '#eff6ff',
            '--border-subtle': '#e2e8f0',
            '--border-medium': '#cbd5e1',
            '--border-focus': '#2563eb',
            '--success': '#10b981',
            '--success-bg': '#d1fae5',
            '--error': '#dc2626',
            '--error-bg': '#fee2e2',
            '--warning': '#f59e0b',
            '--warning-bg': '#fef3c7',
            '--red-accent': '#dc2626',
            '--red-accent-light': '#fca5a5',
            '--shadow-sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
            '--shadow-md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
            '--shadow-lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
            '--shadow-xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)'
        }
    },
    midnight: {
        label: 'Midnight Neon',
        description: 'Deep charcoal canvas with neon cyan accents.',
        preview: ['#050816', '#06b6d4', '#ef4444'],
        tokens: {
            '--bg-app': '#050816',
            '--bg-panel': '#0f172a',
            '--bg-element': '#111b2f',
            '--bg-sidebar': '#0b1120',
            '--bg-header': '#0ea5e9',
            '--text-primary': '#e2e8f0',
            '--text-secondary': '#94a3b8',
            '--text-tertiary': '#64748b',
            '--text-on-blue': '#050816',
            '--accent': '#06b6d4',
            '--accent-hover': '#0891b2',
            '--accent-light': '#22d3ee',
            '--accent-bg': 'rgba(34, 211, 238, 0.12)',
            '--border-subtle': 'rgba(148, 163, 184, 0.24)',
            '--border-medium': 'rgba(148, 163, 184, 0.45)',
            '--border-focus': '#06b6d4',
            '--success': '#34d399',
            '--success-bg': 'rgba(52, 211, 153, 0.12)',
            '--error': '#ef4444',
            '--error-bg': 'rgba(239, 68, 68, 0.15)',
            '--warning': '#fbbf24',
            '--warning-bg': 'rgba(251, 191, 36, 0.18)',
            '--red-accent': '#f43f5e',
            '--red-accent-light': '#fda4af',
            '--shadow-sm': '0 2px 10px rgb(2 6 23 / 0.45)',
            '--shadow-md': '0 10px 25px rgb(2 6 23 / 0.55)',
            '--shadow-lg': '0 20px 45px rgb(2 6 23 / 0.65)',
            '--shadow-xl': '0 35px 65px rgb(2 6 23 / 0.7)'
        }
    },
    ember: {
        label: 'Solar Ember',
        description: 'Golden dusk gradients with warm reds for energy.',
        preview: ['#fff7ed', '#f97316', '#dc2626'],
        tokens: {
            '--bg-app': '#fff7ed',
            '--bg-panel': '#fff1e6',
            '--bg-element': '#ffe6d5',
            '--bg-sidebar': '#fff1e6',
            '--bg-header': '#ea580c',
            '--text-primary': '#431407',
            '--text-secondary': '#9a3412',
            '--text-tertiary': '#fb923c',
            '--text-on-blue': '#fff7ed',
            '--accent': '#f97316',
            '--accent-hover': '#c2410c',
            '--accent-light': '#fdba74',
            '--accent-bg': '#fff1e6',
            '--border-subtle': '#fed7aa',
            '--border-medium': '#fdba74',
            '--border-focus': '#ea580c',
            '--success': '#22c55e',
            '--success-bg': '#dcfce7',
            '--error': '#dc2626',
            '--error-bg': '#fee2e2',
            '--warning': '#fbbf24',
            '--warning-bg': '#fef3c7',
            '--red-accent': '#dc2626',
            '--red-accent-light': '#fecaca',
            '--shadow-sm': '0 4px 8px rgb(248 113 113 / 0.15)',
            '--shadow-md': '0 12px 20px rgb(251 146 60 / 0.25)',
            '--shadow-lg': '0 20px 30px rgb(249 115 22 / 0.25)',
            '--shadow-xl': '0 30px 45px rgb(194 65 12 / 0.3)'
        }
    }
};

const ThemeContext = createContext({
    theme: 'aurora',
    setTheme: () => {},
    themeOptions: []
});

const applyThemeTokens = (themeId) => {
    if (typeof document === 'undefined') return;
    const root = document.documentElement;
    const selected = THEME_LIBRARY[themeId] || THEME_LIBRARY.aurora;

    Object.entries(selected.tokens).forEach(([variable, value]) => {
        root.style.setProperty(variable, value);
    });
    root.setAttribute('data-shakti-theme', themeId);
    document.body.style.backgroundColor = selected.tokens['--bg-app'];
};

const getInitialTheme = () => {
    if (typeof window === 'undefined') {
        return 'aurora';
    }
    return localStorage.getItem(THEME_STORAGE_KEY) || 'aurora';
};

export const ThemeProvider = ({ children }) => {
    const [theme, setThemeState] = useState(getInitialTheme);

    useEffect(() => {
        applyThemeTokens(theme);
        localStorage.setItem(THEME_STORAGE_KEY, theme);
    }, [theme]);

    useEffect(() => {
        applyThemeTokens(theme);
    }, []);

    const setTheme = useCallback((nextTheme) => {
        if (!THEME_LIBRARY[nextTheme]) return;
        setThemeState(nextTheme);
    }, []);

    const value = useMemo(() => ({
        theme,
        setTheme,
        themeOptions: Object.entries(THEME_LIBRARY).map(([id, meta]) => ({
            id,
            label: meta.label,
            description: meta.description,
            preview: meta.preview
        }))
    }), [theme]);

    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => useContext(ThemeContext);

export const themeLibrary = THEME_LIBRARY;
