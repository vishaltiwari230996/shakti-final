import React, { useState } from 'react';
import axios from 'axios';
import {
    Link as LinkIcon, Loader2, Check, AlertCircle, Zap, TrendingUp,
    Users, ShoppingCart, BarChart3, BookOpen, Search, Target
} from 'lucide-react';
import {
    trackProductAnalysisStarted, trackProductAnalysisCompleted,
    trackCompetitorAnalysisViewed, trackKeywordsExtracted, trackError
} from '../utils/analytics';
import { useAuth } from '../contexts/AuthContext';

const Section = ({ icon: Icon, title, subtitle, children, extra }) => (
    <section className="atl-card">
        <div className="atl-section-head">
            <div className="atl-section-icon"><Icon size={16} strokeWidth={1.8} /></div>
            <div style={{ flex: 1, minWidth: 0 }}>
                <h3 className="atl-section-title">{title}</h3>
                {subtitle && <p className="atl-section-sub">{subtitle}</p>}
            </div>
            {extra}
        </div>
        {children}
    </section>
);

const ProductAnalysis = ({ config }) => {
    const { token, userStats, fetchUserStats } = useAuth();
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);
    const [competitors, setCompetitors] = useState([]);
    const [competitorInput, setCompetitorInput] = useState(['', '', '']);

    const handleAnalyze = async () => {
        if (!url.trim()) {
            setError('Please enter a product URL');
            return;
        }

        trackProductAnalysisStarted(url.trim(), config.openai_model || 'gpt-4o-mini');

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const response = await axios.post('/api/product-analysis/analyze', {
                url: url.trim(),
                api_key: config.openai_key,
                model: config.openai_model || 'gpt-4o-mini'
            }, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.data.success) {
                setResult(response.data);
                fetchUserStats?.(token);
                trackProductAnalysisCompleted(
                    response.data.product_data?.title || 'Unknown',
                    response.data.deep_analysis?.main_category || 'Unknown'
                );
                if (response.data.keywords?.short_tail) {
                    trackKeywordsExtracted(response.data.keywords.short_tail.length);
                }
                if (response.data.competitor_analysis?.competitors) {
                    trackCompetitorAnalysisViewed(response.data.competitor_analysis.competitors.length);
                }
                setUrl('');
                setCompetitorInput(['', '', '']);
            } else {
                setError(response.data.error || 'Analysis failed');
                trackError('analysis_failed', response.data.error || 'Analysis failed');
            }
        } catch (err) {
            const errorMsg = err.response?.data?.detail || err.message || 'Analysis failed';
            setError(errorMsg);
            trackError('analysis_error', errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const handleCompetitorChange = (index, value) => {
        const newInput = [...competitorInput];
        newInput[index] = value;
        setCompetitorInput(newInput);
    };

    const handleAddCompetitors = () => {
        const newCompetitors = competitorInput
            .filter(name => name.trim())
            .map(name => ({ name: name.trim(), publisher: '' }));
        if (newCompetitors.length === 0) {
            setError('Please enter at least one competitor');
            return;
        }
        setCompetitors(newCompetitors);
        setCompetitorInput(['', '', '']);
    };

    const usage = userStats?.usage?.product_analysis;

    return (
        <div className="atl-page atl-page-wide">
            <Section
                icon={Search}
                title="Product Analysis"
                subtitle="Deep-dive any Amazon or Flipkart listing — category, features, keywords, competitors."
            />

            <div className="atl-split atl-split-lg">
                {/* LEFT — Input */}
                <div className="atl-col">
                    {usage && (
                        <section className="atl-card">
                            <div className="atl-usage">
                                <div className="atl-usage-head">
                                    <span><strong>Product Analyses</strong></span>
                                    <span>{usage.used}/{usage.limit} used</span>
                                </div>
                                <div className="atl-usage-bar">
                                    <div
                                        className={`atl-usage-fill ${usage.used / usage.limit > 0.8 ? 'warn' : ''}`}
                                        style={{ width: `${Math.min((usage.used / usage.limit) * 100, 100)}%` }}
                                    />
                                </div>
                                <p className="atl-muted">
                                    {usage.remaining} analysis{usage.remaining !== 1 ? 'es' : ''} remaining
                                </p>
                            </div>
                        </section>
                    )}

                    <Section
                        icon={LinkIcon}
                        title="Product URL"
                        subtitle="Supports Amazon.in and Flipkart."
                    >
                        <div className="atl-field">
                            <label className="atl-label">URL</label>
                            <input
                                type="url"
                                className="atl-input"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                                placeholder="https://www.amazon.in/dp/..."
                                disabled={loading}
                            />
                        </div>
                        <button
                            className="atl-btn-primary atl-btn-primary-block"
                            onClick={handleAnalyze}
                            disabled={loading || !url.trim()}
                        >
                            {loading ? (
                                <><Loader2 size={15} className="atl-spin" /> Analyzing…</>
                            ) : (
                                <><Zap size={15} /> Analyze Product</>
                            )}
                        </button>
                        {error && (
                            <div className="atl-alert atl-alert-error" style={{ marginTop: 12 }}>
                                <AlertCircle size={14} />
                                <span>{error}</span>
                            </div>
                        )}
                    </Section>

                    {result && !competitors.length && (
                        <Section
                            icon={ShoppingCart}
                            title="Add Competitors"
                            subtitle="Optional — up to three brands to benchmark against."
                        >
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                {[0, 1, 2].map((i) => (
                                    <input
                                        key={i}
                                        type="text"
                                        className="atl-input"
                                        value={competitorInput[i]}
                                        onChange={(e) => handleCompetitorChange(i, e.target.value)}
                                        placeholder={`Competitor ${i + 1} name…`}
                                    />
                                ))}
                            </div>
                            <button
                                onClick={handleAddCompetitors}
                                className="atl-btn-secondary"
                                disabled={competitorInput.every(c => !c.trim())}
                                style={{ marginTop: 12, width: '100%' }}
                            >
                                Add &amp; Compare
                            </button>
                            <p className="atl-muted-sm">Appears in the competitive-analysis panel after submission.</p>
                        </Section>
                    )}
                </div>

                {/* RIGHT — Results */}
                <div className="atl-col">
                    {result ? (
                        <>
                            <Section
                                icon={Target}
                                title={result.deep_analysis?.product_name || 'Product Analysis'}
                                subtitle={result.deep_analysis?.brand_publisher}
                                extra={<Check size={18} style={{ color: 'var(--ink-success)' }} />}
                            >
                                <div className="atl-meta-grid">
                                    <div className="atl-meta-item">
                                        <p>Category</p>
                                        <p>{result.deep_analysis?.main_category || '—'}</p>
                                    </div>
                                    <div className="atl-meta-item">
                                        <p>Sub-Category</p>
                                        <p>{result.deep_analysis?.sub_category || '—'}</p>
                                    </div>
                                    <div className="atl-meta-item">
                                        <p>Platform</p>
                                        <p>{result.product_data?.platform || '—'}</p>
                                    </div>
                                    <div className="atl-meta-item">
                                        <p>Price</p>
                                        <p>{result.product_data?.price || 'N/A'}</p>
                                    </div>
                                </div>
                            </Section>

                            {result.deep_analysis?.key_features?.length > 0 && (
                                <Section
                                    icon={TrendingUp}
                                    title="Key Features"
                                    subtitle={`${result.deep_analysis.key_features.length} feature${result.deep_analysis.key_features.length !== 1 ? 's' : ''} extracted.`}
                                >
                                    <ul className="atl-feature-list">
                                        {result.deep_analysis.key_features.map((feature, i) => (
                                            <li key={i}>
                                                <Check size={13} strokeWidth={2} />
                                                <span>{feature}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </Section>
                            )}

                            {result.keywords && (
                                <Section
                                    icon={BookOpen}
                                    title="SEO Keywords"
                                    subtitle="Ranked from short-tail to long-tail."
                                >
                                    {result.keywords.short_tail?.length > 0 && (
                                        <div className="atl-field">
                                            <p className="atl-label-caps">Short-Tail</p>
                                            <div className="atl-chip-group">
                                                {result.keywords.short_tail.map((kw, i) => (
                                                    <span key={i} className="atl-chip atl-chip-accent">{kw}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {result.keywords.mid_tail?.length > 0 && (
                                        <div className="atl-field">
                                            <p className="atl-label-caps">Mid-Tail</p>
                                            <div className="atl-chip-group">
                                                {result.keywords.mid_tail.map((kw, i) => (
                                                    <span key={i} className="atl-chip">{kw}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {result.keywords.long_tail?.length > 0 && (
                                        <div className="atl-field">
                                            <p className="atl-label-caps">Long-Tail</p>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                                {result.keywords.long_tail.map((kw, i) => (
                                                    <div key={i} className="atl-result-box" style={{ padding: '8px 12px', fontSize: 12.5 }}>
                                                        {kw}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </Section>
                            )}

                            {result.competitor_analysis?.competitors?.length > 0 && (
                                <Section
                                    icon={ShoppingCart}
                                    title="Competitor Landscape"
                                    subtitle={`${result.competitor_analysis.competitors.length} competitor${result.competitor_analysis.competitors.length !== 1 ? 's' : ''} detected.`}
                                >
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                        {result.competitor_analysis.competitors.map((c, i) => (
                                            <div key={i} className="atl-insight">
                                                <div className="atl-insight-head">
                                                    <div>
                                                        <h4 className="atl-insight-title">#{c.rank} {c.brand}</h4>
                                                        <p className="atl-insight-sub">{c.product_name}</p>
                                                    </div>
                                                    <span className={`atl-chip ${
                                                        c.threat_level === 'High' ? 'atl-chip-warn' :
                                                        c.threat_level === 'Medium' ? 'atl-chip' :
                                                        'atl-chip-success'
                                                    }`}>
                                                        {c.threat_level} threat
                                                    </span>
                                                </div>
                                                <div className="atl-meta-grid">
                                                    <div className="atl-meta-item">
                                                        <p>Price Range</p>
                                                        <p>{c.price_range || '—'}</p>
                                                    </div>
                                                    <div className="atl-meta-item">
                                                        <p>Availability</p>
                                                        <p>{c.availability || '—'}</p>
                                                    </div>
                                                </div>
                                                <div>
                                                    <p className="atl-pro-label">Key Strength</p>
                                                    <p style={{ fontSize: 12.5, color: 'var(--ink-2)', margin: 0, lineHeight: 1.5 }}>
                                                        {c.key_strength}
                                                    </p>
                                                </div>
                                                <div>
                                                    <p className="atl-con-label">Your Advantage</p>
                                                    <p style={{ fontSize: 12.5, color: 'var(--ink-2)', margin: 0, lineHeight: 1.5 }}>
                                                        {c.key_weakness}
                                                    </p>
                                                </div>
                                                <hr className="atl-insight-divider" />
                                                <p style={{ fontSize: 12, color: 'var(--ink-3)', margin: 0, lineHeight: 1.5 }}>
                                                    <strong style={{ color: 'var(--ink-2)' }}>Why customers choose:</strong> {c.customer_preference_reason}
                                                </p>
                                            </div>
                                        ))}
                                    </div>

                                    {result.competitor_analysis.market_analysis && (
                                        <div className="atl-insight" style={{ marginTop: 16 }}>
                                            <h4 className="atl-insight-title">Market Analysis</h4>
                                            <div className="atl-meta-grid">
                                                <div className="atl-meta-item">
                                                    <p>Your Position</p>
                                                    <p>{result.competitor_analysis.market_analysis.subject_product_position || '—'}</p>
                                                </div>
                                                <div className="atl-meta-item">
                                                    <p>Competitive Intensity</p>
                                                    <p>{result.competitor_analysis.market_analysis.competitive_intensity || '—'}</p>
                                                </div>
                                            </div>
                                            {result.competitor_analysis.market_analysis.market_gaps?.length > 0 && (
                                                <div>
                                                    <p className="atl-pro-label">Market Opportunities</p>
                                                    <ul className="atl-feature-list">
                                                        {result.competitor_analysis.market_analysis.market_gaps.map((gap, i) => (
                                                            <li key={i}><Check size={13} strokeWidth={2} /><span>{gap}</span></li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                            {result.competitor_analysis.market_analysis.recommendation && (
                                                <div className="atl-result-box" style={{ fontSize: 12.5 }}>
                                                    <strong>Strategy Recommendation:</strong> {result.competitor_analysis.market_analysis.recommendation}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </Section>
                            )}

                            {result.deep_analysis?.competitor_search_queries?.length > 0 && !competitors.length && (
                                <Section
                                    icon={BarChart3}
                                    title="Competitor Search Queries"
                                    subtitle="Suggested terms to research rival listings."
                                >
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                        {result.deep_analysis.competitor_search_queries.map((query, i) => (
                                            <div key={i} className="atl-result-box" style={{ padding: '8px 12px', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                                                {i + 1}. {query}
                                            </div>
                                        ))}
                                    </div>
                                </Section>
                            )}

                            {result.deep_analysis?.competitor_brands?.length > 0 && (
                                <Section
                                    icon={Users}
                                    title="Known Competitor Brands"
                                    subtitle="Recognized brand names in this category."
                                >
                                    <div className="atl-chip-group">
                                        {result.deep_analysis.competitor_brands.map((brand, i) => (
                                            <span key={i} className="atl-chip">{brand}</span>
                                        ))}
                                    </div>
                                </Section>
                            )}

                            {competitors.length > 0 && (
                                <Section
                                    icon={ShoppingCart}
                                    title="Selected Competitors"
                                    subtitle="Queued for detailed comparison."
                                >
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                        {competitors.map((comp, i) => (
                                            <div key={i} className="atl-result-box" style={{ padding: '10px 14px' }}>
                                                <strong>{comp.name}</strong>
                                            </div>
                                        ))}
                                    </div>
                                </Section>
                            )}

                            <button
                                onClick={() => {
                                    setResult(null);
                                    setCompetitors([]);
                                    setUrl('');
                                    setError('');
                                }}
                                className="atl-btn-secondary"
                                style={{ width: '100%' }}
                            >
                                Analyze Another Product
                            </button>
                        </>
                    ) : (
                        <section className="atl-card">
                            <div className="atl-empty">
                                <div className="atl-empty-icon"><LinkIcon size={26} strokeWidth={1.5} /></div>
                                <h3 className="atl-empty-title">Ready to analyze</h3>
                                <p className="atl-empty-desc">
                                    Enter a product URL from Amazon or Flipkart to get deep insights:
                                    categorization, SEO keywords, competitor mapping, and strategic recommendations.
                                </p>
                            </div>
                        </section>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProductAnalysis;
