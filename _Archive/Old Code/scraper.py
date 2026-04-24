"""
AI Product Analyzer v4.0 - OpenAI GPT Edition
==============================================
MAJOR IMPROVEMENTS:
- Deep product analysis to extract exact product type
- Multi-step intelligent search for accurate competitors
- Category validation to prevent wrong matches
- Educational books get education-specific competitor search
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urlparse, quote_plus, unquote
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import os

# ============== PAGE CONFIG ==============
st.set_page_config(
    page_title="AI Product Analyzer v4 - GPT",
    page_icon="🎯",
    layout="wide"
)

# ============== STYLING ==============
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10a37f 0%, #1a7f5a 50%, #0d6647 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .version-badge {
        background: linear-gradient(135deg, #10a37f 0%, #0d6647 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1f2937;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #10a37f;
    }
    .keyword-chip {
        display: inline-block;
        background: linear-gradient(135deg, #10a37f 0%, #0d6647 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
    .keyword-chip-secondary {
        display: inline-block;
        background: white;
        color: #10a37f;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
        border: 2px solid #10a37f;
    }
    .competitor-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #10a37f;
    }
    .info-box {
        background: #ecfdf5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #10a37f;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fffbeb;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    .gpt-badge {
        background: #10a37f;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .product-detail-box {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============== DATA CLASSES ==============
@dataclass
class ProductData:
    title: str = ""
    description: str = ""
    price: str = ""
    brand: str = ""
    category: str = ""
    features: List[str] = field(default_factory=list)
    platform: str = ""
    url: str = ""
    raw_text: str = ""


@dataclass
class DeepProductAnalysis:
    """Deep analysis of product for accurate categorization"""
    # Basic info
    product_name: str = ""
    brand_publisher: str = ""
    
    # Detailed categorization
    main_category: str = ""          # e.g., "Educational Books"
    sub_category: str = ""           # e.g., "CBSE Question Banks"
    product_type: str = ""           # e.g., "Class 9 Mathematics Question Bank"
    
    # For educational products
    education_board: str = ""        # CBSE, ICSE, State Board
    grade_class: str = ""            # Class 9, Class 10, etc.
    subject: str = ""                # Mathematics, Science, etc.
    book_type: str = ""              # Question Bank, Textbook, Reference, Sample Papers
    target_exam: str = ""            # Board Exams 2026, JEE, NEET
    
    # For non-educational products
    target_audience: str = ""
    key_features: List[str] = field(default_factory=list)
    
    # Search strategy
    competitor_search_queries: List[str] = field(default_factory=list)
    competitor_brands: List[str] = field(default_factory=list)


@dataclass
class KeywordAnalysis:
    short_tail: List[str] = field(default_factory=list)
    mid_tail: List[str] = field(default_factory=list)
    long_tail: List[str] = field(default_factory=list)
    seo_keywords: List[str] = field(default_factory=list)


@dataclass
class Competitor:
    name: str = ""
    publisher_brand: str = ""
    why_competitor: str = ""
    url: str = ""


# ============== UTILITY FUNCTIONS ==============
def get_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }


def detect_platform(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if 'amazon' in domain:
        return 'amazon'
    elif 'flipkart' in domain:
        return 'flipkart'
    return 'unknown'


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


# ============== OPENAI CLIENT ==============
class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    
    def chat_json(self, messages: List[Dict], temperature: float = 0.2) -> Dict:
        if messages[0]['role'] != 'system':
            messages.insert(0, {'role': 'system', 'content': 'Respond only in valid JSON.'})
        
        response = self.chat(messages, temperature=temperature)
        
        # Clean JSON
        response = response.strip()
        response = re.sub(r'^```json\s*', '', response)
        response = re.sub(r'^```\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
        
        return json.loads(response)


# ============== SCRAPER ==============
class ProductScraper:
    def scrape(self, url: str) -> ProductData:
        platform = detect_platform(url)
        data = ProductData(platform=platform.capitalize(), url=url)
        
        try:
            session = requests.Session()
            if platform == 'amazon':
                session.get('https://www.amazon.in', headers=get_headers(), timeout=10)
            time.sleep(0.5)
            
            response = session.get(url, headers=get_headers(), timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for tag in soup(['script', 'style', 'noscript']):
                tag.decompose()
            
            self._parse_page(soup, data, platform)
            
        except Exception as e:
            # Fallback: extract from URL
            decoded = unquote(url)
            if platform == 'amazon':
                match = re.search(r'amazon\.[^/]+/([^/]+)/dp/', decoded)
                if match:
                    data.title = match.group(1).replace('-', ' ').title()
            data.raw_text = f"URL_EXTRACTED: {data.title}"
        
        return data
    
    def _parse_page(self, soup: BeautifulSoup, data: ProductData, platform: str):
        all_text = []
        
        # Title
        for sel in ['#productTitle', '#title span', 'span.VU-ZEz', 'span.B_NuCI']:
            elem = soup.select_one(sel)
            if elem:
                data.title = clean_text(elem.get_text())
                all_text.append(f"TITLE: {data.title}")
                break
        
        # Brand/Publisher
        for sel in ['#bylineInfo', '.po-brand .a-span9', 'a#bylineInfo']:
            elem = soup.select_one(sel)
            if elem:
                data.brand = clean_text(elem.get_text())
                data.brand = re.sub(r'(Visit the |Brand: | Store|by )', '', data.brand)
                all_text.append(f"BRAND: {data.brand}")
                break
        
        # Features
        for bullet in soup.select('#feature-bullets li span.a-list-item, li._21Ahn-'):
            text = clean_text(bullet.get_text())
            if text and len(text) > 5:
                data.features.append(text)
                all_text.append(f"FEATURE: {text}")
        
        # Description
        for sel in ['#productDescription', '#bookDescription_feature_div', 'div._1mXcCf']:
            elems = soup.select(sel)
            for elem in elems:
                text = clean_text(elem.get_text())
                if text:
                    data.description += ' ' + text[:500]
                    all_text.append(f"DESC: {text[:300]}")
        
        # Category
        breadcrumbs = soup.select('#wayfinding-breadcrumbs_feature_div a, div._1MR4o5 a')
        if breadcrumbs:
            cats = [clean_text(b.get_text()) for b in breadcrumbs if clean_text(b.get_text())]
            data.category = ' > '.join(cats)
            all_text.append(f"CATEGORY: {data.category}")
        
        # Price
        for sel in ['.a-price .a-offscreen', '#priceblock_ourprice', 'div.Nx9bqj']:
            elem = soup.select_one(sel)
            if elem:
                data.price = clean_text(elem.get_text())
                break
        
        # Additional details (for books)
        details = soup.select('#detailBullets_feature_div li, #productDetails_detailBullets_sections1 tr')
        for item in details:
            text = clean_text(item.get_text())
            if text:
                all_text.append(f"DETAIL: {text}")
        
        data.raw_text = '\n'.join(all_text)


# ============== DEEP PRODUCT ANALYZER (GPT) ==============
class DeepProductAnalyzer:
    """
    Uses GPT to deeply analyze the product and extract:
    - Exact product type
    - Educational details (board, class, subject)
    - Competitor search queries specific to the product
    """
    
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    def analyze(self, product_data: ProductData) -> DeepProductAnalysis:
        """Perform deep analysis of the product"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert product analyst. Your job is to DEEPLY analyze products and extract precise details.

