# _Archive Folder

This folder contains legacy code, old versions, and test files that are no longer used in the active project but kept for reference.

## Folder Structure

```
_Archive/
├── Old Code/
│   └── scraper.py          # Legacy Streamlit-based product scraper
│
└── Test Files/
    └── test_url_extraction.py  # Test script for URL extraction API
```

## Contents

### Old Code/

#### `scraper.py`
- **Version**: v5.1 (Zero Hallucination Edition)
- **Type**: Legacy Streamlit application
- **Purpose**: Original product analyzer with Streamlit UI
- **Lines**: 1,335+
- **Status**: ⚠️ Deprecated - replaced by FastAPI backend + React frontend

**Key Features** (Legacy):
- Streamlit web interface
- Product data extraction from Amazon/Flipkart
- Basic competitor analysis
- Keyword generation
- All UI and backend logic in single file

**Why Archived**:
- Replaced by modern stack (FastAPI + React)
- Better separation of concerns in new architecture
- Improved API design and scalability
- Enhanced UI/UX with React components

**When to Reference**:
- Understanding original scraper logic
- Legacy prompt engineering approaches
- Historical analysis patterns

---

### Test Files/

#### `test_url_extraction.py`
- **Type**: Manual test script
- **Purpose**: Test the `/api/extract-url` endpoint
- **Test URL**: Amazon iPhone 15 product page
- **Status**: ⚠️ Deprecated - use unit tests or Postman instead

**What it Tests**:
- API endpoint connectivity
- Product data extraction from Amazon
- Response structure and formatting

**How to Use** (if needed):
```bash
python test_url_extraction.py
```

**When to Reference**:
- Understanding expected API response format
- Manual endpoint testing examples
- Debugging scraper issues

---

## Migration Notes

### From Streamlit to FastAPI + React

| Aspect | Old (Streamlit) | New (FastAPI + React) |
|--------|-----------------|----------------------|
| **Backend** | Streamlit (UI+Logic) | FastAPI (Logic only) |
| **Frontend** | Streamlit web | React + Vite |
| **Scalability** | Single user sessions | Multi-user API |
| **API** | Not REST | Full REST API |
| **Deployment** | Streamlit Cloud | Railway/Vercel |
| **Performance** | Slower for batch ops | Optimized with async |
| **Code Org** | Single file (1335 lines) | Modular services |

### Files Affected by Migration

**New equivalent files**:
- `scraper.py` → `backend/app/services/scraper_service.py` + `product_analyzer_service.py`
- Streamlit UI → `frontend/src/pages/*.jsx`
- Manual testing → Unit tests (recommended)

---

## When to Use Files in _Archive

✅ **DO use for reference**:
- Understanding original business logic
- Finding old scraper selectors for specific platforms
- Learning from historical implementation decisions
- Debugging if issues arise from scraper changes

❌ **DON'T use for**:
- Active development (use current files instead)
- Deployment (they're outdated)
- Integration (use new API endpoints)

---

## Cleanup Recommendations

These files can be safely deleted if:
1. All logic has been ported to new architecture ✓
2. No team members need to reference old code ✓
3. Git history is preserved (if using version control) ✓

**Current Status**: Kept for reference. Safe to delete after full team confirmation.

---

## Contact

If you need to recover or understand any archived code:
- Check Git history for full file versions
- Refer to documentation in `_Documentation/`
- Review new equivalents in active codebase
