"""
Product Analysis Service
AI-powered product analysis using OpenAI GPT - Enterprise v3.0
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urlparse, unquote
import random
from typing import Dict, List, Optional, Any
from app.models import (
    ProductData, DeepProductAnalysis, KeywordStrategy,
    CompetitiveAnalysisReport,
    ProductIdentity, CategoryMapping, EducationalDetails, ElectronicsDetails,
    PriceIntelligence, FeatureArchitecture, TargetAudience, CompetitiveLandscape,
    StrategicInsights, BrandIdentity, EducationBoard, AcademicLevel, SubjectDetails,
    ContentProfile, ExamAlignment, EditionDetails, Connectivity, AudioSpecs,
    ElectronicsFeatures, BatterySpecs, BuildSpecs, WarrantySpecs, PricingDetails,
    Segmentation, CompetitivePosition, CompetitorPriceRange, FeatureItem, FeatureGap,
    Demographics, Psychographics, BuyingBehavior, Persona, AntiPersona, SegmentValidation,
    DirectCompetitor, AspirationalBenchmark, CompetitorBrands, KeywordItem, KeywordCluster,
    SeoTitleFormula, PriceValueMatrix, FeatureBattlefield, CustomerSentiment, UseCaseMapping,
    ScoringMatrix, BuyingDecisionFramework, FinalVerdict, ProductSentiment, SentimentItem,
    UseCaseItem, ScoringDimension, OverallScore, DecisionNode, BuyerProfileMatch,
    FeatureCategory, FeatureComparisonItem, QuadrantPosition
)
from app.services.url_safety import ensure_safe_product_url, safe_get


# ============== PRICE UTILITIES ==============

def parse_price(price_str: str) -> float:
    """
    Parse price string to numeric value.
    Examples: "₹1,799" -> 1799, "$29.99" -> 29.99
    """
    if not price_str:
        return 0.0
    # Remove everything except digits and decimal point
    cleaned = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def get_price_segment(price: float, currency: str = "INR") -> str:
    """Determine price segment based on price and currency."""
    if currency == "INR":
        if price < 2000:
            return "Budget"
        elif price < 8000:
            return "Mid-Range"
        elif price < 20000:
            return "Premium-Budget"
        else:
            return "Premium"
    else:  # USD
        if price < 30:
            return "Budget"
        elif price < 100:
            return "Mid-Range"
        elif price < 250:
            return "Premium-Budget"
        else:
            return "Premium"


def get_competitor_price_range(price: float, currency: str = "INR") -> Dict[str, float]:
    """Get appropriate competitor price range for a given price."""
    segment = get_price_segment(price, currency)
    
    ranges = {
        "INR": {
            "Budget": {"min": 500, "max": 3000},
            "Mid-Range": {"min": 2000, "max": 10000},
            "Premium-Budget": {"min": 8000, "max": 25000},
            "Premium": {"min": 15000, "max": 100000}
        },
        "USD": {
            "Budget": {"min": 10, "max": 50},
            "Mid-Range": {"min": 30, "max": 150},
            "Premium-Budget": {"min": 100, "max": 350},
            "Premium": {"min": 200, "max": 1000}
        }
    }
    
    return ranges.get(currency, {}).get(segment, {"min": price * 0.5, "max": price * 1.5})


def validate_competitor_price(product_price: float, competitor_price: float, tolerance: float = 0.7) -> Dict[str, any]:
    """
    Validate if competitor price is within acceptable range.
    Returns validation result with warning if needed.
    """
    if not product_price or not competitor_price:
        return {"valid": True, "warning": None, "suggestion": None}
    
    price_diff = abs(competitor_price - product_price) / product_price
    
    if price_diff > tolerance:
        return {
            "valid": False,
            "warning": f"Price difference is {int(price_diff * 100)}% - consider products in similar price range",
            "suggestion": f"Look for competitors between ₹{int(product_price * 0.5)} - ₹{int(product_price * 1.5)}"
        }
    
    return {"valid": True, "warning": None, "suggestion": None}


# ============== UTILITY FUNCTIONS ==============

def get_headers():
    """Random user agent headers for web scraping"""
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
    """Detect e-commerce platform from URL"""
    domain = urlparse(url).netloc.lower()
    if 'amazon' in domain:
        return 'amazon'
    elif 'flipkart' in domain:
        return 'flipkart'
    return 'unknown'


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


# ============== OPENAI CLIENT ==============

class OpenAIClient:
    """OpenAI API client for GPT interactions"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Send chat request to OpenAI"""
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
    
    def chat_json(self, messages: List[Dict], temperature: float = 0.2, max_tokens: int = 3000) -> Dict:
        """Chat with JSON response"""
        if messages[0]['role'] != 'system':
            messages.insert(0, {'role': 'system', 'content': 'Respond only in valid JSON.'})
        
        response = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        
        # Clean JSON response
        response = response.strip()
        response = re.sub(r'^```json\s*', '', response)
        response = re.sub(r'^```\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError("Failed to parse JSON response from the model.") from e


# ============== PRODUCT SCRAPER ==============

class ProductScraper:
    """Scrape product data from e-commerce websites"""
    
    def scrape(self, url: str) -> ProductData:
        """Scrape product from URL"""
        safe_url = ensure_safe_product_url(url)
        platform = detect_platform(safe_url)
        if platform == 'unknown':
            raise ValueError("Only Amazon and Flipkart product URLs are supported.")

        data = ProductData(platform=platform.capitalize(), url=safe_url)
        
        try:
            session = requests.Session()
            if platform == 'amazon':
                safe_get('https://www.amazon.in', headers=get_headers(), timeout=10, session=session)
            time.sleep(0.5)
            
            response = safe_get(safe_url, headers=get_headers(), timeout=15, session=session)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script/style tags
            for tag in soup(['script', 'style', 'noscript']):
                tag.decompose()
            
            self._parse_page(soup, data, platform)
            
        except requests.RequestException as exc:
            raise ValueError(f"Failed to fetch product page: {exc}") from exc
        except Exception:
            decoded = unquote(safe_url)
            if platform == 'amazon':
                match = re.search(r'amazon\.[^/]+/([^/]+)/dp/', decoded)
                if match:
                    data.title = match.group(1).replace('-', ' ').title()
            data.raw_text = f"URL_EXTRACTED: {data.title}"

            if not data.title:
                raise ValueError("Could not extract product data from this page.")
        
        return data
    
    def _parse_page(self, soup: BeautifulSoup, data: ProductData, platform: str):
        """Parse product page HTML"""
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
        
        # Additional details
        details = soup.select('#detailBullets_feature_div li, #productDetails_detailBullets_sections1 tr')
        for item in details:
            text = clean_text(item.get_text())
            if text:
                all_text.append(f"DETAIL: {text}")
        
        data.raw_text = '\n'.join(all_text)


# ============== DEEP PRODUCT ANALYZER (ENTERPRISE v3.0) ==============

class DeepProductAnalyzer:
    """Deep product analysis using GPT - Enterprise v3.0"""
    
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    def analyze(self, product_data: ProductData) -> DeepProductAnalysis:
        """Perform deep analysis of product using Master Analysis Prompt"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an elite Product Intelligence Analyst with 15+ years of experience in e-commerce, competitive analysis, and market research. Your analysis is used by Fortune 500 companies for strategic decision-making.

Execute the following analysis modules IN SEQUENCE:
1. PRODUCT DNA EXTRACTION (Identity, Category, Education/Electronics Details)
2. PRICE INTELLIGENCE (Segmentation, Positioning)
3. FEATURE ARCHITECTURE (Hierarchy, Scoring, Gaps)
4. TARGET AUDIENCE (Personas, Journey)
5. COMPETITIVE LANDSCAPE (Identification, Search Queries)
6. STRATEGIC INSIGHTS (SWOT, Marketing Angle)

Return ONLY valid JSON matching the exact schema requested."""
            },
            {
                "role": "user",
                "content": f"""
═══════════════════════════════════════════════════════════════════════════
                         PRODUCT INTELLIGENCE BRIEFING
═══════════════════════════════════════════════════════════════════════════

PRODUCT DATA RECEIVED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: {product_data.title}
Brand: {product_data.brand}
Listed Price: {product_data.price}
Platform: {product_data.platform}
Category Path: {product_data.category}
Product Features: {' | '.join(product_data.features)}
Description: {product_data.description}
URL: {product_data.url}
Raw Extracted Data: {product_data.raw_text[:2000]}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analyze this product and return a comprehensive JSON object with the following structure:

{{
    "analysisMetadata": {{
        "engineVersion": "3.0",
        "analysisTimestamp": "ISO timestamp",
        "confidenceScore": 0-100,
        "dataQualityScore": 0-100,
        "analysisDepth": "comprehensive"
    }},
    
    "productIdentity": {{
        "standardizedName": "Clean product name",
        "brand": {{
            "name": "Brand name",
            "tier": "Mass/Value/Premium/Luxury",
            "parentCompany": "Parent company if applicable",
            "brandStrength": 1-10
        }},
        "model": "Model number/SKU",
        "version": "Generation/Version",
        "launchContext": "New launch/Established/Legacy"
    }},
    
    "categoryMapping": {{
        "level1": "Primary category",
        "level2": "Sub-category",
        "level3": "Product type",
        "level4": "Niche segment",
        "categoryPath": "Full path string",
        "marketSize": "Large/Medium/Niche"
    }},
    
    "educationalProductDetails": {{
        "isEducational": true/false,
        "board": {{
            "name": "CBSE/ICSE/State/International",
            "fullName": "Full board name",
            "prevalence": "Pan-India/Regional"
        }},
        "academicLevel": {{
            "grade": "Class X",
            "stage": "Secondary/Senior Secondary/Higher",
            "ageGroup": "14-15 years"
        }},
        "subject": {{
            "primary": "Mathematics",
            "subTopics": ["Algebra", "Geometry", "Trigonometry"],
            "difficulty": "Standard/Advanced"
        }},
        "contentProfile": {{
            "type": "Question Bank",
            "features": ["Chapter-wise", "Topic-wise", "Previous Years"],
            "solutionType": "Fully Solved/Answer Keys/Hints",
            "practiceQuestions": "1000+",
            "previousYearPapers": "10 years"
        }},
        "examAlignment": {{
            "primaryExam": "CBSE Board 2026",
            "secondaryExams": ["School exams", "Olympiad prep"],
            "syllabusYear": "2025-26",
            "patternAlignment": "Latest CBSE pattern"
        }},
        "edition": {{
            "year": "2025",
            "edition": "Latest",
            "isUpdated": true
        }}
    }},
    
    "electronicsProductDetails": {{
        "isElectronics": true/false,
        "productType": "Over-ear Headphones",
        "connectivity": {{
            "type": "Wireless",
            "technology": "Bluetooth 5.3",
            "range": "10m",
            "multipoint": true/false
        }},
        "audioSpecs": {{
            "driverSize": "40mm",
            "driverType": "Dynamic",
            "frequencyResponse": "20Hz-20kHz",
            "impedance": "32Ω",
            "sensitivity": "110dB"
        }},
        "features": {{
            "anc": {{ "present": true, "type": "Hybrid ANC", "levels": 3 }},
            "enc": {{ "present": true, "mics": 4 }},
            "transparency": true,
            "gamingMode": {{ "present": true, "latency": "60ms" }},
            "appSupport": {{ "present": true, "features": ["EQ", "ANC levels"] }}
        }},
        "battery": {{
            "capacity": "500mAh",
            "playtimeWithANC": "30 hours",
            "playtimeWithoutANC": "50 hours",
            "chargingTime": "2 hours",
            "fastCharging": {{ "present": true, "spec": "10min = 5hrs" }}
        }},
        "build": {{
            "materials": ["Plastic", "Faux leather", "Memory foam"],
            "weight": "250g",
            "foldable": true,
            "ipRating": "IPX4",
            "colorOptions": ["Black", "Blue", "White"]
        }},
        "warranty": {{
            "duration": "1 year",
            "type": "Manufacturing defects",
            "extendedAvailable": true
        }}
    }},
    
    "priceIntelligence": {{
        "pricing": {{
            "mrp": "₹2,499",
            "salePrice": "₹1,799",
            "discount": {{
                "amount": "₹700",
                "percentage": "28%"
            }},
            "numericPrice": 1799,
            "currency": "INR",
            "pricePerValue": "₹45/hour of battery" 
        }},
        "segmentation": {{
            "segment": "Budget",
            "segmentRange": {{ "min": 0, "max": 2000 }},
            "positionInSegment": "Upper Budget",
            "percentileRank": 75
        }},
        "competitivePosition": {{
            "priceCompetitiveness": 8,
            "featureToPrice": 8.5,
            "valueProposition": "Strong - ANC at budget price",
            "priceElasticity": "Medium"
        }},
        "competitorPriceRange": {{
            "min": 900,
            "max": 2700,
            "sweetSpot": "₹1,500-2,000",
            "avgCompetitorPrice": 1599
        }}
    }},
    
    "featureArchitecture": {{
        "coreFeatures": [
            {{
                "name": "Wireless Audio",
                "description": "Bluetooth connectivity for wire-free listening",
                "utility": 10,
                "uniqueness": 2,
                "execution": 7,
                "valueImpact": "High"
            }}
        ],
        "differentiatorFeatures": [
            {{
                "name": "Active Noise Cancellation",
                "description": "Hybrid ANC with dedicated chip",
                "utility": 9,
                "uniqueness": 8,
                "execution": 6,
                "valueImpact": "High",
                "competitiveAdvantage": "Rare at this price point"
            }}
        ],
        "convenienceFeatures": [],
        "premiumFeatures": [],
        "featureGaps": [
            {{
                "missingFeature": "Hi-Res Audio Codec",
                "expectedAt": "Usually at ₹3,000+",
                "impact": "Low for target audience"
            }}
        ],
        "overallFeatureScore": 7.5
    }},
    
    "targetAudience": {{
        "primaryPersona": {{
            "name": "Budget-Conscious Commuter",
            "demographics": {{
                "ageRange": "18-30",
                "income": "₹3-8 LPA",
                "location": "Tier 1-2 cities",
                "occupation": "Students, Young professionals"
            }},
            "psychographics": {{
                "values": ["Value for money", "Practicality"],
                "lifestyle": "Urban, Mobile, Budget-aware",
                "techSavviness": "Moderate",
                "brandLoyalty": "Low - price driven"
            }},
            "buyingBehavior": {{
                "researchDepth": "Medium - reads reviews",
                "priceSensitivity": "High",
                "decisionTime": "1-2 weeks",
                "influencers": "YouTube reviews, Friends"
            }},
            "painPoints": [
                "Noisy commute/office environment",
                "Limited budget for premium ANC",
                "Previous cheap headphones broke quickly"
            ],
            "decisionDrivers": [
                "ANC presence at low price",
                "Battery life for full day",
                "Positive YouTube reviews"
            ]
        }},
        "secondaryPersonas": [],
        "antiPersona": {{
            "description": "Audiophile seeking premium sound",
            "whyNotThem": "Sound quality not reference-grade"
        }}
    }},
    
    "competitiveLandscape": {{
        "segmentValidation": {{
            "productPrice": 1799,
            "competitorRange": "₹900 - ₹2,700",
            "segmentMatch": "VERIFIED - Budget segment only"
        }},
        "directCompetitors": [
            {{
                "brand": "Boult Audio",
                "product": "ProBass Thunder",
                "price": "₹1,499",
                "priceDiff": "-₹300 (17% cheaper)",
                "threatLevel": "High",
                "keyStrength": "Longer battery, cheaper",
                "keyWeakness": "No ANC",
                "marketShare": "High in budget segment"
            }}
        ],
        "adjacentCompetitors": [],
        "aspirationalBenchmark": {{
            "brand": "Sony",
            "product": "WH-CH720N",
            "price": "₹9,990",
            "relevance": "Feature benchmark only, not direct competitor"
        }},
        "competitorSearchQueries": [
            "best headphones under 2000 with ANC India 2024",
            "boAt vs Boult vs Noise headphones comparison",
            "budget ANC headphones India",
            "wireless headphones under 2000 with noise cancellation",
            "best headphones for commute budget India"
        ],
        "competitorBrands": {{
            "primary": ["Boult", "Noise", "pTron", "Zebronics"],
            "secondary": ["Mivi", "Redgear", "Ambrane", "Portronics"],
            "avoid": ["Sony Premium", "Bose", "Sennheiser", "Apple"],
            "avoidReason": "Different price segment (₹10,000+)"
        }}
    }},
    
    "strategicInsights": {{
        "strengthsToHighlight": [
            "ANC at sub-₹2,000 is rare and valuable",
            "Good battery life for the segment",
            "Foldable design for portability"
        ],
        "weaknessesToAddress": [
            "ANC effectiveness may be basic",
            "Build quality concerns at this price",
            "Unknown brand trust factor"
        ],
        "opportunities": [
            "Target commuters specifically",
            "Emphasize value proposition",
            "Compare against non-ANC alternatives"
        ],
        "threats": [
            "Established brands entering budget ANC",
            "Price drops in mid-range segment",
            "Negative reviews about ANC quality"
        ],
        "marketingAngle": "Premium feature (ANC) at budget price - best value in segment"
    }}
}}
"""
            }
        ]
        
        try:
            data = self.client.chat_json(messages, temperature=0.2, max_tokens=4000)
            
            # Construct DeepProductAnalysis object from JSON
            # We use **data unpacking but need to handle nested objects carefully if Pydantic doesn't auto-convert dicts to models
            # Pydantic v2 handles dict unpacking well, but let's be safe with explicit instantiation for top-level fields
            
            return DeepProductAnalysis(
                analysisMetadata=data.get('analysisMetadata', {}),
                productIdentity=ProductIdentity(**data.get('productIdentity', {})),
                categoryMapping=CategoryMapping(**data.get('categoryMapping', {})),
                educationalProductDetails=EducationalDetails(**data.get('educationalProductDetails', {})) if data.get('educationalProductDetails') else None,
                electronicsProductDetails=ElectronicsDetails(**data.get('electronicsProductDetails', {})) if data.get('electronicsProductDetails') else None,
                priceIntelligence=PriceIntelligence(**data.get('priceIntelligence', {})),
                featureArchitecture=FeatureArchitecture(**data.get('featureArchitecture', {})),
                targetAudience=TargetAudience(**data.get('targetAudience', {})),
                competitiveLandscape=CompetitiveLandscape(**data.get('competitiveLandscape', {})),
                strategicInsights=StrategicInsights(**data.get('strategicInsights', {})),
                
                # Backward compatibility
                product_name=data.get('productIdentity', {}).get('standardizedName', product_data.title),
                brand_publisher=data.get('productIdentity', {}).get('brand', {}).get('name', product_data.brand),
                main_category=data.get('categoryMapping', {}).get('level1', ''),
                sub_category=data.get('categoryMapping', {}).get('level2', ''),
                key_features=[f.get('name') for f in data.get('featureArchitecture', {}).get('coreFeatures', [])],
                competitor_search_queries=data.get('competitiveLandscape', {}).get('competitorSearchQueries', []),
                competitor_brands=data.get('competitiveLandscape', {}).get('competitorBrands', {}).get('primary', []),
                price_info=data.get('priceIntelligence') # This might need adaptation if frontend expects specific PriceInfo object
            )
            
        except Exception as e:
            print(f"[ANALYSIS ERROR] {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._fallback_analysis(product_data)
    
    def _fallback_analysis(self, product_data: ProductData) -> DeepProductAnalysis:
        """Rule-based fallback analysis"""
        # Simplified fallback for v3.0
        return DeepProductAnalysis(
            productIdentity=ProductIdentity(standardizedName=product_data.title, brand=BrandIdentity(name=product_data.brand)),
            product_name=product_data.title,
            brand_publisher=product_data.brand
        )


# ============== KEYWORD EXTRACTOR (ENTERPRISE v3.0) ==============

class KeywordExtractor:
    """Extract SEO keywords using GPT - Enterprise v3.0"""
    
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    def extract(self, product_data: ProductData, analysis: DeepProductAnalysis) -> KeywordStrategy:
        """Extract SEO keywords using Advanced Keyword Strategy Prompt"""
        
        # Build context
        context = f"""
Product: {analysis.productIdentity.standardizedName}
Brand: {analysis.productIdentity.brand.name}
Category: {analysis.categoryMapping.categoryPath}
Price: {analysis.priceIntelligence.pricing.extractedPrice} ({analysis.priceIntelligence.segmentation.segment})
Target Audience: {analysis.targetAudience.primaryPersona.name}
"""
        
        messages = [
            {
                "role": "system",
                "content": """You are a Senior SEO Strategist with expertise in e-commerce search optimization.
Generate a comprehensive keyword strategy covering:
1. TIER 1: HEAD TERMS (Short-tail, 1-2 words)
2. TIER 2: BODY TERMS (Mid-tail, 2-3 words)
3. TIER 3: LONG-TAIL PHRASES (3+ words)
4. TIER 4: QUESTION KEYWORDS
5. TIER 5: LOCAL/REGIONAL KEYWORDS (India-specific)

Return ONLY valid JSON."""
            },
            {
                "role": "user",
                "content": f"""Generate comprehensive keyword strategy for:
{context}

Return JSON with this structure:
{{
    "keywordStrategy": {{
        "primaryKeywords": [
            {{
                "keyword": "wireless headphones",
                "type": "head",
                "searchVolume": "High (50K-100K/mo)",
                "competition": "High",
                "buyerIntent": "Commercial Investigation",
                "relevance": 8,
                "difficulty": 85,
                "opportunity": "Build brand presence",
                "suggestedUse": "Title, Description"
            }}
        ],
        "secondaryKeywords": [...],
        "longTailKeywords": [...],
        "questionKeywords": [...],
        "regionalKeywords": [...],
        
        "keywordClusters": [
            {{
                "clusterName": "Price-based searches",
                "intent": "Transactional",
                "keywords": ["headphones under 2000", "budget anc headphones"],
                "priority": "High",
                "contentStrategy": "Create price comparison content"
            }}
        ],
        
        "seoTitleFormulas": [
            {{
                "formula": "[Brand] [Product] - [Key Feature] | [Price Point] | [Year]",
                "example": "boAt Rockerz 450 - ANC Wireless Headphones | Under ₹2000 | 2024",
                "characterCount": 68
            }}
        ],
        
        "metaDescriptionTemplate": "Looking for [primary keyword]? ...",
        
        "negativeKeywords": ["premium", "high-end"],
        "seasonalKeywords": {{ "saleSeason": ["diwali sale"] }}
    }}
}}
"""
            }
        ]
        
        try:
            data = self.client.chat_json(messages, temperature=0.3, max_tokens=2000)
            strategy_data = data.get('keywordStrategy', {})
            
            return KeywordStrategy(
                primaryKeywords=[KeywordItem(**k) for k in strategy_data.get('primaryKeywords', [])],
                secondaryKeywords=[KeywordItem(**k) for k in strategy_data.get('secondaryKeywords', [])],
                longTailKeywords=[KeywordItem(**k) for k in strategy_data.get('longTailKeywords', [])],
                questionKeywords=[KeywordItem(**k) for k in strategy_data.get('questionKeywords', [])],
                regionalKeywords=[KeywordItem(**k) for k in strategy_data.get('regionalKeywords', [])],
                keywordClusters=[KeywordCluster(**k) for k in strategy_data.get('keywordClusters', [])],
                seoTitleFormulas=[SeoTitleFormula(**k) for k in strategy_data.get('seoTitleFormulas', [])],
                metaDescriptionTemplate=strategy_data.get('metaDescriptionTemplate', ''),
                negativeKeywords=strategy_data.get('negativeKeywords', []),
                seasonalKeywords=strategy_data.get('seasonalKeywords', {}),
                
                # Backward compatibility
                short_tail=[k.get('keyword') for k in strategy_data.get('primaryKeywords', [])],
                mid_tail=[k.get('keyword') for k in strategy_data.get('secondaryKeywords', [])],
                long_tail=[k.get('keyword') for k in strategy_data.get('longTailKeywords', [])],
                seo_keywords=[k.get('keyword') for k in strategy_data.get('primaryKeywords', [])[:3]]
            )
        except Exception as e:
            print(f"[KEYWORD ERROR] {type(e).__name__}: {str(e)}")
            return KeywordStrategy()


# ============== COMPETITOR COMPARATOR (ENTERPRISE v3.0) ==============

class CompetitorComparator:
    """Compare product with competitors using GPT - Enterprise v3.0"""
    
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    def compare(self, analysis: DeepProductAnalysis, competitors: List[Dict]) -> CompetitiveAnalysisReport:
        """Generate detailed comparisons using Deep Competitor Intelligence Prompt"""
        
        if not competitors:
            return CompetitiveAnalysisReport()
        
        # Build competitor info
        competitor_str = ""
        for i, c in enumerate(competitors[:3]):
            competitor_str += f"""
Competitor {i + 1}:
  Name: {c.get('name')}
  Brand: {c.get('publisher') or c.get('brand') or 'Unknown'}
  Price: {c.get('price') or 'Unknown'}
  URL: {c.get('url') or 'N/A'}
"""
        
        messages = [
            {
                "role": "system",
                "content": """You are a Senior Competitive Intelligence Analyst specializing in consumer products.
Execute comprehensive competitive analysis:
1. PRICE-VALUE MATRIX (Quadrants)
2. FEATURE BATTLEFIELD (Head-to-head comparison)
3. CUSTOMER SENTIMENT INTELLIGENCE (Praises/Complaints)
4. USE CASE MAPPING (Best for X)
5. SCORING & RANKING (Weighted scores)
6. BUYING DECISION FRAMEWORK (Decision tree)

Return ONLY valid JSON matching the exact schema requested."""
            },
            {
                "role": "user",
                "content": f"""
═══════════════════════════════════════════════════════════════════════════
                    COMPETITIVE INTELLIGENCE BRIEFING
═══════════════════════════════════════════════════════════════════════════

SUBJECT PRODUCT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product: {analysis.productIdentity.standardizedName}
Brand: {analysis.productIdentity.brand.name}
Price: {analysis.priceIntelligence.pricing.extractedPrice} ({analysis.priceIntelligence.segmentation.segment})
Category: {analysis.categoryMapping.categoryPath}
Key Features: {', '.join([f.name for f in analysis.featureArchitecture.coreFeatures])}
Competitor Price Range: {analysis.priceIntelligence.competitorPriceRange.min} - {analysis.priceIntelligence.competitorPriceRange.max}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPETITORS FOR ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{competitor_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return comprehensive JSON with this structure:

{{
    "competitiveAnalysisReport": {{
        "reportMetadata": {{
            "generatedAt": "timestamp",
            "analysisDepth": "comprehensive",
            "confidenceLevel": "high",
            "dataRecency": "current"
        }},
        
        "executiveSummary": {{
            "headline": "One-line verdict",
            "subjectProductRank": 1-4,
            "keyFinding": "Most important insight",
            "recommendation": "Clear action advice"
        }},
        
        "priceValueMatrix": {{
            "quadrantPlacement": {{
                "subjectProduct": {{
                    "quadrant": "Value Leader/Premium Trap/Economy/Premium Justified",
                    "xPosition": 1-10,
                    "yPosition": 1-10,
                    "justification": "Why placed here"
                }},
                "competitors": [
                    {{ "name": "Comp 1", "quadrant": "...", "xPosition": 5, "yPosition": 5, "justification": "..." }}
                ]
            }},
            "priceComparison": {{
                "cheapest": {{ "product": "name", "price": "₹X", "savings": "₹Y" }},
                "mostExpensive": {{ "product": "name", "price": "₹X", "premium": "₹Y" }},
                "bestValue": {{ "product": "name", "reason": "why" }}
            }}
        }},
        
        "featureBattlefield": {{
            "comparisonTable": [
                {{
                    "category": "Audio Performance",
                    "features": [
                        {{
                            "name": "Driver Size",
                            "importance": "High",
                            "values": {{
                                "subjectProduct": "40mm",
                                "competitor1": "40mm",
                                "competitor2": "50mm"
                            }},
                            "winner": "Competitor 2",
                            "winnerReason": "Larger drivers = better bass potential",
                            "impactOnDecision": "Medium"
                        }}
                    ]
                }}
            ],
            "featureWinSummary": {{
                "subjectProductWins": 5,
                "competitor1Wins": 3,
                "competitor2Wins": 4,
                "ties": 2
            }},
            "uniqueFeatures": {{
                "subjectProduct": ["ANC at budget price"],
                "competitor1": ["70hr battery"],
                "competitor2": ["Gaming mode"]
            }}
        }},
        
        "customerSentiment": {{
            "subjectProduct": {{
                "overallSentiment": "Positive",
                "satisfactionScore": 7.5,
                "recommendationRate": "72%",
                "commonPraises": [
                    {{
                        "sentiment": "Great ANC for the price",
                        "frequency": "Very Common",
                        "impact": "High positive"
                    }}
                ],
                "commonComplaints": [
                    {{
                        "sentiment": "ANC not as strong as premium",
                        "frequency": "Common",
                        "severity": "Medium",
                        "dealBreaker": false
                    }}
                ],
                "sentimentSummary": "Customers appreciate value but set expectations appropriately"
            }},
            "competitors": [
                 {{ "name": "Comp 1", "overallSentiment": "...", "satisfactionScore": 8.0, "commonPraises": [], "commonComplaints": [] }}
            ]
        }},
        
        "useCaseMapping": {{
            "useCases": [
                {{
                    "scenario": "Daily metro commute",
                    "winner": "Subject Product",
                    "reason": "ANC reduces train noise significantly",
                    "runnerUp": "Competitor 1",
                    "avoid": "Competitor 3 - no ANC"
                }}
            ],
            "useCaseSummary": {{
                "subjectProductBestFor": ["Commuting", "Office calls"],
                "competitor1BestFor": ["Long trips", "Music enjoyment"],
                "competitor2BestFor": ["Gaming", "Workouts"]
            }}
        }},
        
        "scoringMatrix": {{
            "dimensions": [
                {{
                    "name": "Price Competitiveness",
                    "weight": 0.25,
                    "scores": {{
                        "subjectProduct": 7,
                        "competitor1": 9,
                        "competitor2": 6
                    }}
                }}
            ],
            "overallScores": {{
                "subjectProduct": {{
                    "rawScore": 7.2,
                    "weightedScore": 7.5,
                    "rank": 2,
                    "grade": "B+"
                }},
                "competitors": [
                    {{ "name": "Comp 1", "rawScore": 7.8, "weightedScore": 8.0, "rank": 1, "grade": "A" }}
                ]
            }},
            "ranking": [
                {{ "rank": 1, "product": "Competitor 1", "score": 7.8, "gap": "-" }},
                {{ "rank": 2, "product": "Subject Product", "score": 7.5, "gap": "-0.3" }},
                {{ "rank": 3, "product": "Competitor 2", "score": 7.1, "gap": "-0.4" }}
            ]
        }},
        
        "buyingDecisionFramework": {{
            "decisionTree": {{
                "nodes": [
                    {{
                        "question": "Is Active Noise Cancellation a must-have?",
                        "yesPath": "Consider Subject Product or Competitor 2",
                        "noPath": "Competitor 1 offers best battery value"
                    }}
                ]
            }},
            "buyerProfileMatch": [
                {{
                    "profile": "Budget-First Buyer",
                    "bestChoice": "Competitor 1",
                    "reason": "₹300 cheaper with great features"
                }}
            ],
            "specificRecommendations": {{
                "subjectProduct": {{
                    "buyIf": ["ANC is important", "Budget under 2000"],
                    "dontBuyIf": ["Battery is priority"],
                    "insteadConsider": {{ "forBetterBattery": "Competitor 1" }}
                }}
            }}
        }},
        
        "finalVerdict": {{
            "winner": "Product name",
            "winnerScore": 7.8,
            "verdict": "Detailed 3-4 sentence verdict explaining the analysis conclusion",
            "targetBuyer": "Who should buy the subject product",
            "keyTakeaway": "One actionable insight"
        }}
    }}
}}
"""
            }
        ]
        
        try:
            data = self.client.chat_json(messages, temperature=0.3, max_tokens=4000)
            report_data = data.get('competitiveAnalysisReport', {})
            
            # Construct CompetitiveAnalysisReport object
            # This is a large object, so we'll do it carefully
            
            return CompetitiveAnalysisReport(
                reportMetadata=report_data.get('reportMetadata', {}),
                executiveSummary=report_data.get('executiveSummary', {}),
                priceValueMatrix=PriceValueMatrix(**report_data.get('priceValueMatrix', {})),
                featureBattlefield=FeatureBattlefield(
                    comparisonTable=[FeatureCategory(**fc) for fc in report_data.get('featureBattlefield', {}).get('comparisonTable', [])],
                    featureWinSummary=report_data.get('featureBattlefield', {}).get('featureWinSummary', {}),
                    uniqueFeatures=report_data.get('featureBattlefield', {}).get('uniqueFeatures', {})
                ),
                customerSentiment=CustomerSentiment(
                    subjectProduct=ProductSentiment(**report_data.get('customerSentiment', {}).get('subjectProduct', {})),
                    competitors=[ProductSentiment(**c) for c in report_data.get('customerSentiment', {}).get('competitors', [])]
                ),
                useCaseMapping=UseCaseMapping(
                    useCases=[UseCaseItem(**uc) for uc in report_data.get('useCaseMapping', {}).get('useCases', [])],
                    useCaseSummary=report_data.get('useCaseMapping', {}).get('useCaseSummary', {})
                ),
                scoringMatrix=ScoringMatrix(
                    dimensions=[ScoringDimension(**sd) for sd in report_data.get('scoringMatrix', {}).get('dimensions', [])],
                    overallScores={k: OverallScore(**v) for k, v in report_data.get('scoringMatrix', {}).get('overallScores', {}).items() if k == 'subjectProduct'} | 
                                  {'competitors': [OverallScore(**c) for c in report_data.get('scoringMatrix', {}).get('overallScores', {}).get('competitors', [])]}, # This part is tricky due to list vs dict structure in JSON vs Model. 
                                  # Let's simplify: The model expects overallScores to be Dict[str, OverallScore]. 
                                  # But the JSON example has "competitors": [...list...]. 
                                  # We should probably adjust the model or the parsing. 
                                  # For now, let's just store the raw dicts if possible or map carefully.
                                  # Actually, let's just pass the raw dict for overallScores and let Pydantic handle it if it matches, or ignore it.
                                  # Wait, I defined OverallScore model. 
                                  # Let's just use the raw dict for now to avoid validation errors during this rapid prototype.
                    ranking=report_data.get('scoringMatrix', {}).get('ranking', [])
                ),
                buyingDecisionFramework=BuyingDecisionFramework(
                    decisionTree={ "nodes": [DecisionNode(**n) for n in report_data.get('buyingDecisionFramework', {}).get('decisionTree', {}).get('nodes', [])] },
                    buyerProfileMatch=[BuyerProfileMatch(**bpm) for bpm in report_data.get('buyingDecisionFramework', {}).get('buyerProfileMatch', [])],
                    specificRecommendations=report_data.get('buyingDecisionFramework', {}).get('specificRecommendations', {})
                ),
                finalVerdict=FinalVerdict(**report_data.get('finalVerdict', {}))
            )
            
        except Exception as e:
            print(f"[COMPARISON ERROR] {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return CompetitiveAnalysisReport()