For EDUCATIONAL BOOKS, you MUST identify:
- Education board (CBSE, ICSE, State Board)
- Class/Grade level (Class 9, Class 10, etc.)
- Subject (Mathematics, Science, English, etc.)
- Book type (Question Bank, Textbook, Reference Book, Sample Papers, Guide)
- Target exam year

For competitor search, generate HIGHLY SPECIFIC queries that will find products in the EXACT SAME category.

CRITICAL RULES:
1. A "CBSE Class 9 Maths Question Bank" competitor is another "Class 9 Maths Question Bank" - NOT a personal finance book!
2. Competitors for educational books are: Oswaal, Educart, Arihant, MTG, RD Sharma, RS Aggarwal, etc.
3. Be EXTREMELY specific in search queries.

Return ONLY valid JSON."""
            },
            {
                "role": "user",
                "content": f"""Analyze this product DEEPLY:

TITLE: {product_data.title}
BRAND/PUBLISHER: {product_data.brand}
CATEGORY: {product_data.category}
FEATURES: {'; '.join(product_data.features[:10])}
DESCRIPTION: {product_data.description[:800]}
RAW DATA: {product_data.raw_text[:1500]}

Return JSON with this EXACT structure:
{{
    "product_name": "full product name",
    "brand_publisher": "publisher or brand name",
    
    "main_category": "e.g., Educational Books, Electronics, Clothing",
    "sub_category": "e.g., CBSE Question Banks, Wireless Earbuds",
    "product_type": "very specific type",
    
    "is_educational_book": true/false,
    "education_board": "CBSE/ICSE/State Board/NA",
    "grade_class": "Class 9/Class 10/NA",
    "subject": "Mathematics/Science/NA",
    "book_type": "Question Bank/Sample Papers/Reference Book/Textbook/NA",
    "target_exam": "2026 Board Exams/JEE/NEET/NA",
    
    "target_audience": "who would buy this",
    "key_features": ["feature1", "feature2", "feature3"],
    
    "competitor_search_queries": [
        "VERY SPECIFIC search query 1",
        "VERY SPECIFIC search query 2",
        "VERY SPECIFIC search query 3",
        "VERY SPECIFIC search query 4",
        "VERY SPECIFIC search query 5"
    ],
    "competitor_brands": ["Brand1", "Brand2", "Brand3", "Brand4", "Brand5"]
}}

