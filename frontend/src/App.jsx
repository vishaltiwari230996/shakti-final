import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import ReactGA from 'react-ga4';
import { useAuth } from './contexts/AuthContext';
import AtelierLayout from './components/AtelierLayout';
import Login from './components/Login';
import Overview from './pages/Overview';
import SingleOptimize from './pages/SingleOptimize';
import BatchOptimize from './pages/BatchOptimize';
import Support from './pages/Support';
import Settings from './pages/Settings';
import ProductAnalysis from './pages/ProductAnalysis';
import History from './pages/History';
import AnalysisHistory from './pages/AnalysisHistory';
import KeywordDatabase from './pages/KeywordDatabase';
import SKUGroups from './pages/SKUGroups';
import Billing from './pages/Billing';
import SchemaDesigner from './pages/SchemaDesigner';
import MyCatalogue from './pages/MyCatalogue';

const LEGACY_CONFIG_STORAGE_KEY = 'shakti_config';
const CONFIG_PREFERENCES_STORAGE_KEY = 'shakti_config_preferences';
const DEFAULT_CONFIG = {
    // Mode selector: 'classic' (per-provider keys) or 'openrouter' (unified)
    mode: 'openrouter',

    // Classic mode
    openai_key: '',
    openai_model: 'gpt-4.1-mini',
    second_engine: 'None',
    openai2_key: '',
    openai2_model: 'gpt-4o',
    gemini_key: '',
    gemini_model: 'gemini-2.5-pro',
    anthropic_key: '',
    claude_model: 'claude-sonnet-4-5',

    // OpenRouter unified mode
    openrouter_key: '',
    l1_model: 'openai/gpt-4o',
    l2_model: 'anthropic/claude-3.5-sonnet',
    l1_temperature: 0.2,
    l2_temperature: 0.2,
};

function parseStoredJson(value) {
    if (!value) {
        return {};
    }

    try {
        return JSON.parse(value);
    } catch {
        return {};
    }
}

function loadInitialConfig() {
    const persistedPreferences = parseStoredJson(localStorage.getItem(CONFIG_PREFERENCES_STORAGE_KEY));
    const legacyConfig = parseStoredJson(localStorage.getItem(LEGACY_CONFIG_STORAGE_KEY));

    return {
        ...DEFAULT_CONFIG,
        ...legacyConfig,
        ...persistedPreferences,
        openai_key: '',
        openai2_key: '',
        gemini_key: '',
        anthropic_key: '',
        openrouter_key: '',
    };
}

function buildPersistedConfig(config) {
    return {
        mode: config.mode,
        openai_model: config.openai_model,
        second_engine: config.second_engine,
        openai2_model: config.openai2_model,
        gemini_model: config.gemini_model,
        claude_model: config.claude_model,
        l1_model: config.l1_model,
        l2_model: config.l2_model,
        l1_temperature: config.l1_temperature,
        l2_temperature: config.l2_temperature,
    };
}

// Page tracker component
function PageTracker() {
    const location = useLocation();
    
    useEffect(() => {
        // Track page view
        ReactGA.send({ hitType: "pageview", page: location.pathname, title: document.title });
        console.log('📊 Page view tracked:', location.pathname);
    }, [location]);
    
    return null;
}

function AppContent() {
    const { isAuthenticated, loading } = useAuth();

    const [config, setConfig] = useState(loadInitialConfig);

    useEffect(() => {
        localStorage.removeItem(LEGACY_CONFIG_STORAGE_KEY);
        localStorage.setItem(
            CONFIG_PREFERENCES_STORAGE_KEY,
            JSON.stringify(buildPersistedConfig(config))
        );
    }, [config]);

    // Developer tools — bypass auth entirely (not part of the app)
    if (typeof window !== 'undefined' && window.location.pathname.startsWith('/dev/')) {
        return (
            <Router>
                <Routes>
                    <Route path="/dev/schema" element={<SchemaDesigner />} />
                    <Route path="*" element={<Navigate to="/dev/schema" replace />} />
                </Routes>
            </Router>
        );
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Login />;
    }

    return (
        <Router>
            <PageTracker />
            <Routes>
                {/* Main app */}
                <Route
                    path="*"
                    element={
                        <AtelierLayout>
                            <Routes>
                                <Route path="/" element={<MyCatalogue />} />
                                <Route path="/my-catalogue" element={<MyCatalogue />} />
                                <Route path="/overview" element={<Overview />} />
                                <Route path="/optimize" element={<SingleOptimize config={config} />} />
                                <Route path="/batch" element={<BatchOptimize config={config} />} />
                                <Route path="/analyze" element={<ProductAnalysis config={config} />} />
                                <Route path="/history" element={<History />} />
                                <Route path="/analysis-history" element={<AnalysisHistory />} />
                                <Route path="/keywords" element={<KeywordDatabase />} />
                                <Route path="/sku-groups" element={<SKUGroups />} />
                                <Route path="/billing" element={<Billing />} />
                                <Route path="/support" element={<Support />} />
                                <Route path="/settings" element={<Settings config={config} setConfig={setConfig} />} />
                                <Route path="/test-ui" element={<Navigate to="/" replace />} />
                                <Route path="*" element={<Navigate to="/" replace />} />
                            </Routes>
                        </AtelierLayout>
                    }
                />
            </Routes>
        </Router>
    );
}

function App() {
    return <AppContent />;
}

export default App;
