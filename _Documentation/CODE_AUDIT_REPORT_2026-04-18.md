# Code Audit Report

Date: 2026-04-18
Project: Shakti 1.2
Scope: Static audit of the active backend and frontend runtime paths, focused on auth, scraping, LLM integrations, storage, rendering, and deployment defaults.

## Executive Summary

This codebase is not production-safe in its current state. The two most serious issues are a built-in authentication bypass for any bearer token starting with demo_token_ and multiple server-side request forgery paths that allow the backend to fetch arbitrary URLs.

The frontend also renders model-generated HTML without sanitization while storing auth tokens and LLM API keys in localStorage, which creates a straightforward credential-theft chain if any XSS lands. Operationally, quotas and history are stored in process memory, so restarts and horizontal scaling will break core product behavior.

## Score

- Health score: 28/100
- Rating: Critical
- Total issues: 10
- Critical: 2
- High: 4
- Medium: 3
- Low: 1

Scoring basis:

- Critical: 15 points each
- High: 8 points each
- Medium: 3 points each
- Low: 1 point each

## Findings

### 1. Critical: Authentication bypass through demo tokens

Evidence:

- [backend/app/api/routes.py](backend/app/api/routes.py#L66)
- [backend/app/api/routes.py](backend/app/api/routes.py#L116)
- [backend/app/api/routes.py](backend/app/api/routes.py#L218)
- [backend/app/api/routes.py](backend/app/api/routes.py#L312)
- [backend/app/api/routes.py](backend/app/api/routes.py#L437)

Impact:

Any client can fabricate a bearer token with the demo_token_ prefix and be treated as an authenticated user for stats, history, single optimization, batch optimization, and product analysis. In production this is a direct authorization bypass, not a convenience feature.

Recommended fix:

Remove the prefix-based bypass entirely from protected routes. If demo access is required, issue a server-signed short-lived token with explicit demo claims and gate it behind an environment flag that is disabled in production.

### 2. Critical: SSRF through arbitrary URL fetching

Evidence:

- [backend/app/api/routes.py](backend/app/api/routes.py#L195)
- [backend/app/api/routes.py](backend/app/api/routes.py#L482)
- [backend/app/services/scraper_service.py](backend/app/services/scraper_service.py#L216)
- [backend/app/services/product_analyzer_service.py](backend/app/services/product_analyzer_service.py#L70)
- [backend/app/services/product_analysis_service.py](backend/app/services/product_analysis_service.py#L214)

Impact:

The backend fetches user-supplied URLs without hostname allowlists, DNS validation, or private-network blocking. An attacker can use these endpoints to probe internal services, cloud metadata endpoints, localhost-only services, or other internal network targets.

Recommended fix:

Restrict scraping to an explicit allowlist of supported e-commerce hosts, validate resolved IPs against private and link-local ranges, reject redirects to disallowed hosts, and log rejected attempts. If generic scraping is truly required, isolate it in a network-restricted worker.

### 3. High: XSS via unsanitized model-generated HTML

Evidence:

- [frontend/src/pages/SingleOptimize.jsx](frontend/src/pages/SingleOptimize.jsx#L340)
- [frontend/src/pages/History.jsx](frontend/src/pages/History.jsx#L135)

Impact:

The app injects generated listing HTML directly into the DOM with dangerouslySetInnerHTML. That content is produced by external LLMs and can contain unsafe attributes or payloads. A malicious or malformed response can execute script-like browser behavior and steal tokens, API keys, or user data.

Recommended fix:

Sanitize all rendered HTML with a strict allowlist sanitizer such as DOMPurify before rendering, or render only plain text / markdown. Treat model output as untrusted input.

### 4. High: Auth tokens and LLM API keys are stored in localStorage

Evidence:

- [frontend/src/contexts/AuthContext.jsx](frontend/src/contexts/AuthContext.jsx#L14)
- [frontend/src/contexts/AuthContext.jsx](frontend/src/contexts/AuthContext.jsx#L111)
- [frontend/src/App.jsx](frontend/src/App.jsx#L36)
- [frontend/src/App.jsx](frontend/src/App.jsx#L51)
- [frontend/src/pages/Settings.jsx](frontend/src/pages/Settings.jsx#L125)
- [frontend/src/pages/Settings.jsx](frontend/src/pages/Settings.jsx#L219)
- [frontend/src/pages/Settings.jsx](frontend/src/pages/Settings.jsx#L248)

Impact:

Google auth tokens and OpenAI, Gemini, and Anthropic keys persist in browser storage. With the XSS issue above, this becomes immediate credential exfiltration. Even without XSS, browser extensions and shared-device scenarios raise the risk substantially.

Recommended fix:

Move authentication to httpOnly sameSite cookies. If this product is bring-your-own-key, store encrypted provider keys server-side per user session or account instead of in localStorage. At minimum, keep them only in memory for the active tab.

### 5. High: Core state is stored in process memory

Evidence:

- [backend/app/services/auth_service.py](backend/app/services/auth_service.py#L15)
- [backend/app/services/auth_service.py](backend/app/services/auth_service.py#L16)
- [backend/app/services/history_service.py](backend/app/services/history_service.py#L8)

Impact:

Users, quotas, and optimization history disappear on restart and diverge across multiple instances. Any horizontal scale-out, deploy restart, or worker recycle will reset usage enforcement and break user expectations.

Recommended fix:

Move auth metadata, quota counters, and history into a durable shared store such as Postgres plus Redis. Quota enforcement should be atomic and shared across all instances.

### 6. High: Expensive endpoints run synchronously with no rate limiting or job isolation

Evidence:

- [backend/app/api/routes.py](backend/app/api/routes.py#L352)
- [backend/app/api/routes.py](backend/app/api/routes.py#L475)
- [backend/app/api/routes.py](backend/app/api/routes.py#L507)

Impact:

Batch optimization processes rows sequentially inside the request cycle, and product analysis chains scraping plus multiple LLM calls before responding. Under real load this will tie up workers, amplify latency, and create cascading failures.

Recommended fix:

Add per-user and per-IP rate limiting, move long-running work to background jobs, and return job IDs for polling or streaming progress. Bound concurrency for outbound LLM and scraping calls.

### 7. Medium: CORS fails open when ALLOWED_ORIGINS is not configured

Evidence:

- [backend/main.py](backend/main.py#L9)
- [backend/main.py](backend/main.py#L16)
- [backend/main.py](backend/main.py#L17)

Impact:

If the environment variable is missing, the backend allows all origins. That makes cross-origin usage far broader than intended and increases exposure if tokens are stolen or if a browser-side flaw appears.

Recommended fix:

Fail closed in non-development environments. Use explicit origin lists and separate development defaults from production startup.

### 8. Medium: Quota logic is inconsistent between backend and frontend

Evidence:

- [backend/app/services/auth_service.py](backend/app/services/auth_service.py#L122)
- [backend/app/services/auth_service.py](backend/app/services/auth_service.py#L126)
- [frontend/src/pages/ProductAnalysis.jsx](frontend/src/pages/ProductAnalysis.jsx#L115)
- [frontend/src/pages/SingleOptimize.jsx](frontend/src/pages/SingleOptimize.jsx#L114)
- [frontend/src/pages/SingleOptimize.jsx](frontend/src/pages/SingleOptimize.jsx#L173)

Impact:

The backend enforces a limit of 10 while the UI communicates 5. This causes billing confusion, support overhead, and brittle client-side guardrails.

Recommended fix:

Define quota values in one server-side source of truth and return them via the stats endpoint. The UI should render whatever the backend reports.

### 9. Medium: Aggressive stats polling creates avoidable backend load

Evidence:

- [frontend/src/components/UserProfile.jsx](frontend/src/components/UserProfile.jsx#L10)
- [frontend/src/components/UserProfile.jsx](frontend/src/components/UserProfile.jsx#L14)

Impact:

Each signed-in browser polls user stats every 5 seconds. At scale this becomes a large amount of low-value traffic and competes with the app's expensive AI endpoints.

Recommended fix:

Refresh stats after state-changing actions and on tab focus. If periodic polling is still needed, widen the interval substantially and pause when the dropdown is closed or the tab is hidden.

### 10. Low: Sensitive business data is pushed into analytics and logs

Evidence:

- [frontend/src/pages/ProductAnalysis.jsx](frontend/src/pages/ProductAnalysis.jsx#L31)
- [frontend/src/utils/analytics.js](frontend/src/utils/analytics.js#L19)
- [backend/app/services/auth_service.py](backend/app/services/auth_service.py#L93)
- [backend/app/api/routes.py](backend/app/api/routes.py#L481)
- [backend/app/services/product_analysis_service.py](backend/app/services/product_analysis_service.py#L193)

Impact:

Product URLs, product names, user emails, and model-response fragments are written to analytics and console logs. For agency or enterprise customers this is a privacy and data-governance problem.

Recommended fix:

Redact or hash sensitive fields before logging or analytics emission. Adopt structured logging with explicit allowlists for safe fields.

## Scalability and Architecture Notes

- The codebase currently has two overlapping product-analysis stacks in [backend/app/services/product_analyzer_service.py](backend/app/services/product_analyzer_service.py) and [backend/app/services/product_analysis_service.py](backend/app/services/product_analysis_service.py). This increases drift risk and doubles maintenance cost.
- The DOCX extraction endpoint reads the full upload into memory at [backend/app/api/routes.py](backend/app/api/routes.py#L160) and [backend/app/api/routes.py](backend/app/api/routes.py#L161) with no size or type enforcement.
- There is no structured retry, backoff, circuit breaker, or provider-failure isolation around outbound LLM calls. A transient provider slowdown will directly hit request latency and success rate.
- Observability is mostly print-based today. That is not enough for incident response once this app runs behind multiple workers or in managed hosting.

## Unused or Redundant Code Risk

- Product scraping and analysis responsibilities are duplicated across [backend/app/services/product_analyzer_service.py](backend/app/services/product_analyzer_service.py) and [backend/app/services/product_analysis_service.py](backend/app/services/product_analysis_service.py).
- Some UI pages are marked Soon in navigation but are still routable, which increases the visible surface area without providing complete product value. That is a product-quality issue more than a security issue.

## Remediation Plan

### Phase 1: Immediate containment

1. Remove demo token bypasses from all protected routes.
2. Disable generic URL fetching until SSRF protections are implemented.
3. Stop rendering unsanitized HTML in the frontend.
4. Turn off verbose logs that include emails, URLs, and model output.

### Phase 2: Secure the trust boundaries

1. Move auth to secure cookies and stop storing provider keys in localStorage.
2. Enforce strict CORS and explicit environment-based startup validation.
3. Add upload size limits, MIME validation, and request size limits.
4. Add server-side rate limiting to auth, scraping, and LLM endpoints.

### Phase 3: Stabilize persistence and scale

1. Replace in-memory user, usage, and history stores with durable shared storage.
2. Move batch jobs and deep analysis to asynchronous workers.
3. Add retry and timeout policy per provider with bounded concurrency.
4. Replace 5-second client polling with event-driven refresh or slow polling.

### Phase 4: Simplify and harden the architecture

1. Consolidate the duplicate product-analysis service layers.
2. Introduce structured logging, metrics, and health/readiness endpoints.
3. Centralize product limits and feature flags in the backend.
4. Add automated tests for auth, quotas, HTML sanitization, and URL validation.

## System Flow

Frontend flow:

Login -> Google OAuth -> backend token verification -> token stored in browser -> protected pages call backend APIs with bearer token -> results rendered in React UI -> selected outputs saved in local browser storage.

Optimization flow:

SingleOptimize or BatchOptimize -> frontend sends product data plus user-supplied API keys -> backend route validates token -> backend calls L1 and optional L2 model pipeline -> backend stores history in memory -> frontend renders final HTML and allows export.

Product analysis flow:

ProductAnalysis page -> backend validates token -> backend scrapes target URL -> backend performs deep analysis -> backend extracts keywords -> backend generates competitor analysis -> backend increments in-memory quota -> frontend renders results and emits analytics events.

Storage and control points:

Frontend storage: localStorage for auth token, user object, theme, and engine config.

Backend storage: in-memory dicts and deque for user records, quotas, and history.

External dependencies: Google token verification, OpenAI, Gemini, Anthropic, remote target websites for scraping, Google Analytics.

## Audit Method Notes

- This was a static audit only. I did not run runtime penetration tests, load tests, or end-to-end user flows.
- The audit focused on active runtime files in backend/main.py, backend/app/api, backend/app/services, frontend/src, and deployment or setup documentation.