import React, { useState, useEffect, useMemo } from 'react';
import {
    Save,
    Cpu,
    Layers,
    Palette,
    Trash2,
    AlertTriangle,
    Sparkles,
    Zap,
    Check,
    Info,
    ExternalLink,
    Settings as SettingsIcon,
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext.jsx';

/* ─── OpenRouter live catalog ─── */
const OPENROUTER_MODELS_ENDPOINT = 'https://openrouter.ai/api/v1/models';

const FALLBACK_MODELS = [
    { id: 'openai/gpt-5', name: 'OpenAI: GPT-5', group: 'OpenAI' },
    { id: 'openai/gpt-5-mini', name: 'OpenAI: GPT-5 Mini', group: 'OpenAI' },
    { id: 'openai/gpt-4o', name: 'OpenAI: GPT-4o', group: 'OpenAI' },
    { id: 'openai/gpt-4o-mini', name: 'OpenAI: GPT-4o Mini', group: 'OpenAI' },
    { id: 'anthropic/claude-opus-4.6', name: 'Anthropic: Claude Opus 4.6', group: 'Anthropic' },
    { id: 'anthropic/claude-sonnet-4.5', name: 'Anthropic: Claude Sonnet 4.5', group: 'Anthropic' },
    { id: 'anthropic/claude-haiku-4.5', name: 'Anthropic: Claude Haiku 4.5', group: 'Anthropic' },
    { id: 'google/gemini-2.5-pro', name: 'Google: Gemini 2.5 Pro', group: 'Google' },
    { id: 'google/gemini-2.5-flash', name: 'Google: Gemini 2.5 Flash', group: 'Google' },
    { id: 'deepseek/deepseek-r1', name: 'DeepSeek: R1', group: 'DeepSeek' },
    { id: 'deepseek/deepseek-chat', name: 'DeepSeek: V3', group: 'DeepSeek' },
    { id: 'meta-llama/llama-3.3-70b-instruct', name: 'Meta: Llama 3.3 70B', group: 'Meta' },
    { id: 'x-ai/grok-4', name: 'xAI: Grok 4', group: 'xAI' },
    { id: 'mistralai/mistral-large', name: 'Mistral Large', group: 'Mistral' },
    { id: 'qwen/qwen3-max', name: 'Qwen: Qwen3 Max', group: 'Qwen' },
];

const groupOrder = [
    'OpenAI', 'Anthropic', 'Google', 'xAI', 'Meta',
    'DeepSeek', 'Qwen', 'Mistral', 'MoonshotAI', 'MiniMax',
    'Z.ai', 'NVIDIA', 'Cohere', 'Amazon', 'Perplexity',
    'Inception', 'ByteDance', 'Tencent', 'Baidu', 'StepFun',
    'Liquid', 'Arcee', 'AI21', 'NousResearch', 'AllenAI',
    'OpenRouter', 'Other',
];

const deriveGroup = (model) => {
    const provider = (model.id || '').split('/')[0]?.toLowerCase() || '';
    if (provider.includes('openai')) return 'OpenAI';
    if (provider.includes('anthropic')) return 'Anthropic';
    if (provider.includes('google')) return 'Google';
    if (provider.includes('x-ai') || provider.includes('xai')) return 'xAI';
    if (provider.includes('meta')) return 'Meta';
    if (provider.includes('deepseek')) return 'DeepSeek';
    if (provider.includes('qwen') || provider.includes('alibaba')) return 'Qwen';
    if (provider.includes('mistral')) return 'Mistral';
    if (provider.includes('moonshot')) return 'MoonshotAI';
    if (provider.includes('minimax')) return 'MiniMax';
    if (provider.includes('z-ai') || provider.includes('zai')) return 'Z.ai';
    if (provider.includes('nvidia')) return 'NVIDIA';
    if (provider.includes('cohere')) return 'Cohere';
    if (provider.includes('amazon')) return 'Amazon';
    if (provider.includes('perplexity')) return 'Perplexity';
    if (provider.includes('inception')) return 'Inception';
    if (provider.includes('bytedance')) return 'ByteDance';
    if (provider.includes('tencent')) return 'Tencent';
    if (provider.includes('baidu')) return 'Baidu';
    if (provider.includes('stepfun')) return 'StepFun';
    if (provider.includes('liquid')) return 'Liquid';
    if (provider.includes('arcee')) return 'Arcee';
    if (provider.includes('ai21')) return 'AI21';
    if (provider.includes('nous')) return 'NousResearch';
    if (provider.includes('allen')) return 'AllenAI';
    if (provider.includes('openrouter')) return 'OpenRouter';
    return 'Other';
};

const formatPrice = (p) => {
    if (p === undefined || p === null || p === '') return '';
    const n = parseFloat(p);
    if (Number.isNaN(n) || n === 0) return 'free';
    const per1M = n * 1_000_000;
    if (per1M < 0.01) return `$${per1M.toFixed(4)}/M`;
    return `$${per1M.toFixed(2)}/M`;
};

let _catalogCache = null;
const useOpenRouterCatalog = () => {
    const [state, setState] = useState(() => _catalogCache || { loading: true, error: null, models: FALLBACK_MODELS });

    useEffect(() => {
        if (_catalogCache && !_catalogCache.loading) return;
        let cancelled = false;
        (async () => {
            try {
                const res = await fetch(OPENROUTER_MODELS_ENDPOINT);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const json = await res.json();
                const models = (json.data || []).map(m => ({
                    id: m.id,
                    name: m.name || m.id,
                    group: deriveGroup(m),
                    context: m.context_length,
                    prompt: m.pricing?.prompt,
                    completion: m.pricing?.completion,
                }));
                const next = { loading: false, error: null, models };
                _catalogCache = next;
                if (!cancelled) setState(next);
            } catch (err) {
                const next = { loading: false, error: err.message, models: FALLBACK_MODELS };
                _catalogCache = next;
                if (!cancelled) setState(next);
            }
        })();
        return () => { cancelled = true; };
    }, []);

    return state;
};

const ModelSelect = ({ name, value, onChange, includeNone = false, catalog, disabled }) => {
    const { loading, error, models } = catalog;

    const grouped = useMemo(() => {
        const map = new Map();
        for (const m of models) {
            if (!map.has(m.group)) map.set(m.group, []);
            map.get(m.group).push(m);
        }
        const ordered = [];
        for (const g of groupOrder) {
            if (map.has(g)) {
                ordered.push([g, map.get(g).sort((a, b) => a.name.localeCompare(b.name))]);
                map.delete(g);
            }
        }
        for (const [g, list] of map) {
            ordered.push([g, list.sort((a, b) => a.name.localeCompare(b.name))]);
        }
        return ordered;
    }, [models]);

    return (
        <select
            name={name}
            value={value || ''}
            onChange={onChange}
            disabled={disabled}
            className="atl-input atl-select"
        >
            {includeNone && <option value="none">— None (skip this pass) —</option>}
            {!value && <option value="" disabled>{loading ? 'Loading catalog…' : 'Select a model'}</option>}
            {error && <option disabled>⚠ Could not load live catalog — using fallback</option>}
            {grouped.map(([group, list]) => (
                <optgroup key={group} label={`${group} (${list.length})`}>
                    {list.map(m => {
                        const price = formatPrice(m.prompt);
                        const suffix = price ? ` · ${price}` : '';
                        return (
                            <option key={m.id} value={m.id}>
                                {m.name}{suffix}
                            </option>
                        );
                    })}
                </optgroup>
            ))}
        </select>
    );
};

const findModelLabel = (id, catalog) => {
    const m = catalog.models.find(m => m.id === id);
    return m ? m.name : id;
};

/* ─── Section wrapper ─── */
const Section = ({ icon: Icon, title, subtitle, children, extra }) => (
    <section className="atl-card">
        <div className="atl-section-head">
            <div className="atl-section-icon">
                <Icon size={16} strokeWidth={1.8} />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
                <h3 className="atl-section-title">{title}</h3>
                {subtitle && <p className="atl-section-sub">{subtitle}</p>}
            </div>
            {extra}
        </div>
        {children}
    </section>
);

/* ─── Main ─── */
const Settings = ({ config, setConfig }) => {
    const { theme, setTheme, themeOptions } = useTheme();
    const [showClearModal, setShowClearModal] = useState(false);
    const [clearing, setClearing] = useState(false);
    const [saved, setSaved] = useState(false);
    const catalog = useOpenRouterCatalog();

    const mode = config.mode || 'openrouter';

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        const v = type === 'number' ? parseFloat(value) : value;
        setConfig(prev => ({ ...prev, [name]: v }));
    };

    const setMode = (newMode) => {
        setConfig(prev => ({ ...prev, mode: newMode }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setSaved(true);
        setTimeout(() => setSaved(false), 2200);
    };

    const handleClearData = async () => {
        setClearing(true);
        try {
            localStorage.removeItem('shakti_optimization_history');
            localStorage.removeItem('shakti_analysis_history');
            setTimeout(() => {
                setClearing(false);
                setShowClearModal(false);
                window.location.reload();
            }, 700);
        } catch (err) {
            console.error('Error clearing data:', err);
            setClearing(false);
        }
    };

    const statusChip = catalog.loading
        ? 'Loading catalog…'
        : catalog.error
            ? `⚠ Offline · ${catalog.models.length} fallback`
            : `✓ ${catalog.models.length} models live`;

    return (
        <div className="atl-settings">
            {/* Header */}
            <Section
                icon={SettingsIcon}
                title="Engine Configuration"
                subtitle="Choose how your listings get optimized"
            />

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                {/* Mode Toggle */}
                <Section
                    icon={Cpu}
                    title="Engine Mode"
                    subtitle="Pick a single unified gateway, or bring your own per-provider keys"
                >
                    <div className="atl-mode-grid">
                        <button
                            type="button"
                            onClick={() => setMode('openrouter')}
                            className={`atl-mode-card ${mode === 'openrouter' ? 'atl-mode-card-active' : ''}`}
                        >
                            <div className="atl-mode-head">
                                <span className="atl-mode-name">
                                    <Sparkles size={15} />
                                    OpenRouter
                                </span>
                                <span className="atl-badge atl-badge-accent">Recommended</span>
                            </div>
                            <p className="atl-mode-desc">
                                One API key → 100+ models from OpenAI, Anthropic, Google, Meta, DeepSeek &amp; more.
                                Mix-and-match L1 and L2 engines freely.
                            </p>
                        </button>

                        <button
                            type="button"
                            onClick={() => setMode('classic')}
                            className={`atl-mode-card ${mode === 'classic' ? 'atl-mode-card-active' : ''}`}
                        >
                            <div className="atl-mode-head">
                                <span className="atl-mode-name">
                                    <Layers size={15} />
                                    Classic
                                </span>
                                <span className="atl-badge">Legacy</span>
                            </div>
                            <p className="atl-mode-desc">
                                Bring your own OpenAI, Gemini, or Anthropic keys directly. Classic dual-engine setup.
                            </p>
                        </button>
                    </div>
                </Section>

                {/* OpenRouter */}
                {mode === 'openrouter' && (
                    <>
                        <Section
                            icon={Sparkles}
                            title="OpenRouter Gateway"
                            subtitle={
                                <>
                                    Sign up at{' '}
                                    <a href="https://openrouter.ai/keys" target="_blank" rel="noreferrer" className="atl-link">
                                        openrouter.ai/keys <ExternalLink size={10} style={{ display: 'inline', verticalAlign: 'middle' }} />
                                    </a>
                                    {' '}to get your API key
                                </>
                            }
                            extra={<span className="atl-status-chip">{statusChip}</span>}
                        >
                            <div className="atl-field">
                                <label className="atl-label">OpenRouter API Key</label>
                                <input
                                    type="password"
                                    name="openrouter_key"
                                    value={config.openrouter_key || ''}
                                    onChange={handleChange}
                                    className="atl-input"
                                    placeholder="sk-or-v1-..."
                                    style={{ fontFamily: 'var(--font-mono, monospace)' }}
                                />
                                <div className="atl-hint-row">
                                    <Info size={11} />
                                    Your key is stored only in this browser session. We never persist it.
                                </div>
                            </div>
                        </Section>

                        <Section
                            icon={Zap}
                            title="L1 — Primary Engine"
                            subtitle="Generates the first listing draft from your prompt"
                        >
                            <div className="atl-field-grid">
                                <div className="atl-field">
                                    <label className="atl-label">Model</label>
                                    <ModelSelect name="l1_model" value={config.l1_model} onChange={handleChange} catalog={catalog} />
                                </div>
                                <div className="atl-field">
                                    <label className="atl-label">Temperature</label>
                                    <input
                                        type="number"
                                        name="l1_temperature"
                                        value={config.l1_temperature ?? 0.2}
                                        onChange={handleChange}
                                        min="0" max="2" step="0.1"
                                        className="atl-input"
                                    />
                                </div>
                            </div>
                        </Section>

                        <Section
                            icon={Layers}
                            title="L2 — Refinement Engine"
                            subtitle="Optional second pass. Try Claude for editorial polish or DeepSeek-R1 for reasoning."
                        >
                            <div className="atl-field-grid">
                                <div className="atl-field">
                                    <label className="atl-label">Model</label>
                                    <ModelSelect
                                        name="l2_model"
                                        value={config.l2_model}
                                        onChange={handleChange}
                                        includeNone
                                        catalog={catalog}
                                    />
                                </div>
                                <div className="atl-field">
                                    <label className="atl-label">Temperature</label>
                                    <input
                                        type="number"
                                        name="l2_temperature"
                                        value={config.l2_temperature ?? 0.2}
                                        onChange={handleChange}
                                        min="0" max="2" step="0.1"
                                        className="atl-input"
                                        disabled={!config.l2_model || config.l2_model === 'none'}
                                    />
                                </div>
                            </div>

                            {config.l1_model && (
                                <div className="atl-pipeline">
                                    <p className="atl-pipeline-label">Pipeline</p>
                                    <div className="atl-pipeline-row">
                                        <span className="atl-pipeline-pill">
                                            {findModelLabel(config.l1_model, catalog)}
                                        </span>
                                        <span className="atl-pipeline-arrow">→</span>
                                        {config.l2_model && config.l2_model !== 'none' ? (
                                            <span className="atl-pipeline-pill">
                                                {findModelLabel(config.l2_model, catalog)}
                                            </span>
                                        ) : (
                                            <span className="atl-pipeline-pill atl-pipeline-pill-muted">
                                                No second pass
                                            </span>
                                        )}
                                        <span className="atl-pipeline-arrow">→</span>
                                        <span className="atl-pipeline-pill atl-pipeline-pill-final">
                                            Final listing
                                        </span>
                                    </div>
                                </div>
                            )}
                        </Section>
                    </>
                )}

                {/* Classic */}
                {mode === 'classic' && (
                    <>
                        <Section
                            icon={Cpu}
                            title="Primary Engine (OpenAI)"
                            subtitle="Main model for L1 generation"
                        >
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                                <div className="atl-field">
                                    <label className="atl-label">OpenAI API Key</label>
                                    <input
                                        type="password"
                                        name="openai_key"
                                        value={config.openai_key || ''}
                                        onChange={handleChange}
                                        className="atl-input"
                                        placeholder="sk-..."
                                        style={{ fontFamily: 'var(--font-mono, monospace)' }}
                                    />
                                </div>
                                <div className="atl-field">
                                    <label className="atl-label">Model</label>
                                    <select
                                        name="openai_model"
                                        value={config.openai_model || ''}
                                        onChange={handleChange}
                                        className="atl-input atl-select"
                                    >
                                        <option value="gpt-5">GPT-5</option>
                                        <option value="gpt-5-mini">GPT-5 Mini</option>
                                        <option value="gpt-4.1">GPT-4.1</option>
                                        <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
                                        <option value="gpt-4o">GPT-4o</option>
                                        <option value="gpt-4o-mini">GPT-4o Mini</option>
                                    </select>
                                </div>
                            </div>
                        </Section>

                        <Section
                            icon={Layers}
                            title="Secondary Engine"
                            subtitle="Optional L2 refinement"
                        >
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                                <div className="atl-field">
                                    <label className="atl-label">Provider</label>
                                    <select
                                        name="second_engine"
                                        value={config.second_engine || 'None'}
                                        onChange={handleChange}
                                        className="atl-input atl-select"
                                    >
                                        <option value="None">None</option>
                                        <option value="OpenAI (second pass)">OpenAI (second pass)</option>
                                        <option value="Gemini (Google)">Gemini (Google)</option>
                                        <option value="Claude (Anthropic)">Claude (Anthropic)</option>
                                    </select>
                                </div>

                                {config.second_engine === 'OpenAI (second pass)' && (
                                    <div className="atl-nested">
                                        <div className="atl-field">
                                            <label className="atl-label">OpenAI API Key (Second Pass)</label>
                                            <input
                                                type="password"
                                                name="openai2_key"
                                                value={config.openai2_key || ''}
                                                onChange={handleChange}
                                                className="atl-input"
                                                placeholder="Leave empty to use primary key"
                                                style={{ fontFamily: 'var(--font-mono, monospace)' }}
                                            />
                                        </div>
                                        <div className="atl-field">
                                            <label className="atl-label">Model</label>
                                            <select name="openai2_model" value={config.openai2_model || ''} onChange={handleChange} className="atl-input atl-select">
                                                <option value="gpt-5">GPT-5</option>
                                                <option value="gpt-5-mini">GPT-5 Mini</option>
                                                <option value="gpt-4.1">GPT-4.1</option>
                                                <option value="gpt-4o">GPT-4o</option>
                                            </select>
                                        </div>
                                    </div>
                                )}

                                {config.second_engine === 'Gemini (Google)' && (
                                    <div className="atl-nested">
                                        <div className="atl-field">
                                            <label className="atl-label">Gemini API Key</label>
                                            <input
                                                type="password"
                                                name="gemini_key"
                                                value={config.gemini_key || ''}
                                                onChange={handleChange}
                                                className="atl-input"
                                                style={{ fontFamily: 'var(--font-mono, monospace)' }}
                                            />
                                        </div>
                                        <div className="atl-field">
                                            <label className="atl-label">Model</label>
                                            <select name="gemini_model" value={config.gemini_model || ''} onChange={handleChange} className="atl-input atl-select">
                                                <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                                                <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                                                <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
                                            </select>
                                        </div>
                                    </div>
                                )}

                                {config.second_engine === 'Claude (Anthropic)' && (
                                    <div className="atl-nested">
                                        <div className="atl-field">
                                            <label className="atl-label">Anthropic API Key</label>
                                            <input
                                                type="password"
                                                name="anthropic_key"
                                                value={config.anthropic_key || ''}
                                                onChange={handleChange}
                                                className="atl-input"
                                                style={{ fontFamily: 'var(--font-mono, monospace)' }}
                                            />
                                        </div>
                                        <div className="atl-field">
                                            <label className="atl-label">Model</label>
                                            <select name="claude_model" value={config.claude_model || ''} onChange={handleChange} className="atl-input atl-select">
                                                <option value="claude-sonnet-4-5">Claude Sonnet 4.5</option>
                                                <option value="claude-haiku-4-5">Claude Haiku 4.5</option>
                                                <option value="claude-opus-4-1">Claude Opus 4.1</option>
                                                <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                                            </select>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </Section>
                    </>
                )}

                {/* Theme */}
                <Section
                    icon={Palette}
                    title="Interface Theme"
                    subtitle="Pick a visual mood for Shakti"
                >
                    <div className="atl-theme-grid">
                        {themeOptions.map((option) => {
                            const isActive = option.id === theme;
                            return (
                                <button
                                    key={option.id}
                                    type="button"
                                    onClick={() => setTheme(option.id)}
                                    className={`atl-theme-card ${isActive ? 'atl-theme-card-active' : ''}`}
                                >
                                    <div className="atl-theme-head">
                                        <div style={{ minWidth: 0 }}>
                                            <p className="atl-theme-name">{option.label}</p>
                                            <p className="atl-theme-desc">{option.description}</p>
                                        </div>
                                        <span className={`atl-theme-dot ${isActive ? 'atl-theme-dot-active' : ''}`} />
                                    </div>
                                    <div className="atl-theme-swatches">
                                        {option.preview.map((color, idx) => (
                                            <span
                                                key={`${option.id}-${idx}`}
                                                className="atl-theme-swatch"
                                                style={{ background: color }}
                                            />
                                        ))}
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </Section>

                {/* Save */}
                <div className="atl-settings-actions">
                    <button type="submit" className="atl-btn-primary-sm" style={{ padding: '10px 20px' }}>
                        {saved ? <><Check size={14} /> Saved</> : <><Save size={14} /> Save Configuration</>}
                    </button>
                </div>
            </form>

            {/* Danger Zone */}
            <section className="atl-card atl-card-danger">
                <div className="atl-section-head">
                    <div
                        className="atl-section-icon"
                        style={{ background: 'var(--ink-accent-soft)', borderColor: 'rgba(194,65,12,0.2)', color: 'var(--ink-accent)' }}
                    >
                        <AlertTriangle size={16} strokeWidth={1.8} />
                    </div>
                    <div style={{ flex: 1 }}>
                        <h3 className="atl-section-title">Danger Zone</h3>
                        <p className="atl-section-sub">Irreversible actions — use with caution</p>
                    </div>
                </div>

                <div className="atl-danger-row">
                    <div className="atl-danger-text">
                        <h4>Clear All Data</h4>
                        <p>
                            Remove all optimization history, analysis data, and cached information.
                            Your account, settings, and subscription will remain intact.
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={() => setShowClearModal(true)}
                        className="atl-btn-danger"
                    >
                        <Trash2 size={14} />
                        Clear Data
                    </button>
                </div>
            </section>

            {/* Modal */}
            {showClearModal && (
                <div className="atl-modal-overlay" onClick={() => !clearing && setShowClearModal(false)}>
                    <div className="atl-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="atl-modal-head">
                            <div className="atl-modal-icon">
                                <AlertTriangle size={20} />
                            </div>
                            <h3>Clear All Data?</h3>
                        </div>

                        <p>This will permanently delete:</p>
                        <ul>
                            <li>All optimization history</li>
                            <li>Product analysis records</li>
                            <li>Cached data and temporary files</li>
                        </ul>

                        <div className="atl-modal-warn">
                            This action cannot be undone.
                        </div>

                        <div className="atl-modal-actions">
                            <button
                                onClick={() => setShowClearModal(false)}
                                disabled={clearing}
                                className="atl-btn-ghost-sm"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleClearData}
                                disabled={clearing}
                                className="atl-btn-danger atl-btn-danger-solid"
                            >
                                {clearing ? (
                                    <>
                                        <div style={{
                                            width: 12, height: 12,
                                            border: '2px solid currentColor',
                                            borderTopColor: 'transparent',
                                            borderRadius: '50%',
                                            animation: 'atlSpin 0.8s linear infinite',
                                        }} />
                                        Clearing…
                                    </>
                                ) : (
                                    <>
                                        <Trash2 size={14} />
                                        Clear All Data
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Settings;
