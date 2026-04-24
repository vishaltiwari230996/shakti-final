"""
Product Analyzer Service - AI-powered deep product analysis
Includes: Scraping, Deep Analysis, Keyword Extraction, Competitor Analysis
"""

import json
import re
import requests
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import random

from app.models import (
    ProductData, DeepProductAnalysis, KeywordStrategy,
    ProductIdentity, BrandIdentity, CategoryMapping,
    EducationalDetails, ElectronicsDetails,
    PriceIntelligence, PricingDetails, FeatureArchitecture,
    TargetAudience, Persona, CompetitiveLandscape,
    StrategicInsights, KeywordItem, KeywordCluster
)
from app.services.url_safety import ensure_safe_product_url, safe_get


class ProductScraperService:
    """Scrapes product data from e-commerce platforms"""
    
    @staticmethod
    def get_headers():
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        ]
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        }
    
    @staticmethod
    def detect_platform(url: str) -> str:
        domain = urlparse(url).netloc.lower()
        if 'amazon' in domain:
            return 'amazon'
        elif 'flipkart' in domain:
            return 'flipkart'
        return 'unknown'
    
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    @classmethod
    def scrape(cls, url: str) -> ProductData:
        """Scrape product data from URL"""
        safe_url = ensure_safe_product_url(url)
        platform = cls.detect_platform(safe_url)
        if platform == 'unknown':
            raise ValueError("Only Amazon and Flipkart product URLs are supported.")

        data = ProductData(platform=platform.capitalize(), url=safe_url)
        
        try:
            session = requests.Session()
            if platform == 'amazon':
                try:
                    safe_get('https://www.amazon.in', headers=cls.get_headers(), timeout=10, session=session)
                    time.sleep(0.5)
                except Exception:
                    pass
            
            response = safe_get(safe_url, headers=cls.get_headers(), timeout=20, session=session)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for tag in soup(['script', 'style', 'noscript', 'iframe']):
                tag.decompose()
            
            if platform == 'amazon':
                cls._parse_amazon(soup, data)
            elif platform == 'flipkart':
                cls._parse_flipkart(soup, data)
            else:
                cls._parse_generic(soup, data)
        
        except requests.RequestException as exc:
            raise ValueError(f"Failed to fetch product page: {exc}") from exc
        except Exception:
            cls._extract_from_url(safe_url, data, platform)
            if not data.title:
                raise ValueError("Could not extract product data from this page.")
        
        return data
    
    @staticmethod
    def _parse_amazon(soup: BeautifulSoup, data: ProductData):
        """Parse Amazon product page"""
        all_text = []
        
        # Title
        for sel in ['#productTitle', '#title span', 'h1#title span']:
            elem = soup.select_one(sel)
            if elem and elem.get_text().strip():
                data.title = ProductScraperService.clean_text(elem.get_text())
                all_text.append(f"TITLE: {data.title}")
                break
        
        # Brand
        for sel in ['#bylineInfo', 'a#bylineInfo', '.po-brand .a-span9']:
            elem = soup.select_one(sel)
            if elem and elem.get_text().strip():
                brand = ProductScraperService.clean_text(elem.get_text())
                brand = re.sub(r'(Visit the |Brand:\s*| Store|by\s+)', '', brand, flags=re.I)
                if brand:
                    data.brand = brand.strip()
                    all_text.append(f"BRAND: {data.brand}")
                    break
        
        # Category
        breadcrumbs = soup.select('#wayfinding-breadcrumbs_feature_div a')
        if breadcrumbs:
            cats = [ProductScraperService.clean_text(b.get_text()) for b in breadcrumbs 
                   if ProductScraperService.clean_text(b.get_text())]
            if cats:
                data.category = ' > '.join(cats)
                all_text.append(f"CATEGORY: {data.category}")
        
        # Features
        for f in soup.select('#feature-bullets li span.a-list-item'):
            text = ProductScraperService.clean_text(f.get_text())
            if text and 5 < len(text) < 500:
                data.features.append(text)
                all_text.append(f"FEATURE: {text}")
        
        # Description
        for sel in ['#productDescription p', '#productDescription', '#bookDescription_feature_div span']:
            elems = soup.select(sel)
            for elem in elems:
                text = ProductScraperService.clean_text(elem.get_text())
                if text and len(text) > 20:
                    data.description += ' ' + text[:800]
                    all_text.append(f"DESC: {text[:400]}")
        data.description = data.description.strip()
        
        # Price
        for sel in ['.a-price .a-offscreen', '#priceblock_ourprice', '#corePrice_feature_div .a-price .a-offscreen']:
            elem = soup.select_one(sel)
            if elem:
                data.price = ProductScraperService.clean_text(elem.get_text())
                break
        
        data.raw_text = '\n'.join(all_text)
    
    @staticmethod
    def _parse_flipkart(soup: BeautifulSoup, data: ProductData):
        """Parse Flipkart product page"""
        all_text = []
        
        for sel in ['span.VU-ZEz', 'span.B_NuCI', 'h1 span']:
            elem = soup.select_one(sel)
            if elem and elem.get_text().strip():
                data.title = ProductScraperService.clean_text(elem.get_text())
                all_text.append(f"TITLE: {data.title}")
                break
        
        breadcrumbs = soup.select('div._1MR4o5 a')
        if breadcrumbs:
            cats = [ProductScraperService.clean_text(b.get_text()) for b in breadcrumbs]
            data.category = ' > '.join(cats)
            all_text.append(f"CATEGORY: {data.category}")
        
        for li in soup.select('li._21Ahn-'):
            text = ProductScraperService.clean_text(li.get_text())
            if text:
                data.features.append(text)
                all_text.append(f"FEATURE: {text}")
        
        for sel in ['div.Nx9bqj', 'div._30jeq3']:
            elem = soup.select_one(sel)
            if elem:
                data.price = ProductScraperService.clean_text(elem.get_text())
                break
        
        data.raw_text = '\n'.join(all_text)
    
    @staticmethod
    def _parse_generic(soup: BeautifulSoup, data: ProductData):
        """Generic parser for other websites"""
        for sel in ['h1', '.product-title', '[itemprop="name"]']:
            elem = soup.select_one(sel)
            if elem:
                data.title = ProductScraperService.clean_text(elem.get_text())
                break
        
        paragraphs = soup.select('p')
        desc_parts = [ProductScraperService.clean_text(p.get_text()) 
                     for p in paragraphs[:10] 
                     if len(ProductScraperService.clean_text(p.get_text())) > 30]
        data.description = ' '.join(desc_parts)[:1500]
        data.raw_text = f"TITLE: {data.title}\nDESC: {data.description}"
    
    @staticmethod
    def _extract_from_url(url: str, data: ProductData, platform: str):
        """Extract title from URL if scraping fails"""
        try:
            from urllib.parse import unquote
            decoded = unquote(url)
            if platform == 'amazon':
                match = re.search(r'amazon\.[^/]+/([^/]+)/dp/', decoded)
                if match:
                    data.title = match.group(1).replace('-', ' ').title()
            data.raw_text = f"URL_EXTRACTED: {data.title}"
        except:
            pass