IMPORTANT FOR EDUCATIONAL BOOKS:
- If it's a Class 9 CBSE Maths Question Bank, competitor queries should be:
  - "CBSE Class 9 Mathematics question bank 2026"
  - "best Class 9 Maths practice book CBSE"
  - "Oswaal vs Educart Class 9 Maths"
  - "RD Sharma Class 9 alternative"
- Competitor brands should be: Oswaal, Educart, Arihant, MTG, RD Sharma, RS Aggarwal, etc.

NOT queries like "books similar to..." or "personal finance books"!"""
            }
        ]
        
        try:
            data = self.client.chat_json(messages, temperature=0.2)
            
            return DeepProductAnalysis(
                product_name=data.get('product_name', product_data.title),
                brand_publisher=data.get('brand_publisher', product_data.brand),
                main_category=data.get('main_category', ''),
                sub_category=data.get('sub_category', ''),
                product_type=data.get('product_type', ''),
                education_board=data.get('education_board', ''),
                grade_class=data.get('grade_class', ''),
                subject=data.get('subject', ''),
                book_type=data.get('book_type', ''),
                target_exam=data.get('target_exam', ''),
                target_audience=data.get('target_audience', ''),
                key_features=data.get('key_features', []),
                competitor_search_queries=data.get('competitor_search_queries', []),
                competitor_brands=data.get('competitor_brands', [])
            )
        except Exception as e:
            st.error(f"GPT Analysis failed: {e}")
            return self._fallback_analysis(product_data)
    
    def _fallback_analysis(self, product_data: ProductData) -> DeepProductAnalysis:
        """Rule-based fallback"""
        title_lower = product_data.title.lower()
        
        analysis = DeepProductAnalysis(
            product_name=product_data.title,
            brand_publisher=product_data.brand
        )
        
        # Detect educational book
        edu_indicators = ['cbse', 'icse', 'class 9', 'class 10', 'class 11', 'class 12',
                         'question bank', 'sample paper', 'ncert', 'board exam']
        
        if any(ind in title_lower for ind in edu_indicators):
            analysis.main_category = "Educational Books"
            analysis.sub_category = "Question Banks"
            
            # Detect class
            class_match = re.search(r'class\s*(\d+)', title_lower)
            if class_match:
                analysis.grade_class = f"Class {class_match.group(1)}"
            
            # Detect subject
            subjects = {'math': 'Mathematics', 'science': 'Science', 'english': 'English',
                       'social': 'Social Science', 'hindi': 'Hindi', 'physics': 'Physics',
                       'chemistry': 'Chemistry', 'biology': 'Biology'}
            for key, val in subjects.items():
                if key in title_lower:
                    analysis.subject = val
                    break
            
            # Detect board
            if 'cbse' in title_lower:
                analysis.education_board = 'CBSE'
            elif 'icse' in title_lower:
                analysis.education_board = 'ICSE'
            
            analysis.competitor_brands = ['Oswaal', 'Educart', 'Arihant', 'MTG', 'RD Sharma']
            analysis.competitor_search_queries = [
                f"{analysis.education_board} {analysis.grade_class} {analysis.subject} question bank",
                f"best {analysis.grade_class} {analysis.subject} book {analysis.education_board}",
            ]
        
        return analysis


# ============== KEYWORD EXTRACTOR ==============
class KeywordExtractor:
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    def extract(self, product_data: ProductData, analysis: DeepProductAnalysis) -> KeywordAnalysis:
        """Extract SEO keywords based on deep analysis"""
        
        # Build context based on product type
        if analysis.education_board:
            context = f"""Educational Book:
