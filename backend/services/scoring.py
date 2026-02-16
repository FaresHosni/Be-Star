"""
Quiz Scoring Engine - Fuzzy text matching for completion questions
Uses rapidfuzz for high-performance fuzzy string matching.
Falls back to basic matching if rapidfuzz not installed.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Try to import rapidfuzz, fallback to basic matching
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
    logger.info("rapidfuzz loaded successfully")
except ImportError:
    HAS_RAPIDFUZZ = False
    logger.warning("rapidfuzz not installed, using basic matching")


def normalize_arabic(text: str) -> str:
    """Normalize Arabic text for comparison"""
    if not text:
        return ""
    text = text.strip().lower()
    # Remove tashkeel (diacritics)
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]', '', text)
    # Normalize alef variants
    text = re.sub(r'[إأآا]', 'ا', text)
    # Normalize taa marbuta
    text = text.replace('ة', 'ه')
    # Normalize ya
    text = text.replace('ى', 'ي')
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text


def basic_similarity(s1: str, s2: str) -> float:
    """Basic similarity using set overlap (fallback if rapidfuzz not available)"""
    if not s1 or not s2:
        return 0.0
    words1 = set(s1.split())
    words2 = set(s2.split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return (len(intersection) / len(union)) * 100


def calculate_similarity(answer: str, correct: str) -> float:
    """
    Calculate similarity between user answer and correct answer.
    Returns a score 0-100.
    """
    # Normalize both texts
    norm_answer = normalize_arabic(answer)
    norm_correct = normalize_arabic(correct)
    
    # Exact match
    if norm_answer == norm_correct:
        return 100.0
    
    if HAS_RAPIDFUZZ:
        # Use multiple fuzzy matching strategies and take the best
        scores = [
            fuzz.ratio(norm_answer, norm_correct),
            fuzz.partial_ratio(norm_answer, norm_correct),
            fuzz.token_sort_ratio(norm_answer, norm_correct),
            fuzz.token_set_ratio(norm_answer, norm_correct),
        ]
        return max(scores)
    else:
        return basic_similarity(norm_answer, norm_correct)


def evaluate_answer(answer_text: str, correct_answer: str, question_type: str, threshold: float = 90.0) -> dict:
    """
    Evaluate a participant's answer.
    
    Returns:
        {
            "is_correct": bool,
            "similarity_score": float (0-100),
            "method": str
        }
    """
    if question_type == "mcq":
        # MCQ: extract first letter if it matches A-D (e.g. "A) answer" -> "A")
        clean_answer = answer_text.strip().upper()
        # Regex to capture starting letter (A, B, C, D) followed by optional punctuation/space
        match = re.match(r"^([A-D])", clean_answer)
        if match:
            clean_answer = match.group(1)
        
        is_correct = clean_answer == correct_answer.strip().upper()
        return {
            "is_correct": is_correct,
            "similarity_score": 100.0 if is_correct else 0.0,
            "method": "exact_match"
        }
    
    elif question_type == "completion":
        # Completion: fuzzy matching
        similarity = calculate_similarity(answer_text, correct_answer)
        is_correct = similarity >= threshold
        return {
            "is_correct": is_correct,
            "similarity_score": round(similarity, 1),
            "method": "fuzzy_match" if HAS_RAPIDFUZZ else "basic_match"
        }
    
    return {"is_correct": False, "similarity_score": 0.0, "method": "unknown"}
