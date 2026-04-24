from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# ============== GOOGLE OAUTH & USER MANAGEMENT MODELS ==============

class GoogleTokenRequest(BaseModel):
    token: str

class UserProfile(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False

class UsageLimit(BaseModel):
    used: int = 0
    limit: int = 10
    remaining: int = 10
    resets_at: str = ""

class UserStats(BaseModel):
    user: UserProfile
    usage: Dict[str, UsageLimit]

class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserProfile] = None
    message: str = ""

class EngineConfig(BaseModel):
    # Legacy / classic mode (per-provider keys)
    openai_key: str = ""
    openai_model: str = ""
    second_engine: str = "None"
    openai2_key: Optional[str] = None
    openai2_model: Optional[str] = None
    gemini_key: Optional[str] = None
    gemini_model: Optional[str] = None
    anthropic_key: Optional[str] = None
    claude_model: Optional[str] = None

    # New: Unified OpenRouter gateway
    # When mode="openrouter", l1_* and l2_* select any model available on OpenRouter
    mode: Optional[str] = "classic"  # "classic" | "openrouter"
    openrouter_key: Optional[str] = None
    l1_model: Optional[str] = None   # e.g. "openai/gpt-4o", "anthropic/claude-3.5-sonnet"
    l2_model: Optional[str] = None   # None or "none" to skip second pass
    l1_temperature: Optional[float] = None
    l2_temperature: Optional[float] = None

class OptimizeRequest(BaseModel):
    prev_title: str
    prev_desc: str
    product_link: Optional[str] = ""
    l1_prompt: str
    l2_prompt: Optional[str] = ""
    config: EngineConfig

class BatchRow(BaseModel):
    row_id: int
    prev_title: str
    prev_desc: str
    product_link: Optional[str] = ""

class BatchRequest(BaseModel):
    rows: List[BatchRow]
    l1_prompt: str
    l2_prompt: Optional[str] = ""
    config: EngineConfig

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str
    api_key: str

class ListingResult(BaseModel):
    new_title: str
    new_description: str
    keywords_short: List[str]
    keywords_mid: List[str]
    keywords_long: List[str]

class OptimizeResponse(BaseModel):
    draft: Optional[ListingResult] = None
    final: Optional[ListingResult] = None
    report_html: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

class OptimizationHistoryEntry(BaseModel):
    entry_id: str
    mode: str  # 'single' or 'batch'
    created_at: str
    prev_title: str = ""
    prev_desc: str = ""
    product_link: Optional[str] = ""
    final: Optional[ListingResult] = None
    row_id: Optional[int] = None

class OptimizationHistoryResponse(BaseModel):
    success: bool = True
    entries: List[OptimizationHistoryEntry] = []

# ============== ENTERPRISE PRODUCT INTELLIGENCE MODELS v3.0 ==============

# --- Module 1: Product DNA ---
class BrandIdentity(BaseModel):
    name: str = ""
    tier: str = "" # Mass/Value/Premium/Luxury
    parentCompany: str = ""
    brandStrength: int = 0 # 1-10

class ProductIdentity(BaseModel):
    standardizedName: str = ""
    brand: BrandIdentity = BrandIdentity()
    model: str = ""
    version: str = ""
    launchContext: str = ""

class CategoryMapping(BaseModel):
    level1: str = ""
    level2: str = ""
    level3: str = ""
    level4: str = ""
    categoryPath: str = ""
    marketSize: str = ""

class EducationBoard(BaseModel):
    name: str = ""
    fullName: str = ""
    prevalence: str = ""

class AcademicLevel(BaseModel):
    grade: str = ""
    stage: str = ""
    ageGroup: str = ""

class SubjectDetails(BaseModel):
    primary: str = ""
    subTopics: List[str] = []
    difficulty: str = ""

class ContentProfile(BaseModel):
    type: str = ""
    features: List[str] = []
    solutionType: str = ""
    practiceQuestions: str = ""
    previousYearPapers: str = ""

class ExamAlignment(BaseModel):
    primaryExam: str = ""
    secondaryExams: List[str] = []
    syllabusYear: str = ""
    patternAlignment: str = ""

class EditionDetails(BaseModel):
    year: str = ""
    edition: str = ""
    isUpdated: bool = False

class EducationalDetails(BaseModel):
    isEducational: bool = False
    board: EducationBoard = EducationBoard()
    academicLevel: AcademicLevel = AcademicLevel()
    subject: SubjectDetails = SubjectDetails()
    contentProfile: ContentProfile = ContentProfile()
    examAlignment: ExamAlignment = ExamAlignment()
    edition: EditionDetails = EditionDetails()