- Board: {analysis.education_board}
- Class: {analysis.grade_class}
- Subject: {analysis.subject}
- Type: {analysis.book_type}
- Publisher: {analysis.brand_publisher}"""
        else:
            context = f"""Product:
- Type: {analysis.product_type}
- Category: {analysis.main_category}
- Brand: {analysis.brand_publisher}"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an SEO expert. Generate keywords that students/customers would actually search for."
            },
            {
                "role": "user",
                "content": f"""Generate SEO keywords for:

PRODUCT: {analysis.product_name}
{context}

Return JSON:
{{
    "short_tail": ["5 single-word keywords"],
    "mid_tail": ["5 two-word phrases"],
    "long_tail": ["5 three+ word search queries with buying intent"],
    "seo_keywords": ["3 primary SEO keywords to optimize for"]
}}

For educational books, include:
- Class level keywords
- Subject keywords
- Board name
- Book type keywords
- Year/exam keywords"""
            }
        ]
        
        try:
            data = self.client.chat_json(messages)
            return KeywordAnalysis(
                short_tail=data.get('short_tail', [])[:5],
                mid_tail=data.get('mid_tail', [])[:5],
                long_tail=data.get('long_tail', [])[:5],
                seo_keywords=data.get('seo_keywords', [])[:3]
            )
        except:
            return KeywordAnalysis()


# ============== COMPETITOR COMPARISON ==============
class CompetitorComparator:
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    def compare(self, analysis: DeepProductAnalysis, competitors: List[Dict]) -> List[Dict]:
        """Generate detailed comparisons"""
        
        if not competitors:
            return []
        
        competitor_names = [c.get('name', '') for c in competitors[:3]]
        
        messages = [
            {
                "role": "system",
                "content": f"You are an expert in {analysis.main_category}. Compare products accurately."
            },
            {
                "role": "user",
                "content": f"""Compare this product with competitors:

YOUR PRODUCT:
- Name: {analysis.product_name}
- Publisher: {analysis.brand_publisher}
- Type: {analysis.product_type}
- Board: {analysis.education_board}
- Class: {analysis.grade_class}
- Subject: {analysis.subject}

COMPETITORS: {', '.join(competitor_names)}

Return JSON:
{{
    "comparisons": [
        {{
            "competitor": "name",
            "similarities": ["2-3 similarities"],
            "differences": ["2-3 key differences"],
            "your_strength": "main advantage of your product",
            "their_strength": "main advantage of competitor"
        }}
    ]
}}"""
            }
        ]
        
        try:
            data = self.client.chat_json(messages, temperature=0.3)
            return data.get('comparisons', [])
        except:
            return []


