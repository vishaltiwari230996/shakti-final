# Intelligent Competitor Analysis Feature

## Overview

The intelligent competitor analysis feature automatically identifies direct competitors for the analyzed product and provides detailed competitive intelligence including:

- **Competitor Identification**: Automatically identifies top 5 direct competitors
- **Key Strengths**: What each competitor excels at
- **Comparative Analysis**: How they compare to your product
- **Threat Assessment**: Level of competitive threat
- **Market Positioning**: Where your product stands in the market
- **Strategic Recommendations**: Actionable insights for market positioning

## How It Works

### Architecture

```
User enters Product URL
    ↓
Backend analyzes product
    ↓
ProductAnalyzerService creates detailed product profile
    ↓
CompetitorIntelligenceService identifies competitors
    ↓
Returns competitor data with strengths, weaknesses, threats
    ↓
Frontend displays intelligent competitor comparison
```

### File Structure

**Backend Files**:

1. **`backend/app/services/competitor_intelligence_service.py`** (NEW)
   - `CompetitorIntelligenceService` class
   - Methods:
     - `identify_competitors()` - Automatically find competitors
     - `get_competitor_comparison()` - Detailed feature comparison
     - `analyze_competitive_threats()` - Threat & opportunity analysis

2. **`backend/app/api/routes.py`** (UPDATED)
   - `/product-analysis/analyze` - Now includes automatic competitor identification
   - `/product-analysis/identify-competitors` - Manual competitor identification endpoint
   - `/product-analysis/compare-with-competitors` - Detailed comparison endpoint

3. **`backend/app/models.py`** (UPDATED)
   - `ProductAnalysisResponse` - Now includes `competitor_analysis` field

**Frontend Files**:

1. **`frontend/src/pages/ProductAnalysis.jsx`** (UPDATED)
   - New "Intelligent Competitor Analysis" section
   - Displays competitor ranking and threat levels
   - Shows key strengths and comparative advantages
   - Market analysis and strategic recommendations

## Competitor Data Structure

Each competitor includes:

```json
{
  "rank": 1,
  "brand": "Brand Name",
  "product_name": "Product Name",
  "price_range": "₹XXX - ₹YYY",
  "availability": "Amazon, Flipkart",
  "key_strength": "What they excel at",
  "key_weakness": "What your product does better",
  "threat_level": "High/Medium/Low",
  "threat_reason": "Why they are/aren't a threat",
  "target_segment": "Who buys this competitor",
  "market_share_estimate": "Low/Medium/High",
  "comparison_to_subject": {
    "price_difference": "Cheaper by ₹XXX",
    "feature_parity": "Similar/Better/Worse",
    "brand_strength": "Established/Growing/Niche",
    "key_differentiator": "What makes them unique"
  },
  "customer_preference_reason": "Why customers choose this"
}
```

## Market Analysis Data

```json
{
  "subject_product_position": "Leader/Strong contender/Challenger/Niche player",
  "competitive_intensity": "Low/Medium/High",
  "market_gaps": ["Opportunity 1", "Opportunity 2"],
  "threats_to_subject": ["Threat 1", "Threat 2"],
  "key_success_factors": ["Factor 1", "Factor 2"],
  "price_positioning": "Premium/Mid-range/Budget",
  "recommendation": "Strategic positioning advice"
}
```

## API Endpoints

### 1. Analyze Product (with Auto Competitor Identification)
```
POST /api/product-analysis/analyze
Content-Type: application/json

{
  "url": "https://www.amazon.in/dp/...",
  "api_key": "sk-...",
  "model": "gpt-4o-mini"
}

Response includes:
- product_data
- deep_analysis
- keywords
- competitor_analysis (NEW!)
```

### 2. Identify Competitors (Manual)
```
POST /api/product-analysis/identify-competitors
Content-Type: application/json

{
  "api_key": "sk-...",
  "model": "gpt-4o-mini",
  "analysis": { deep_analysis_object },
  "product_data": { product_data_object }
}

Response:
{
  "success": true,
  "competitor_analysis": {
    "competitors": [...],
    "market_analysis": {...}
  }
}
```

### 3. Compare with Specific Competitors
```
POST /api/product-analysis/compare-with-competitors
Content-Type: application/json

{
  "api_key": "sk-...",
  "model": "gpt-4o-mini",
  "analysis": { deep_analysis_object },
  "competitor_names": ["Competitor 1", "Competitor 2", "Competitor 3"]
}

Response:
{
  "success": true,
  "comparison": {
    "feature_comparison": {...},
    "price_analysis": {...},
    "buying_scenarios": [...],
    "overall_verdict": {...}
  }
}
```

## Frontend Display

The intelligent competitor analysis is displayed in the results panel with:

1. **Competitor Card** (for each competitor)
   - Rank and brand name
   - Threat level indicator (color-coded)
   - Price range and availability
   - Key strength (what they do better)
   - Your advantage (what you do better)
   - Why customers choose them

