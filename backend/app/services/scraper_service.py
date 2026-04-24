import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import random

from app.services.url_safety import ensure_safe_product_url, safe_get

# Rotate user agents for better scraping success
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

def get_headers():
    """Get headers with randomized user agent."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

# Keep HEADERS for backward compatibility
HEADERS = get_headers()

def detect_platform(url: str) -> str:
    """Detect e-commerce platform from URL."""
    domain = urlparse(url).netloc.lower()
    
    if 'amazon' in domain:
        return 'amazon'
    elif 'flipkart' in domain:
        return 'flipkart'
    elif 'meesho' in domain:
        return 'meesho'
    elif 'myntra' in domain:
        return 'myntra'
    else:
        return 'generic'

def clean_text(text: str) -> str:
    """Clean extracted text."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_amazon(soup: BeautifulSoup) -> dict:
    """Extract product data from Amazon page."""
    data = {
        'title': '',
        'description': '',
        'price': '',
        'features': []
    }
    
    # Extract title
    title_elem = soup.find('span', {'id': 'productTitle'})
    if title_elem:
        data['title'] = clean_text(title_elem.get_text())
    
    # Extract description from feature bullets
    description_parts = []
    
    # Try feature bullets
    feature_bullets = soup.find('div', {'id': 'feature-bullets'})
    if feature_bullets:
        bullets = feature_bullets.find_all('li')
        for bullet in bullets:
            text = clean_text(bullet.get_text())
            if text and len(text) > 10:  # Skip very short texts
                description_parts.append(text)
                data['features'].append(text)
    
    # Try product description
    prod_desc = soup.find('div', {'id': 'productDescription'})
    if prod_desc:
        desc_text = clean_text(prod_desc.get_text())
        if desc_text:
            description_parts.append(desc_text)
    
    # Try A+ content
    aplus = soup.find('div', {'id': 'aplus'})
    if aplus:
        aplus_text = clean_text(aplus.get_text())
        if aplus_text and len(aplus_text) > 50:
            description_parts.append(aplus_text[:500])  # Limit A+ content
    
    # Combine description parts
    # Join all parts to ensure we don't miss the main description if there are many bullets
    data['description'] = '\n\n'.join(description_parts)
    
    # Extract price (optional)
    price_elem = soup.find('span', {'class': 'a-price-whole'})
    if price_elem:
        data['price'] = clean_text(price_elem.get_text())
    
    return data

def extract_flipkart(soup: BeautifulSoup) -> dict:
    """Extract product data from Flipkart page."""
    data = {
        'title': '',
        'description': '',
        'price': '',
        'features': []
    }
    
    # Extract title
    title_elem = soup.find('span', {'class': 'B_NuCI'})
    if not title_elem:
        title_elem = soup.find('h1', {'class': 'yhB1nd'})
    if title_elem:
        data['title'] = clean_text(title_elem.get_text())
    
    # Extract description
    description_parts = []
    
    # Try product description
    desc_elem = soup.find('div', {'class': '_1mXcCf'})
    if desc_elem:
        desc_text = clean_text(desc_elem.get_text())
        if desc_text:
            description_parts.append(desc_text)
    
    # Try specifications
    specs = soup.find_all('li', {'class': '_21lJbe'})
    for spec in specs[:5]:  # Limit to first 5 specs
        text = clean_text(spec.get_text())
        if text:
            description_parts.append(text)
            data['features'].append(text)
    
    data['description'] = ' '.join(description_parts)
    
    # Extract price
    price_elem = soup.find('div', {'class': '_30jeq3'})
    if price_elem:
        data['price'] = clean_text(price_elem.get_text())
    
    return data

def extract_generic(soup: BeautifulSoup, url: str) -> dict:
    """Generic extraction fallback."""
    data = {
        'title': '',
        'description': '',
        'price': '',
        'features': []
    }
    
    # Try to get title from common places
    title = None
    # Try meta tags first
    og_title = soup.find('meta', {'property': 'og:title'})
    if og_title:
        title = og_title.get('content')
    
    # Try h1
    if not title:
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text()
    
    # Try page title
    if not title:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text()
    
    data['title'] = clean_text(title) if title else ""
    
    # Try to get description from meta tags
    og_desc = soup.find('meta', {'property': 'og:description'})
    if og_desc:
        data['description'] = clean_text(og_desc.get('content'))
    else:
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            data['description'] = clean_text(meta_desc.get('content'))
    
    return data

def extract_product_data(url: str) -> dict:
    """
    Main function to extract product data from URL.
    
    Args:
        url: Product page URL
        
    Returns:
        dict with extracted data and metadata
    """
    try:
        safe_url = ensure_safe_product_url(url)
        
        # Detect platform
        platform = detect_platform(safe_url)
        if platform not in {'amazon', 'flipkart'}:
            return {
                'success': False,
                'error': 'Only Amazon and Flipkart product URLs are supported'
            }
        
        # Download HTML with fresh headers
        response = safe_get(safe_url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract based on platform
        if platform == 'amazon':
            data = extract_amazon(soup)
        elif platform == 'flipkart':
            data = extract_flipkart(soup)
        else:
            data = extract_generic(soup, safe_url)
        
        # Validate that we got at least title
        if not data.get('title'):
            return {
                'success': False,
                'error': 'Could not extract product title from this page'
            }
        
        return {
            'success': True,
            'platform': platform,
            'data': data
        }
        
    except ValueError as e:
        return {
            'success': False,
            'error': str(e)
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Request timed out - the page took too long to load'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Failed to fetch URL: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Extraction error: {str(e)}'
        }