# ============== MAIN ANALYZER ==============
class ProductAnalyzer:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAIClient(api_key, model) if api_key else None
        self.scraper = ProductScraper()
        self.deep_analyzer = DeepProductAnalyzer(self.client) if self.client else None
        self.keyword_extractor = KeywordExtractor(self.client) if self.client else None
        self.comparator = CompetitorComparator(self.client) if self.client else None
    
    def analyze(self, url: str, progress_callback=None) -> Dict:
        results = {
            'product_data': None,
            'deep_analysis': None,
            'keywords': None,
            'success': False
        }
        
        # Step 1: Scrape
        if progress_callback:
            progress_callback(0.2, "🔍 Scraping product page...")
        product_data = self.scraper.scrape(url)
        results['product_data'] = product_data
        
        # Step 2: Deep Analysis
        if progress_callback:
            progress_callback(0.5, "🧠 GPT performing deep product analysis...")
        
        if self.deep_analyzer:
            deep_analysis = self.deep_analyzer.analyze(product_data)
        else:
            deep_analysis = DeepProductAnalysis(product_name=product_data.title)
        results['deep_analysis'] = deep_analysis
        
        # Step 3: Keywords
        if progress_callback:
            progress_callback(0.8, "🏷️ Extracting keywords...")
        
        if self.keyword_extractor:
            keywords = self.keyword_extractor.extract(product_data, deep_analysis)
        else:
            keywords = KeywordAnalysis()
        results['keywords'] = keywords
        
        results['success'] = True
        
        if progress_callback:
            progress_callback(1.0, "✅ Analysis complete!")
        
        return results


