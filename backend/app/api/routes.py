from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from app.models import (
    OptimizeRequest, OptimizeResponse, BatchRequest, ChatRequest, ListingResult,
    ProductAnalysisRequest, ProductAnalysisResponse, CompetitorComparisonRequest,
    GoogleTokenRequest, UserStats, AuthResponse, OptimizationHistoryResponse
)
from app.services.llm_service import run_l1_l2_logic, openai_chat_completion, to_utf8_clean
from app.services.report_service import html_report_bytes
from app.services.prompt_service import get_available_categories, get_prompt_by_category
from app.services.scraper_service import extract_product_data
from app.services.product_analyzer_service import (
    ProductScraperService, DeepProductAnalyzerService, KeywordExtractorService
)
from app.services.competitor_intelligence_service import CompetitorIntelligenceService
from app.services.auth_service import AuthService
from app.services.history_service import HistoryService
import io
import zipfile
from xml.etree import ElementTree as ET

router = APIRouter()


def get_authenticated_user_id(authorization: str) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required. Please log in with Google.")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required. Please log in with Google.")

    user_data = AuthService.verify_google_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please log in again.")

    user = AuthService.create_or_update_user(user_data)
    return user['user_id']

# ============== GOOGLE OAUTH ENDPOINTS ==============

@router.post("/auth/google-login", response_model=AuthResponse)
async def google_login(request: GoogleTokenRequest):
    """Verify Google OAuth token and create/update user"""
    try:
        # Verify the token with Google
        user_data = AuthService.verify_google_token(request.token)
        
        if not user_data:
            return AuthResponse(success=False, message="Invalid token")
        
        # Create or update user in database
        user = AuthService.create_or_update_user(user_data)
        
        from app.models import UserProfile
        return AuthResponse(
            success=True,
            user=UserProfile(
                user_id=user['user_id'],
                email=user['email'],
                name=user['name'],
                picture=user.get('picture'),
                email_verified=user_data.get('email_verified', False)
            ),
            message="Login successful"
        )
    except Exception as e:
        return AuthResponse(success=False, message="Authentication failed")

@router.get("/auth/user-stats")
async def get_user_stats(authorization: str = Header(None)):
    """Get current user's usage statistics"""
    try:
        user_id = get_authenticated_user_id(authorization)
        
        stats = AuthService.get_user_stats(user_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="User not found")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimize/history", response_model=OptimizationHistoryResponse)
async def get_optimization_history(authorization: str = Header(None)):
    try:
        user_id = get_authenticated_user_id(authorization)

        entries = HistoryService.get_history(user_id)
        return OptimizationHistoryResponse(entries=entries)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            xml = z.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = [t.text or "" for t in root.iterfind(".//w:t", ns)]
        return " ".join("".join(texts).split()).strip()
    except Exception as e:
        return f"[DOCX READ ERROR] {e}"

@router.post("/extract-docx")
async def extract_docx(file: UploadFile = File(...)):
    content = await file.read()
    text = extract_text_from_docx(content)
    return {"text": text}

@router.get("/prompt-templates")
async def get_prompt_templates():
    """Get list of available prompt template categories."""
    try:
        categories = get_available_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompt-templates/{category_id}")
async def get_prompt_template(category_id: str):
    """Get prompt text for a specific category."""
    try:
        prompt_text = get_prompt_by_category(category_id)
        return {"category_id": category_id, "prompt": prompt_text}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-url")
async def extract_from_url(request: dict):
    """Extract product data from e-commerce URL."""
    try:
        url = request.get('url', '').strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        result = extract_product_data(url)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Extraction failed'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/single", response_model=OptimizeResponse)
