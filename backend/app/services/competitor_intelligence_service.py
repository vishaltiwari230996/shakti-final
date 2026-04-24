"""
Intelligent Competitor Intelligence Service
Automatically identifies competitors and provides detailed analysis
"""

import requests
import json
from typing import Dict, List, Optional, Any
from app.models import (
    DirectCompetitor, CompetitorBrands, DeepProductAnalysis, ProductData
)


class CompetitorIntelligenceService:
    """Intelligently identify and analyze competitors"""
    
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
    
    def identify_competitors(
        self,
        product_data: ProductData,
        analysis: DeepProductAnalysis
    ) -> Dict[str, Any]:
        """
        Intelligently identify direct competitors based on product analysis
        Returns competitor information with key strengths and weaknesses
        """
        
        # Build context about the product
        context = f"""
PRODUCT BEING ANALYZED:
Name: {analysis.product_name}
Brand: {analysis.brand_publisher}
Category: {analysis.main_category} > {analysis.sub_category}
Price: {analysis.price_info.get('extractedPrice', 'N/A') if analysis.price_info else 'N/A'}
Key Features: {', '.join(analysis.key_features[:5]) if analysis.key_features else 'N/A'}
Target Market: {analysis.competitor_search_queries[0] if analysis.competitor_search_queries else 'General market'}
"""

        # Prompt to identify competitors
        messages = [
            {
                "role": "system",
                "content": """You are an expert market researcher specializing in e-commerce competitive intelligence. 
Your task is to identify the top 5 direct competitors for the given product and analyze their strengths and weaknesses 
compared to the subject product. Be specific, realistic, and based on actual market knowledge."""
            },
            {
                "role": "user",
                "content": f"""{context}

Based on this product analysis, please:

1. IDENTIFY TOP 5 DIRECT COMPETITORS
   For each competitor, provide:
   - Exact brand and product name
   - Approximate price range (in INR for Indian products)
   - Market availability (Amazon, Flipkart, etc.)

2. FOR EACH COMPETITOR, ANALYZE:
   - Key Strength (what they do better than the subject product)
   - Key Weakness (what the subject product does better)
   - Threat Level (High/Medium/Low) based on feature parity and price
   - Target Segment they focus on
   - Why customers choose them over alternatives

3. MARKET POSITIONING:
   - Where the subject product stands vs competitors
   - Price-to-feature value proposition
   - Market opportunities

Return ONLY valid JSON in this format:
{{
    "competitors": [
        {{
            "rank": 1,
            "brand": "Brand Name",
            "product_name": "Product Name",
            "price_range": "₹XXX - ₹YYY",
            "availability": "Amazon, Flipkart",
            "key_strength": "What they excel at (specific feature/benefit)",
            "key_weakness": "What subject product does better",
            "threat_level": "High/Medium/Low",
            "threat_reason": "Why they are a threat (or not)",
            "target_segment": "Who buys this competitor",
            "market_share_estimate": "Low/Medium/High",
            "comparison_to_subject": {{
                "price_difference": "Cheaper by ₹XXX or More expensive",
                "feature_parity": "Similar/Better/Worse",
                "brand_strength": "Established/Growing/Niche",
                "key_differentiator": "What makes them unique"
            }},
            "customer_preference_reason": "Why customers choose this over alternatives"
        }}
    ],
    "market_analysis": {{
        "subject_product_position": "Leader/Strong contender/Challenger/Niche player",
        "competitive_intensity": "Low/Medium/High",
        "market_gaps": ["Opportunity 1", "Opportunity 2"],
        "threats_to_subject": ["Threat 1", "Threat 2"],
        "key_success_factors": ["Factor 1", "Factor 2"],
        "price_positioning": "Premium/Mid-range/Budget",
        "recommendation": "Strategic positioning advice for subject product"
    }}
}}
"""
            }
        ]
        
        try:
            response = self.chat(messages, temperature=0.3, max_tokens=3000)
            
            # Clean JSON response
            response = response.strip()
            response = response.replace('```json', '').replace('```', '')
            
            data = json.loads(response)
            return data
            
        except Exception as e:
            print(f"[COMPETITOR ANALYSIS ERROR] {type(e).__name__}: {str(e)}")
            return self._fallback_competitors(analysis)
    
    def _fallback_competitors(self, analysis: DeepProductAnalysis) -> Dict[str, Any]:
        """Provide fallback competitor data based on keywords"""
        return {
            "competitors": [
                {
                    "rank": 1,
                    "brand": "Market Leader",
                    "product_name": "Premium Variant",
                    "price_range": "Higher",
                    "key_strength": "Brand recognition and features",
                    "key_weakness": "Higher price point",
                    "threat_level": "Medium",
                    "target_segment": "Premium segment"
                }
            ],
            "market_analysis": {
                "subject_product_position": "Emerging",
                "competitive_intensity": "Medium",
                "market_gaps": ["Value segment", "Feature-rich budget options"],
                "recommendation": "Focus on unique differentiators"
            }
        }
    
    def get_competitor_comparison(
        self,
        analysis: DeepProductAnalysis,
        competitor_names: List[str]
    ) -> Dict[str, Any]:
        """
        Get detailed comparison between subject product and specified competitors
        """
        
        context = f"""
SUBJECT PRODUCT:
Name: {analysis.product_name}
Brand: {analysis.brand_publisher}
Category: {analysis.main_category}
Price: {analysis.price_info.get('extractedPrice', 'N/A') if analysis.price_info else 'N/A'}
Key Features: {', '.join(analysis.key_features[:5]) if analysis.key_features else 'N/A'}

COMPETITORS TO COMPARE WITH:
{', '.join(competitor_names)}
"""

        messages = [
            {
                "role": "system",
                "content": """You are an expert competitive analyst. Provide detailed feature-by-feature 
and price-by-price comparisons between the subject product and competitors. Be factual and balanced."""
            },
            {
                "role": "user",
                "content": f"""{context}

Create a detailed competitive comparison table showing:

1. FEATURE COMPARISON
   For each key category (Price, Performance, Design, Features, Warranty):
   - Subject product rating (1-10)
   - Each competitor rating (1-10)
   - Winner and why

2. PRICE ANALYSIS
   - Price positioning of each product
   - Value for money score (1-10)
   - Best value product

3. BUYING SCENARIOS
   - Which product is best for: Budget buyer, Performance seeker, Brand loyalist, etc.
   - When to choose subject product vs competitors

4. OVERALL VERDICT
   - Strengths of subject product
   - Weaknesses vs competitors
   - Recommendation for different buyer types

Return ONLY valid JSON.
"""
            }
        ]
        
        try:
            response = self.chat(messages, temperature=0.3, max_tokens=2500)
            
            response = response.strip()
            response = response.replace('```json', '').replace('```', '')
            
            data = json.loads(response)
            return data
            
        except Exception as e:
            print(f"[COMPARISON ERROR] {type(e).__name__}: {str(e)}")
            return {"error": f"Failed to generate comparison: {str(e)}"}
    
    def analyze_competitive_threats(
        self,
        analysis: DeepProductAnalysis,
        top_competitors: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Analyze threats and opportunities in the competitive landscape
        """
        
        competitors_str = "\n".join([
            f"- {c.get('brand', 'Unknown')}: {c.get('key_strength', 'N/A')}"
            for c in top_competitors[:5]
        ])
        
        messages = [
            {
                "role": "system",
                "content": """You are a strategic business analyst. Analyze competitive threats and market opportunities."""
            },
            {
                "role": "user",
                "content": f"""
SUBJECT PRODUCT: {analysis.product_name} by {analysis.brand_publisher}

TOP COMPETITORS:
{competitors_str}

Provide strategic analysis on:
1. Immediate threats from competitors
2. Market opportunities for subject product
3. Recommended strategy to win market share
4. Key differentiators to emphasize
5. Pricing strategy recommendation

Return as JSON with threat_analysis and opportunity_analysis sections.
"""
            }
        ]
        
        try:
            response = self.chat(messages, temperature=0.4, max_tokens=2000)
            
            response = response.strip()
            response = response.replace('```json', '').replace('```', '')
            
            data = json.loads(response)
            return data
            
        except Exception as e:
            print(f"[THREAT ANALYSIS ERROR] {type(e).__name__}: {str(e)}")
            return {"error": "Failed to analyze competitive threats"}