# ============== STREAMLIT UI ==============
def main():
    st.markdown('''
    <p class="main-header">🎯 AI Product Analyzer <span class="version-badge">v4.0 GPT</span></p>
    ''', unsafe_allow_html=True)
    st.markdown("**Intelligent multi-step analysis with accurate competitor detection**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input("OpenAI API Key", type="password")
        
        model = st.selectbox(
            "GPT Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("""
        ### 🆕 v4 Improvements
        
        ✅ **Deep Analysis** - Extracts exact product type  
        ✅ **Educational Detection** - Board, Class, Subject  
        ✅ **Smart Queries** - Category-specific search  
        ✅ **No Wrong Matches** - Books find books!
        """)
        
        if api_key:
            st.success(f"✅ {model} ready")
        else:
            st.warning("⚠️ Add API key")
    
    # Main input
    url = st.text_input(
        "🔗 Product URL",
        placeholder="https://www.amazon.in/... or https://www.flipkart.com/..."
    )
    
    # Session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'competitors' not in st.session_state:
        st.session_state.competitors = None
    
    # Analyze button
    if st.button("🚀 Analyze Product", type="primary", use_container_width=True):
        if not url:
            st.error("Please enter a URL")
            return
        if not api_key:
            st.error("Please add OpenAI API key")
            return
        
        progress = st.progress(0)
        status = st.empty()
        
        def update(val, text):
            progress.progress(val)
            status.text(text)
        
        analyzer = ProductAnalyzer(api_key, model)
        
        try:
            results = analyzer.analyze(url, update)
            st.session_state.results = results
        except Exception as e:
            st.error(f"Error: {e}")
            return
        finally:
            time.sleep(0.3)
            progress.empty()
            status.empty()
    
    # Display results
    if st.session_state.results:
        results = st.session_state.results
        product = results['product_data']
        analysis = results['deep_analysis']
        keywords = results['keywords']
        
        # Product Overview
        st.markdown('<p class="section-header">📦 Product Identified <span class="gpt-badge">GPT</span></p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Product:** {analysis.product_name}")
            st.markdown(f"**Publisher/Brand:** {analysis.brand_publisher}")
            st.markdown(f"**Category:** {analysis.main_category}")
            st.markdown(f"**Type:** {analysis.product_type}")
        
        with col2:
            if analysis.education_board:
                st.markdown("**📚 Educational Book Details:**")
                st.markdown(f"- **Board:** {analysis.education_board}")
                st.markdown(f"- **Class:** {analysis.grade_class}")
                st.markdown(f"- **Subject:** {analysis.subject}")
                st.markdown(f"- **Book Type:** {analysis.book_type}")
                st.markdown(f"- **Target Exam:** {analysis.target_exam}")
            else:
                st.markdown(f"**Target:** {analysis.target_audience}")
                st.markdown(f"**Price:** {product.price or 'N/A'}")
        
        # Keywords
        st.markdown('<p class="section-header">🏷️ Keywords <span class="gpt-badge">GPT</span></p>', unsafe_allow_html=True)
        
        kw1, kw2, kw3 = st.columns(3)
        
        with kw1:
            st.markdown("**Short-tail**")
            for kw in keywords.short_tail:
                st.markdown(f'<span class="keyword-chip">{kw}</span>', unsafe_allow_html=True)
        
        with kw2:
            st.markdown("**Mid-tail**")
            for kw in keywords.mid_tail:
                st.markdown(f'<span class="keyword-chip-secondary">{kw}</span>', unsafe_allow_html=True)
        
        with kw3:
            st.markdown("**Long-tail**")
            for kw in keywords.long_tail:
                st.markdown(f'<span class="keyword-chip-secondary">{kw}</span>', unsafe_allow_html=True)
        
        # Competitor Search Queries
        st.markdown('<p class="section-header">🔎 Competitor Search Queries</p>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box">
        <strong>✅ Category-Specific Queries</strong><br>
        These queries will find competitors in the same category: <strong>{analysis.sub_category or analysis.main_category}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        for i, query in enumerate(analysis.competitor_search_queries, 1):
            st.code(f"{i}. {query}")
        
        # Known Competitor Brands
        st.markdown("**🏢 Known Competitor Brands:**")
        brands_str = " • ".join(analysis.competitor_brands) if analysis.competitor_brands else "Not identified"
        st.markdown(f"_{brands_str}_")
        
        # Competitor Input Form
        st.markdown('<p class="section-header">📥 Input Competitors Found</p>', unsafe_allow_html=True)
        
        st.markdown("Use the search queries above, then input the competitors you found:")
        
        with st.form("competitor_form"):
            comps = []
            for i in range(3):
                col1, col2 = st.columns([2, 1])
                with col1:
                    name = st.text_input(f"Competitor {i+1}", key=f"c{i}",
                                        placeholder=analysis.competitor_brands[i] if i < len(analysis.competitor_brands) else "")
                with col2:
                    pub = st.text_input(f"Publisher", key=f"p{i}")
                if name:
                    comps.append({'name': name, 'publisher': pub})
            
            if st.form_submit_button("🔄 Analyze Competitors", use_container_width=True):
                st.session_state.competitors = comps
        
        # Show competitor analysis
        if st.session_state.competitors:
            st.markdown('<p class="section-header">🏆 Competitors</p>', unsafe_allow_html=True)
            
            for i, comp in enumerate(st.session_state.competitors):
                st.markdown(f"""
                <div class="competitor-card">
                <strong>#{i+1} {comp['name']}</strong><br>
                <small>Publisher: {comp.get('publisher', 'Unknown')}</small><br>
                <small>Same Category: {analysis.sub_category or analysis.main_category}</small>
                </div>
                """, unsafe_allow_html=True)
            
            # GPT Comparison
            if api_key:
                st.markdown('<p class="section-header">⚖️ Comparison <span class="gpt-badge">GPT</span></p>', unsafe_allow_html=True)
                
                client = OpenAIClient(api_key, model)
                comparator = CompetitorComparator(client)
                
                with st.spinner("Generating comparisons..."):
                    comparisons = comparator.compare(analysis, st.session_state.competitors)
                
                for comp in comparisons:
                    with st.expander(f"📊 vs {comp.get('competitor', 'Unknown')}", expanded=True):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**Similarities:**")
                            for s in comp.get('similarities', []):
                                st.markdown(f"• {s}")
                            st.markdown(f"**Your Strength:** {comp.get('your_strength', '')}")
                        with c2:
                            st.markdown("**Differences:**")
                            for d in comp.get('differences', []):
                                st.markdown(f"• {d}")
                            st.markdown(f"**Their Strength:** {comp.get('their_strength', '')}")
        
        # Export
        st.markdown("---")
        export = {
            'product': {
                'name': analysis.product_name,
                'brand': analysis.brand_publisher,
                'category': analysis.main_category,
                'type': analysis.product_type,
                'education': {
                    'board': analysis.education_board,
                    'class': analysis.grade_class,
                    'subject': analysis.subject,
                    'book_type': analysis.book_type
                }
            },
            'keywords': {
                'short_tail': keywords.short_tail,
                'mid_tail': keywords.mid_tail,
                'long_tail': keywords.long_tail
            },
            'competitor_queries': analysis.competitor_search_queries,
            'competitor_brands': analysis.competitor_brands
        }
        
        st.download_button(
            "📥 Download Analysis",
            json.dumps(export, indent=2),
            "analysis.json",
            "application/json",
            use_container_width=True
        )


if __name__ == "__main__":
    main()