class Connectivity(BaseModel):
    type: str = ""
    technology: str = ""
    range: str = ""
    multipoint: bool = False

class AudioSpecs(BaseModel):
    driverSize: str = ""
    driverType: str = ""
    frequencyResponse: str = ""
    impedance: str = ""
    sensitivity: str = ""

class ElectronicsFeatures(BaseModel):
    anc: Dict[str, Any] = {}
    enc: Dict[str, Any] = {}
    transparency: bool = False
    gamingMode: Dict[str, Any] = {}
    appSupport: Dict[str, Any] = {}

class BatterySpecs(BaseModel):
    capacity: str = ""
    playtimeWithANC: str = ""
    playtimeWithoutANC: str = ""
    chargingTime: str = ""
    fastCharging: Dict[str, Any] = {}

class BuildSpecs(BaseModel):
    materials: List[str] = []
    weight: str = ""
    foldable: bool = False
    ipRating: str = ""
    colorOptions: List[str] = []

class WarrantySpecs(BaseModel):
    duration: str = ""
    type: str = ""
    extendedAvailable: bool = False

class ElectronicsDetails(BaseModel):
    isElectronics: bool = False
    productType: str = ""
    connectivity: Connectivity = Connectivity()
    audioSpecs: AudioSpecs = AudioSpecs()
    features: ElectronicsFeatures = ElectronicsFeatures()
    battery: BatterySpecs = BatterySpecs()
    build: BuildSpecs = BuildSpecs()
    warranty: WarrantySpecs = WarrantySpecs()

# --- Module 2: Price Intelligence ---
class PricingDetails(BaseModel):
    extractedPrice: str = ""
    mrp: str = ""
    salePrice: str = ""
    discount: Dict[str, str] = {}
    numericPrice: float = 0.0
    currency: str = "INR"
    pricePerValue: str = ""

class Segmentation(BaseModel):
    segment: str = ""
    segmentRange: Dict[str, float] = {}
    positionInSegment: str = ""
    percentileRank: int = 0

class CompetitivePosition(BaseModel):
    priceCompetitiveness: int = 0
    featureToPrice: float = 0.0
    valueProposition: str = ""
    priceElasticity: str = ""

class CompetitorPriceRange(BaseModel):
    min: float = 0.0
    max: float = 0.0
    sweetSpot: str = ""
    avgCompetitorPrice: float = 0.0

class PriceIntelligence(BaseModel):
    pricing: PricingDetails = PricingDetails()
    segmentation: Segmentation = Segmentation()
    competitivePosition: CompetitivePosition = CompetitivePosition()
    competitorPriceRange: CompetitorPriceRange = CompetitorPriceRange()

# --- Module 3: Feature Architecture ---
class FeatureItem(BaseModel):
    name: str = ""
    description: str = ""
    utility: int = 0
    uniqueness: int = 0
    execution: int = 0
    valueImpact: str = ""
    competitiveAdvantage: Optional[str] = None

class FeatureGap(BaseModel):
    missingFeature: str = ""
    expectedAt: str = ""
    impact: str = ""

class FeatureArchitecture(BaseModel):
    coreFeatures: List[FeatureItem] = []
    differentiatorFeatures: List[FeatureItem] = []
    convenienceFeatures: List[FeatureItem] = []
    premiumFeatures: List[FeatureItem] = []
    featureGaps: List[FeatureGap] = []
    overallFeatureScore: float = 0.0

# --- Module 4: Target Audience ---
class Demographics(BaseModel):
    ageRange: str = ""
    income: str = ""
    location: str = ""
    occupation: str = ""

class Psychographics(BaseModel):
    values: List[str] = []
    lifestyle: str = ""
    techSavviness: str = ""
    brandLoyalty: str = ""

class BuyingBehavior(BaseModel):
    researchDepth: str = ""
    priceSensitivity: str = ""
    decisionTime: str = ""
    influencers: str = ""

class Persona(BaseModel):
    name: str = ""
    demographics: Demographics = Demographics()
    psychographics: Psychographics = Psychographics()
    buyingBehavior: BuyingBehavior = BuyingBehavior()
    painPoints: List[str] = []
    decisionDrivers: List[str] = []

class AntiPersona(BaseModel):
    description: str = ""
    whyNotThem: str = ""

