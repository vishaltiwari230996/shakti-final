import os
import io
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

# Define the prompt library directory
# From backend/app/services/ go up 4 levels to workspace root, then to "prompt library l1"
PROMPT_LIBRARY_DIR = Path(__file__).parent.parent.parent.parent / "prompt library l1"

# Map of category names to file names
PROMPT_CATEGORIES = {
    "automotive": "Automotive Accessories SEO l1 prompt .docx",
    "baby_kids": "Baby & Kids SEO.docx",
    "books_office": "Books & Office Supplies SEO l1 prompt .docx",
    "electronics": "Electronics SEO l1 prompt  .docx",
    "fashion": "Fashion SEO l1 prompt .docx",
    "food_grocery": "Food & Grocery SEO l1 prompt.docx",
    "health_fitness": "Health & Fitness SEO l1 prompt.docx",
    "home_kitchen": "Home & Kitchen SEO l1 prompt .docx",
    "beauty_personal_care": "_Beauty & Personal Care SEO li prompt.docx",
    "pet_care": "_Pet Care & Supplies SEO l1 prompt .docx",
    "fitness_equipment": "Fitness Equipment  l1 prompt .docx",
    "medical_aid": "Medical Aid & Healthcare l1 prompt.docx",
    "mobile_tablets": "Mobile & Tablets l1 prompt .docx",
    "exam_books": "_Exam Preparation Books l1 prompt .docx",
    "laptops_computers": "_Laptops, Desktops & Computer Accessories  l1 prompt.docx"
}

# User-friendly display names
CATEGORY_DISPLAY_NAMES = {
    "automotive": "Automotive Accessories",
    "baby_kids": "Baby & Kids",
    "books_office": "Books & Office Supplies",
    "electronics": "Electronics",
    "fashion": "Fashion",
    "food_grocery": "Food & Grocery",
    "health_fitness": "Health & Fitness",
    "home_kitchen": "Home & Kitchen",
    "beauty_personal_care": "Beauty & Personal Care",
    "pet_care": "Pet Care & Supplies",
    "fitness_equipment": "Fitness Equipment",
    "medical_aid": "Medical Aid & Healthcare",
    "mobile_tablets": "Mobiles & Tablets",
    "exam_books": "Exam Preparation Books",
    "laptops_computers": "Laptops & Computer Accessories"
}

def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from a DOCX file."""
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            xml = z.read("word/document.xml")
        
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = [t.text or "" for t in root.iterfind(".//w:t", ns)]
        return " ".join("".join(texts).split()).strip()
    except Exception as e:
        return f"[DOCX READ ERROR] {e}"

def get_available_categories():
    """Get list of available prompt categories."""
    categories = []
    for key, filename in PROMPT_CATEGORIES.items():
        file_path = PROMPT_LIBRARY_DIR / filename
        categories.append({
            "id": key,
            "name": CATEGORY_DISPLAY_NAMES[key],
            "filename": filename,
            "available": file_path.exists()
        })
    return categories

def get_prompt_by_category(category_id: str) -> str:
    """Load prompt text for a specific category."""
    if category_id not in PROMPT_CATEGORIES:
        raise ValueError(f"Invalid category: {category_id}")
    
    filename = PROMPT_CATEGORIES[category_id]
    file_path = PROMPT_LIBRARY_DIR / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {filename}")
    
    return extract_text_from_docx(file_path)