async def optimize_single(request: OptimizeRequest, authorization: str = Header(None)):
    try:
        user_id = get_authenticated_user_id(authorization)
    except HTTPException as exc:
        return OptimizeResponse(
            success=False,
            error=exc.detail
        )

    # Check usage limit (same as batch_optimize counter)
    usage_check = AuthService.check_usage_limit(user_id, 'batch_optimize')
    
    if not usage_check['allowed']:
        return OptimizeResponse(
            success=False,
            error=f"⚠️ Single optimization limit reached! You've used all 10 optimizations in the last 72 hours. Limit resets at {usage_check['resets_at']}"
        )
    
    try:
        draft, final = run_l1_l2_logic(
            prev_title=request.prev_title,
            prev_desc=request.prev_desc,
            product_link=request.product_link,
            sp_l1=request.l1_prompt,
            sp_l2=request.l2_prompt,
            config=request.config
        )
        
        report_html = html_report_bytes(
            title_text="Shakti 1.2 — Single Report",
            inputs={
                "prev_title": request.prev_title,
                "prev_desc": request.prev_desc,
                "product_link": request.product_link,
            },
            draft=draft,
            final_=final
        )
        
        # Persist in history for quick review
        HistoryService.record_entry(
            user_id=user_id,
            mode="single",
            prev_title=request.prev_title,
            prev_desc=request.prev_desc,
            product_link=request.product_link,
            final=final
        )

        # Increment usage counter
        AuthService.increment_usage(user_id, 'batch_optimize')

        return OptimizeResponse(draft=draft, final=final, report_html=report_html, success=True)
    except Exception as e:
        return OptimizeResponse(
            success=False,
            error=f"Optimization failed: {str(e)}"
        )