class TargetAudience(BaseModel):
    primaryPersona: Persona = Persona()
    secondaryPersonas: List[Persona] = []
    antiPersona: AntiPersona = AntiPersona()

# --- Module 5: Competitive Landscape ---
class SegmentValidation(BaseModel):
    productPrice: float = 0.0
    competitorRange: str = ""
    segmentMatch: str = ""

class DirectCompetitor(BaseModel):
    brand: str = ""
    product: str = ""
    price: str = ""
    priceDiff: str = ""
    threatLevel: str = ""
    keyStrength: str = ""
    keyWeakness: str = ""
    marketShare: str = ""

class AspirationalBenchmark(BaseModel):
    brand: str = ""
    product: str = ""
    price: str = ""
    relevance: str = ""

class CompetitorBrands(BaseModel):
    primary: List[str] = []
    secondary: List[str] = []
    avoid: List[str] = []
    avoidReason: str = ""

class CompetitiveLandscape(BaseModel):
    segmentValidation: SegmentValidation = SegmentValidation()
    directCompetitors: List[DirectCompetitor] = []
    adjacentCompetitors: List[DirectCompetitor] = []
    aspirationalBenchmark: AspirationalBenchmark = AspirationalBenchmark()
    competitorSearchQueries: List[str] = []
    competitorBrands: CompetitorBrands = CompetitorBrands()

# --- Module 6: Strategic Insights ---
class StrategicInsights(BaseModel):
    strengthsToHighlight: List[str] = []
    weaknessesToAddress: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []
    marketingAngle: str = ""

# --- MASTER ANALYSIS MODEL ---
class DeepProductAnalysis(BaseModel):
    """Enterprise v3.0 Master Analysis Model"""
    analysisMetadata: Dict[str, Any] = {}
    productIdentity: ProductIdentity = ProductIdentity()
    categoryMapping: CategoryMapping = CategoryMapping()
    educationalProductDetails: Optional[EducationalDetails] = None
    electronicsProductDetails: Optional[ElectronicsDetails] = None
    priceIntelligence: PriceIntelligence = PriceIntelligence()
    featureArchitecture: FeatureArchitecture = FeatureArchitecture()
    targetAudience: TargetAudience = TargetAudience()
    competitiveLandscape: CompetitiveLandscape = CompetitiveLandscape()
    strategicInsights: StrategicInsights = StrategicInsights()
    
    # Backward compatibility fields (optional)
    product_name: str = ""
    brand_publisher: str = ""
    main_category: str = ""
    sub_category: str = ""
    key_features: List[str] = []
    competitor_search_queries: List[str] = []
    competitor_brands: List[str] = []
    price_info: Optional[Any] = None # Deprecated, mapped to priceIntelligence

# --- COMPETITOR INTELLIGENCE MODELS ---

class Competitor(BaseModel):
    name: str = ""
    publisher: str = ""
    price: str = ""
    url: str = ""

class QuadrantPosition(BaseModel):
    quadrant: str = ""
    xPosition: float = 0.0
    yPosition: float = 0.0
    justification: str = ""

class PriceValueMatrix(BaseModel):
    quadrantPlacement: Dict[str, Any] = {} # subjectProduct, competitors
    priceComparison: Dict[str, Any] = {}

class FeatureComparisonItem(BaseModel):
    name: str = ""
    importance: str = ""
    values: Dict[str, str] = {}
    winner: str = ""
    winnerReason: str = ""
    impactOnDecision: str = ""

class FeatureCategory(BaseModel):
    category: str = ""
    features: List[FeatureComparisonItem] = []

class FeatureBattlefield(BaseModel):
    comparisonTable: List[FeatureCategory] = []
    featureWinSummary: Dict[str, int] = {}
    uniqueFeatures: Dict[str, List[str]] = {}

class SentimentItem(BaseModel):
    sentiment: str = ""
    frequency: str = ""
    impact: Optional[str] = None
    severity: Optional[str] = None
    dealBreaker: Optional[bool] = None

class ProductSentiment(BaseModel):
    overallSentiment: str = ""
    satisfactionScore: float = 0.0
    recommendationRate: str = ""
    commonPraises: List[SentimentItem] = []
    commonComplaints: List[SentimentItem] = []
    sentimentSummary: str = ""

class CustomerSentiment(BaseModel):
    subjectProduct: ProductSentiment = ProductSentiment()
    competitors: List[ProductSentiment] = []