class DeepProductAnalyzerService:
    """AI-powered deep product analysis using LLM"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def _chat(self, messages: List[Dict], temperature: float = 0.3) -> str:
        """Call OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 3000
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _chat_json(self, messages: List[Dict], temperature: float = 0.1) -> Dict:
        """Get JSON response"""
        if messages[0]['role'] == 'system':
            messages[0]['content'] = "IMPORTANT: Respond with ONLY valid JSON. No markdown, no backticks.\n\n" + messages[0]['content']
        else:
            messages.insert(0, {'role': 'system', 'content': 'Respond with ONLY valid JSON. No markdown, no backticks.'})
        
        response = self._chat(messages, temperature=temperature)
        
        # Clean response
        response = response.strip()
        response = re.sub(r'^```json\s*', '', response)
        response = re.sub(r'^```\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
        
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            response = json_match.group(0)
        
        response = re.sub(r',\s*}', '}', response)
        response = re.sub(r',\s*]', ']', response)
        
        try:
            return json.loads(response)
        except:
            return {}
    
    def analyze(self, product_data: ProductData) -> DeepProductAnalysis:
        """Perform deep analysis of product"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert product analyst. Analyze products deeply and return ONLY valid JSON."
            },
            {
                "role": "user",
                "content": f"""Analyze this product DEEPLY and return a JSON object with these exact keys:
                
PRODUCT DATA:
- Title: {product_data.title}
- Brand: {product_data.brand}
- Category: {product_data.category}
- Price: {product_data.price}
- Features: {'; '.join(product_data.features[:5])}
- Description: {product_data.description[:500]}

Return JSON:
{{
    "product_name": "standardized product name",
    "brand": "brand name",
    "main_category": "primary category",
    "sub_category": "secondary category",
    "is_educational": false,
    "price": "{product_data.price}",
    "key_features": ["feature1", "feature2", "feature3"],
    "target_audience": "who would buy this",
    "competitor_search_queries": [
        "specific search query 1",
        "specific search query 2",
        "specific search query 3"
    ],
    "competitor_brands": ["Brand1", "Brand2", "Brand3"]
}}"""
            }
        ]
        
        try:
            data = self._chat_json(messages, temperature=0.2)
            
            analysis = DeepProductAnalysis(
                product_identity=ProductIdentity(
                    standardizedName=data.get('product_name', product_data.title),
                    brand=BrandIdentity(name=data.get('brand', product_data.brand))
                ),
                categoryMapping=CategoryMapping(
                    level1=data.get('main_category', ''),
                    level2=data.get('sub_category', ''),
                    categoryPath=f"{data.get('main_category', '')} > {data.get('sub_category', '')}"
                ),
                priceIntelligence=PriceIntelligence(
                    pricing=PricingDetails(extractedPrice=product_data.price)
                ),
                featureArchitecture=FeatureArchitecture(
                    coreFeatures=[
                        {"name": f, "utility": 8, "uniqueness": 5, "execution": 8}
                        for f in data.get('key_features', [])[:5]
                    ]
                ),
                targetAudience=TargetAudience(
                    primaryPersona=Persona(
                        name="Primary Buyer",
                        demographics={"income": "middle_class"}
                    )
                ),
                competitiveLandscape=CompetitiveLandscape(
                    competitorSearchQueries=data.get('competitor_search_queries', []),
                    competitorBrands={"primary": data.get('competitor_brands', [])}
                ),
                # Backward compatibility
                product_name=data.get('product_name', product_data.title),
                brand_publisher=data.get('brand', product_data.brand),
                main_category=data.get('main_category', ''),
                sub_category=data.get('sub_category', ''),
                key_features=data.get('key_features', []),
                competitor_search_queries=data.get('competitor_search_queries', []),
                competitor_brands=data.get('competitor_brands', [])
            )
            
            return analysis
        except Exception as e:
            # Return minimal analysis on error
            return DeepProductAnalysis(
                product_name=product_data.title,
                brand_publisher=product_data.brand,
                main_category=product_data.category
            )


class KeywordExtractorService:
    """Extract SEO keywords for product"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def _chat_json(self, messages: List[Dict]) -> Dict:
        """Call OpenAI and get JSON"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Clean JSON
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        
        try:
            return json.loads(content)
        except:
            return {}
    
    def extract(self, product_name: str, category: str, brand: str) -> KeywordStrategy:
        """Extract keywords for product"""
        
        messages = [
            {
                "role": "system",
                "content": "Extract SEO keywords. Return ONLY valid JSON."
            },
            {
                "role": "user",
                "content": f"""Extract keywords for this product:
- Name: {product_name}
- Category: {category}
- Brand: {brand}

Return JSON:
{{
    "short_tail": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "mid_tail": ["phrase 1", "phrase 2", "phrase 3", "phrase 4", "phrase 5"],
    "long_tail": ["long phrase 1", "long phrase 2", "long phrase 3", "long phrase 4", "long phrase 5"],
    "seo_keywords": ["primary1", "primary2", "primary3"]
}}"""
            }
        ]
        
        try:
            data = self._chat_json(messages)
            
            return KeywordStrategy(
                short_tail=data.get('short_tail', []),
                mid_tail=data.get('mid_tail', []),
                long_tail=data.get('long_tail', []),
                seo_keywords=data.get('seo_keywords', [])
            )
        except:
            return KeywordStrategy()