2. **Market Analysis Section**
   - Your market position
   - Competitive intensity
   - Market opportunities
   - Strategic recommendations

## Key Features

### Intelligence Features

1. **Automatic Identification**
   - Uses product category, price, features, target audience
   - Identifies realistic market competitors
   - Validates competitor relevance

2. **Threat Assessment**
   - Evaluates competitive threat level
   - Analyzes price-to-feature ratio
   - Considers brand strength

3. **Market Positioning**
   - Determines subject product's market position
   - Identifies competitive gaps
   - Suggests strategic positioning

4. **Comparative Analysis**
   - Feature-by-feature comparison
   - Price analysis and value assessment
   - Customer preference analysis

### UI/UX Features

1. **Color-Coded Threat Levels**
   - Red: High threat
   - Orange: Medium threat
   - Green: Low threat

2. **Organized Information Display**
   - Rank-based ordering
   - Key information highlighted
   - Strategic insights summarized

3. **Market Analysis Summary**
   - One-line market position
   - Competitive intensity indicator
   - Actionable recommendations

## Usage Examples

### Example 1: Analyzing a Smartphone

```
Input: Amazon smartphone URL

Analysis identifies:
- OnePlus (Strong camera competitor)
- Realme (Better battery life)
- Samsung (Brand advantage)
- Motorola (Value competitor)
- Xiaomi (Feature-rich budget option)

Output: Detailed comparison showing:
- Which competitors are threats
- What your product does better
- Where market opportunities exist
```

### Example 2: Analyzing a Headphone

```
Input: Flipkart headphone URL

Analysis identifies:
- Sony (Audio quality leader)
- Boat (Budget competitor)
- Noise (Feature-rich budget)
- Sennheiser (Premium competitor)
- JBL (Balance competitor)

Output: Shows:
- Audio quality comparison
- Price positioning
- Feature advantages
- Target segment analysis
```

## Customization & Extension

### Adding Custom Competitor Identification Logic

Edit `CompetitorIntelligenceService.identify_competitors()`:

```python
# Add custom filters
if category in ['Electronics', 'Smartphones']:
    # Apply electronics-specific logic
    pass

# Add fallback logic
if len(competitors) < 3:
    # Add more competitors based on price/category
    pass
```

### Modifying Competitor Prompt

Edit the system prompt in `identify_competitors()` to:
- Focus on specific aspects
- Change competitor count
- Adjust evaluation criteria

### Adding More Analysis Dimensions

Extend the JSON schema to include:
- Supply chain analysis
- Retail availability
- Customer reviews sentiment
- Social media presence

## Performance Considerations

**API Calls**: 
- 1 call to identify competitors
- 1 additional call per competitor comparison request

**Processing Time**:
- Competitor identification: 10-15 seconds
- Full analysis with competitors: 20-30 seconds

**Recommendations**:
- Cache competitor data when possible
- Batch competitor requests
- Use faster models for quick analysis

## Troubleshooting

### Issue: Competitors not identifying correctly

**Solution**: 
- Verify product data is accurate
- Check category mapping
- Increase temperature in identify prompt

### Issue: Missing competitor information

**Solution**:
- Verify API key has sufficient quota
- Check model availability
- Review error logs in backend terminal

### Issue: Timeout on competitor analysis

**Solution**:
- Reduce competitor count
- Use faster model (gpt-3.5-turbo)
- Increase timeout value in requests

## Future Enhancements

1. **Real-time Web Scraping**
   - Scrape actual competitor websites
   - Extract real prices and features
   - Monitor competitor changes

2. **Social Media Analysis**
   - Analyze competitor sentiment
   - Track social mentions
   - Monitor review ratings

3. **Historical Tracking**
   - Track competitor changes over time
   - Monitor market dynamics
   - Trend analysis

4. **Advanced Pricing Analysis**
   - Dynamic pricing patterns
   - Discount trends
   - Price elasticity estimation

5. **Competitor Clustering**
   - Group similar competitors
   - Identify market segments
   - Analyze market structure

## API Integration Example

```javascript
// Frontend - Request with competitor analysis
const response = await axios.post('/api/product-analysis/analyze', {
  url: productUrl,
  api_key: openaiKey,
  model: 'gpt-4o-mini'
});

// Access competitor data
const competitors = response.data.competitor_analysis.competitors;
const marketAnalysis = response.data.competitor_analysis.market_analysis;

// Display in UI
competitors.forEach(comp => {
  console.log(`${comp.rank}. ${comp.brand} - Threat: ${comp.threat_level}`);
  console.log(`  Strength: ${comp.key_strength}`);
  console.log(`  Your edge: ${comp.key_weakness}`);
});
```

## Summary

The Intelligent Competitor Analysis feature provides:

✅ Automatic competitor identification  
✅ Detailed threat assessment  
✅ Key strength/weakness comparison  
✅ Market positioning analysis  
✅ Strategic recommendations  
✅ Clean, organized UI display  

This enables users to understand their competitive landscape without manual competitor research!