@router.post("/optimize/batch")
async def optimize_batch(request: BatchRequest, authorization: str = Header(None)):
    try:
        user_id = get_authenticated_user_id(authorization)
    except HTTPException as exc:
        return {
            "error": exc.detail,
            "results": []
        }

    # Check usage limit
    usage_check = AuthService.check_usage_limit(user_id, 'batch_optimize')
    
    if not usage_check['allowed']:
        return {
            "error": f"⚠️ Batch optimize limit reached! You've used all 10 batch operations in the last 72 hours. Limit resets at {usage_check['resets_at']}",
            "results": []
        }
    
    results = []
    # Process sequentially
    for row in request.rows:
        try:
            draft, final = run_l1_l2_logic(
                prev_title=row.prev_title,
                prev_desc=row.prev_desc,
                product_link=row.product_link,
                sp_l1=request.l1_prompt,
                sp_l2=request.l2_prompt,
                config=request.config
            )
            
            report_html = html_report_bytes(
                title_text=f"Shakti 1.2 — Batch Report #{row.row_id}",
                inputs={
                    "prev_title": row.prev_title,
                    "prev_desc": row.prev_desc,
                    "product_link": row.product_link,
                },
                draft=draft,
                final_=final
            )

            HistoryService.record_entry(
                user_id=user_id,
                mode="batch",
                prev_title=row.prev_title,
                prev_desc=row.prev_desc,
                product_link=row.product_link,
                final=final,
                row_id=row.row_id
            )
            
            results.append({
                "row_id": row.row_id,
                "status": "success",
                "draft": draft.dict(),
                "final": final.dict(),
                "report_html": report_html
            })
        except Exception as e:
            results.append({
                "row_id": row.row_id,
                "status": "error",
                "error": str(e)
            })
    
    # Increment usage counter
    AuthService.increment_usage(user_id, 'batch_optimize')

    return {"results": results}

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Convert messages to format expected by openai_chat_completion
        msgs = [{"role": m.role, "content": m.content} for m in request.messages]
        
        response = openai_chat_completion(
            api_key=request.api_key,
            model=request.model,
            messages=msgs
        )
        return {"role": "assistant", "content": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== PRODUCT ANALYSIS ENDPOINTS ==============

@router.post("/product-analysis/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(request: ProductAnalysisRequest, authorization: str = Header(None)):
    """Analyze a product from Amazon/Flipkart URL using GPT"""
    try:
        user_id = get_authenticated_user_id(authorization)
    except HTTPException as exc:
        return ProductAnalysisResponse(
            success=False,
            error=exc.detail
        )

    try:
        # Check usage limit
        usage_check = AuthService.check_usage_limit(user_id, 'product_analysis')
        
        if not usage_check['allowed']:
            return ProductAnalysisResponse(
                success=False,
                error=f"⚠️ Usage limit reached! You've used all 10 product analyses in the last 72 hours. Limit resets at {usage_check['resets_at']}"
            )
        
        # Initialize services
        scraper = ProductScraperService()
        analyzer = DeepProductAnalyzerService(request.api_key, request.model)
        keyword_extractor = KeywordExtractorService(request.api_key, request.model)
        competitor_intel = CompetitorIntelligenceService(request.api_key, request.model)

        product_data = scraper.scrape(request.url)
        deep_analysis = analyzer.analyze(product_data)
        keywords = keyword_extractor.extract(
            deep_analysis.product_name,
            deep_analysis.main_category,
            deep_analysis.brand_publisher
        )
        competitor_analysis = competitor_intel.identify_competitors(product_data, deep_analysis)

        # Increment usage counter
        AuthService.increment_usage(user_id, 'product_analysis')

        return ProductAnalysisResponse(
            success=True,
            product_data=product_data,
            deep_analysis=deep_analysis,
            keywords=keywords,
            competitor_analysis=competitor_analysis  # Include in response
        )

    except Exception as e:
        return ProductAnalysisResponse(
            success=False,
            error=f"Analysis failed: {str(e)}"
        )



@router.post("/product-analysis/compare")
async def compare_competitors(request: CompetitorComparisonRequest):
    """Compare product with competitors using GPT"""
    try:
        from app.services.product_analysis_service import CompetitorComparator, OpenAIClient
        
        client = OpenAIClient(request.api_key, request.model)
        comparator = CompetitorComparator(client)
        
        # Convert competitors to dict format
        competitors_dict = [{"name": c.name, "publisher": c.publisher} for c in request.competitors]
        
        comparisons = comparator.compare(request.analysis, competitors_dict)
        
        return {"comparisons": [c.dict() for c in comparisons]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/product-analysis/identify-competitors")
async def identify_competitors(request: dict):
    """Intelligently identify competitors for analyzed product"""
    try:
        from app.services.competitor_intelligence_service import CompetitorIntelligenceService
        
        api_key = request.get('api_key')
        model = request.get('model', 'gpt-4o-mini')
        analysis_data = request.get('analysis')
        product_data = request.get('product_data')
        
        if not api_key or not analysis_data:
            raise HTTPException(status_code=400, detail="api_key and analysis are required")
        
        # Convert dicts to model objects if needed
        from app.models import DeepProductAnalysis, ProductData
        
        if isinstance(analysis_data, dict):
            deep_analysis = DeepProductAnalysis(**analysis_data)
        else:
            deep_analysis = analysis_data
        
        if isinstance(product_data, dict):
            product_data_obj = ProductData(**product_data)
        else:
            product_data_obj = product_data
        
        competitor_intel = CompetitorIntelligenceService(api_key, model)
        competitor_analysis = competitor_intel.identify_competitors(product_data_obj, deep_analysis)
        
        return {
            "success": True,
            "competitor_analysis": competitor_analysis
        }
        
    except Exception as e:
        print(f"[ERROR] Competitor identification error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/product-analysis/compare-with-competitors")
async def compare_with_competitors(request: dict):
    """Get detailed comparison between product and specified competitors"""
    try:
        from app.services.competitor_intelligence_service import CompetitorIntelligenceService
        from app.models import DeepProductAnalysis
        
        api_key = request.get('api_key')
        model = request.get('model', 'gpt-4o-mini')
        analysis_data = request.get('analysis')
        competitor_names = request.get('competitor_names', [])
        
        if not api_key or not analysis_data or not competitor_names:
            raise HTTPException(status_code=400, detail="api_key, analysis, and competitor_names are required")
        
        if isinstance(analysis_data, dict):
            deep_analysis = DeepProductAnalysis(**analysis_data)
        else:
            deep_analysis = analysis_data
        
        competitor_intel = CompetitorIntelligenceService(api_key, model)
        comparison = competitor_intel.get_competitor_comparison(deep_analysis, competitor_names)
        
        return {
            "success": True,
            "comparison": comparison
        }
        
    except Exception as e:
        print(f"[ERROR] Comparison error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


