"""
Text Analysis Utility Module
Implements rule-based suspicious pattern detection for reviews.
This module handles Epic 2 (Detect suspicious review patterns) and
Epic 4 (Explain the Result - provide reasons for the decision).
"""
import re
import string
from collections import Counter
from utils.database import get_active_detection_rules


class TextAnalyzer:
    """
    Analyzes review text for suspicious patterns commonly associated with fake reviews.
    Returns a list of flags (reasons) explaining why a review may be suspicious.
    """

    def __init__(self):
        self._load_rules()

    def _load_rules(self):
        """Load active detection rules from the database."""
        rules = get_active_detection_rules()
        self.rules = {}
        for rule in rules:
            self.rules[rule["rule_name"]] = {
                "type": rule["rule_type"],
                "value": rule["rule_value"],
                "weight": rule["weight"],
                "description": rule["description"]
            }

    def reload_rules(self):
        """Reload rules from database (useful after admin updates)."""
        self._load_rules()

    def analyze(self, text):
        """
        Analyze a review text and return all detected suspicious patterns.

        Args:
            text (str): The review text to analyze.

        Returns:
            dict: {
                "flags": list of flagged issues with descriptions,
                "suspicion_score": float (0.0 to 1.0, higher = more suspicious),
                "details": dict of individual check results
            }
        """
        flags = []
        details = {}
        total_weight = 0.0
        triggered_weight = 0.0

        # --- Check 1: Overly Promotional Words ---
        promo_result = self._check_promotional_words(text)
        details["promotional_words"] = promo_result
        rule_weight = self.rules.get("promotional_keywords", {}).get("weight", 1.0)
        total_weight += rule_weight
        if promo_result["found"]:
            flags.append({
                "type": "promotional_language",
                "severity": "high" if promo_result["count"] >= 3 else "medium",
                "message": f"Contains {promo_result['count']} overly promotional word(s): {', '.join(promo_result['words'][:5])}",
                "detail": "Fake reviews often use exaggerated positive language to boost product ratings."
            })
            triggered_weight += rule_weight * min(promo_result["count"] / 3.0, 1.0)

        # --- Check 2: Negative Spam Keywords ---
        neg_result = self._check_negative_spam(text)
        details["negative_spam"] = neg_result
        rule_weight = self.rules.get("negative_spam_keywords", {}).get("weight", 1.0)
        total_weight += rule_weight
        if neg_result["found"]:
            flags.append({
                "type": "negative_spam",
                "severity": "high" if neg_result["count"] >= 3 else "medium",
                "message": f"Contains {neg_result['count']} excessively negative word(s): {', '.join(neg_result['words'][:5])}",
                "detail": "Competitor sabotage reviews often use extreme negative language."
            })
            triggered_weight += rule_weight * min(neg_result["count"] / 3.0, 1.0)

        # --- Check 3: Review Too Short ---
        length_result = self._check_review_length(text)
        details["review_length"] = length_result
        rule_weight = self.rules.get("short_review_warning", {}).get("weight", 0.5)
        total_weight += rule_weight
        if length_result["is_short"]:
            flags.append({
                "type": "short_review",
                "severity": "low",
                "message": f"Review is very short ({length_result['char_count']} characters, {length_result['word_count']} words).",
                "detail": "Genuine reviews typically provide more detailed feedback about the product."
            })
            triggered_weight += rule_weight * 0.6

        # --- Check 4: Excessive Punctuation ---
        punct_result = self._check_excessive_punctuation(text)
        details["punctuation"] = punct_result
        rule_weight = self.rules.get("excessive_punctuation_ratio", {}).get("weight", 0.8)
        total_weight += rule_weight
        if punct_result["is_excessive"]:
            flags.append({
                "type": "excessive_punctuation",
                "severity": "medium",
                "message": f"Excessive punctuation detected (ratio: {punct_result['ratio']:.2%}).",
                "detail": "Fake reviews often use excessive exclamation marks or question marks for emphasis."
            })
            triggered_weight += rule_weight * min(punct_result["ratio"] / 0.15, 1.0)

        # --- Check 5: Excessive Capitalization ---
        caps_result = self._check_excessive_caps(text)
        details["capitalization"] = caps_result
        rule_weight = self.rules.get("excessive_caps_ratio", {}).get("weight", 0.7)
        total_weight += rule_weight
        if caps_result["is_excessive"]:
            flags.append({
                "type": "excessive_caps",
                "severity": "medium",
                "message": f"Excessive use of capital letters ({caps_result['ratio']:.2%} of letters are uppercase).",
                "detail": "Excessive capitalization often indicates exaggerated tone or automated text."
            })
            triggered_weight += rule_weight * min(caps_result["ratio"] / 0.5, 1.0)

        # --- Check 6: Repeated Words/Phrases ---
        repetition_result = self._check_repetition(text)
        details["repetition"] = repetition_result
        rule_weight = self.rules.get("repetition_threshold", {}).get("weight", 0.9)
        total_weight += rule_weight
        if repetition_result["is_repetitive"]:
            flags.append({
                "type": "word_repetition",
                "severity": "medium",
                "message": f"High word repetition detected ({repetition_result['ratio']:.2%}). Most repeated: {', '.join(repetition_result['top_repeated'][:3])}",
                "detail": "Fake reviews often repeat certain words or phrases to pad the review length."
            })
            triggered_weight += rule_weight * min(repetition_result["ratio"] / 0.3, 1.0)

        # --- Check 7: Generic/Vague Language ---
        generic_result = self._check_generic_language(text)
        details["generic_language"] = generic_result
        total_weight += 0.6
        if generic_result["is_generic"]:
            flags.append({
                "type": "generic_language",
                "severity": "low",
                "message": f"Review uses generic/vague language ({generic_result['count']} generic phrases found).",
                "detail": "Fake reviews tend to be vague without specific product details."
            })
            triggered_weight += 0.6 * min(generic_result["count"] / 3.0, 1.0)

        # Calculate overall suspicion score from rule-based analysis
        suspicion_score = triggered_weight / total_weight if total_weight > 0 else 0.0
        suspicion_score = min(max(suspicion_score, 0.0), 1.0)  # Clamp to [0, 1]

        return {
            "flags": flags,
            "suspicion_score": round(suspicion_score, 4),
            "details": details,
            "total_flags": len(flags)
        }

    def _check_promotional_words(self, text):
        """Check for overly promotional words."""
        keywords_str = self.rules.get("promotional_keywords", {}).get("value", "")
        keywords = [kw.strip().lower() for kw in keywords_str.split(",") if kw.strip()]
        text_lower = text.lower()
        found = [kw for kw in keywords if kw in text_lower]
        return {"found": len(found) > 0, "count": len(found), "words": found}

    def _check_negative_spam(self, text):
        """Check for excessively negative keywords (competitor sabotage)."""
        keywords_str = self.rules.get("negative_spam_keywords", {}).get("value", "")
        keywords = [kw.strip().lower() for kw in keywords_str.split(",") if kw.strip()]
        text_lower = text.lower()
        found = [kw for kw in keywords if kw in text_lower]
        return {"found": len(found) > 0, "count": len(found), "words": found}

    def _check_review_length(self, text):
        """Check if review is too short."""
        char_count = len(text.strip())
        word_count = len(text.strip().split())
        threshold = int(self.rules.get("short_review_warning", {}).get("value", "50"))
        return {
            "char_count": char_count,
            "word_count": word_count,
            "is_short": char_count < threshold,
            "threshold": threshold
        }

    def _check_excessive_punctuation(self, text):
        """Check for excessive punctuation marks."""
        if len(text) == 0:
            return {"ratio": 0.0, "is_excessive": False, "punct_count": 0}
        punct_count = sum(1 for c in text if c in "!?...!!???")
        ratio = punct_count / len(text)
        threshold = float(self.rules.get("excessive_punctuation_ratio", {}).get("value", "0.15"))
        return {
            "ratio": round(ratio, 4),
            "is_excessive": ratio > threshold,
            "punct_count": punct_count,
            "threshold": threshold
        }

    def _check_excessive_caps(self, text):
        """Check for excessive use of capital letters."""
        letters = [c for c in text if c.isalpha()]
        if len(letters) == 0:
            return {"ratio": 0.0, "is_excessive": False}
        upper_count = sum(1 for c in letters if c.isupper())
        ratio = upper_count / len(letters)
        threshold = float(self.rules.get("excessive_caps_ratio", {}).get("value", "0.5"))
        return {
            "ratio": round(ratio, 4),
            "is_excessive": ratio > threshold,
            "upper_count": upper_count,
            "total_letters": len(letters),
            "threshold": threshold
        }

    def _check_repetition(self, text):
        """Check for repeated words or phrases."""
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        # Filter out very short common words
        stop_words = {"the", "a", "an", "is", "it", "in", "to", "and", "of", "for", "on", "at", "i", "my", "me"}
        words = [w for w in words if w not in stop_words and len(w) > 2]

        if len(words) == 0:
            return {"ratio": 0.0, "is_repetitive": False, "top_repeated": []}

        word_counts = Counter(words)
        # Count words that appear more than once
        repeated = {w: c for w, c in word_counts.items() if c > 1}
        repeated_count = sum(c - 1 for c in repeated.values())  # Extra occurrences
        ratio = repeated_count / len(words) if len(words) > 0 else 0.0

        threshold = float(self.rules.get("repetition_threshold", {}).get("value", "0.3"))
        top_repeated = sorted(repeated.keys(), key=lambda w: repeated[w], reverse=True)

        return {
            "ratio": round(ratio, 4),
            "is_repetitive": ratio > threshold,
            "top_repeated": top_repeated[:5],
            "threshold": threshold
        }

    def _check_generic_language(self, text):
        """Check for generic/vague language that lacks specific product details."""
        generic_phrases = [
            "great product", "love it", "highly recommend", "works great",
            "very good", "good quality", "nice product", "as described",
            "fast shipping", "exactly what i needed", "five stars",
            "would buy again", "perfect", "just what i wanted",
            "as advertised", "as expected", "happy with purchase"
        ]
        text_lower = text.lower()
        found = [phrase for phrase in generic_phrases if phrase in text_lower]
        return {
            "is_generic": len(found) >= 2,
            "count": len(found),
            "phrases": found
        }