class UseCaseItem(BaseModel):
    scenario: str = ""
    winner: str = ""
    reason: str = ""
    runnerUp: str = ""
    avoid: str = ""

class UseCaseMapping(BaseModel):
    useCases: List[UseCaseItem] = []
    useCaseSummary: Dict[str, List[str]] = {}

class ScoringDimension(BaseModel):
    name: str = ""
    weight: float = 0.0
    scores: Dict[str, float] = {}

class OverallScore(BaseModel):
    rawScore: float = 0.0
    weightedScore: float = 0.0
    rank: int = 0
    grade: str = ""

class ScoringMatrix(BaseModel):
    dimensions: List[ScoringDimension] = []
    overallScores: Dict[str, OverallScore] = {}
    ranking: List[Dict[str, Any]] = []

class DecisionNode(BaseModel):
    question: str = ""
    yesPath: str = ""
    noPath: str = ""

class BuyerProfileMatch(BaseModel):
    profile: str = ""
    bestChoice: str = ""
    reason: str = ""

class BuyingDecisionFramework(BaseModel):
    decisionTree: Dict[str, List[DecisionNode]] = {}
    buyerProfileMatch: List[BuyerProfileMatch] = []
    specificRecommendations: Dict[str, Any] = {}

class FinalVerdict(BaseModel):
    winner: str = ""
    winnerScore: float = 0.0
    verdict: str = ""
    targetBuyer: str = ""
    keyTakeaway: str = ""

class CompetitiveAnalysisReport(BaseModel):
    """Enterprise v3.0 Competitor Report"""
    reportMetadata: Dict[str, Any] = {}
    executiveSummary: Dict[str, Any] = {}
    priceValueMatrix: PriceValueMatrix = PriceValueMatrix()
    featureBattlefield: FeatureBattlefield = FeatureBattlefield()
    customerSentiment: CustomerSentiment = CustomerSentiment()
    useCaseMapping: UseCaseMapping = UseCaseMapping()
    scoringMatrix: ScoringMatrix = ScoringMatrix()
    buyingDecisionFramework: BuyingDecisionFramework = BuyingDecisionFramework()
    finalVerdict: FinalVerdict = FinalVerdict()

class CompetitorComparisonRequest(BaseModel):
    analysis: DeepProductAnalysis
    competitors: List[Competitor]
    api_key: str
    model: str = "gpt-4o-mini"

# --- KEYWORD INTELLIGENCE MODELS ---

class KeywordItem(BaseModel):
    keyword: str = ""
    type: str = ""
    searchVolume: str = ""
    competition: str = ""
    buyerIntent: str = ""
    relevance: int = 0
    difficulty: int = 0
    opportunity: str = ""
    suggestedUse: str = ""

class KeywordCluster(BaseModel):
    clusterName: str = ""
    intent: str = ""
    keywords: List[str] = []
    priority: str = ""
    contentStrategy: str = ""

class SeoTitleFormula(BaseModel):
    formula: str = ""
    example: str = ""
    characterCount: int = 0

class KeywordStrategy(BaseModel):
    """Enterprise v3.0 Keyword Strategy"""
    primaryKeywords: List[KeywordItem] = []
    secondaryKeywords: List[KeywordItem] = []
    longTailKeywords: List[KeywordItem] = []
    questionKeywords: List[KeywordItem] = []
    regionalKeywords: List[KeywordItem] = []
    keywordClusters: List[KeywordCluster] = []
    seoTitleFormulas: List[SeoTitleFormula] = []
    metaDescriptionTemplate: str = ""
    negativeKeywords: List[str] = []
    seasonalKeywords: Dict[str, List[str]] = {}
    
    # Backward compatibility
    short_tail: List[str] = []
    mid_tail: List[str] = []
    long_tail: List[str] = []
    seo_keywords: List[str] = []

class ProductData(BaseModel):
    """Raw scraped product data"""
    title: str = ""
    description: str = ""
    price: str = ""
    brand: str = ""
    category: str = ""
    features: List[str] = []
    platform: str = ""
    url: str = ""
    raw_text: str = ""

class ProductAnalysisRequest(BaseModel):
    url: str
    api_key: str
    model: str = "gpt-4o-mini"

class ProductAnalysisResponse(BaseModel):
    success: bool
    product_data: Optional[ProductData] = None
    deep_analysis: Optional[DeepProductAnalysis] = None
    keywords: Optional[KeywordStrategy] = None
    competitor_analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

