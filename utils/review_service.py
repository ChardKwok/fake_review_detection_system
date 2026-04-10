"""
Review Analysis Service Module
Combines ML model prediction with rule-based text analysis to produce
a final classification, credibility score, and explanation flags.
This is the core business logic that brings together all analysis components.
"""
from utils.ml_model import get_model
from utils.text_analyzer import TextAnalyzer
from utils.database import save_analysis_result
from config import Config


class ReviewService:
    """
    Main service for analyzing product reviews.
    Combines:
    1. TF-IDF + Naive Bayes ML prediction
    2. Rule-based suspicious pattern detection
    3. Final classification and credibility scoring
    """

    def __init__(self):
        self.text_analyzer = TextAnalyzer()

    def analyze_review(self, review_text):
        """
        Perform complete analysis on a review text.

        Args:
            review_text (str): The review text to analyze.

        Returns:
            dict: Complete analysis result including classification,
                  credibility score, ML prediction, and explanation flags.
        """
        # Input validation (Epic 5)
        validation = self._validate_input(review_text)
        if not validation["is_valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "error_type": validation["error_type"]
            }

        # Step 1: ML Model Prediction
        model = get_model()
        ml_result = None
        if model.is_loaded:
            ml_result = model.predict(review_text)

        # Step 2: Rule-based Text Analysis
        text_analysis = self.text_analyzer.analyze(review_text)

        # Step 3: Combine scores for final classification
        final_result = self._compute_final_result(ml_result, text_analysis, review_text)

        # Step 4: Save to history
        record_id = save_analysis_result(
            review_text=review_text,
            classification=final_result["classification"],
            credibility_score=final_result["credibility_score"],
            fake_probability=final_result["fake_probability"],
            flags=final_result["flags"]
        )

        final_result["id"] = record_id
        final_result["success"] = True
        return final_result

    def _validate_input(self, text):
        """
        Validate review input text (Epic 5: Input Validation).

        Returns:
            dict: {"is_valid": bool, "error": str or None, "error_type": str or None}
        """
        if text is None or not isinstance(text, str):
            return {
                "is_valid": False,
                "error": "Review text is required and must be a string.",
                "error_type": "missing_input"
            }

        stripped = text.strip()
        if len(stripped) == 0:
            return {
                "is_valid": False,
                "error": "Review text cannot be empty. Please enter a review to analyze.",
                "error_type": "empty_input"
            }

        if len(stripped) < Config.MIN_REVIEW_LENGTH:
            return {
                "is_valid": False,
                "error": f"Review text is too short (minimum {Config.MIN_REVIEW_LENGTH} characters). Please enter a longer review.",
                "error_type": "too_short"
            }

        return {"is_valid": True, "error": None, "error_type": None}

    def _compute_final_result(self, ml_result, text_analysis, review_text):
        """
        Combine ML prediction and rule-based analysis into a final result.

        The final fake probability is a weighted combination:
        - 70% from ML model (if available)
        - 30% from rule-based analysis

        If ML model is not available, use only rule-based analysis.
        """
        flags = text_analysis["flags"]

        if ml_result is not None:
            # Weighted combination: 70% ML + 30% Rules
            ml_fake_prob = ml_result["fake_probability"]
            rule_suspicion = text_analysis["suspicion_score"]
            combined_fake_prob = (0.7 * ml_fake_prob) + (0.3 * rule_suspicion)
        else:
            # Fallback: only rule-based
            combined_fake_prob = text_analysis["suspicion_score"]
            ml_fake_prob = None

        # Clamp probability
        combined_fake_prob = min(max(combined_fake_prob, 0.0), 1.0)

        # Credibility score (inverse of fake probability, 0-100 scale)
        credibility_score = round((1.0 - combined_fake_prob) * 100, 1)

        # Classification based on thresholds
        if combined_fake_prob >= Config.FAKE_THRESHOLD:
            classification = "Possibly Fake"
        elif combined_fake_prob <= Config.GENUINE_THRESHOLD:
            classification = "Likely Genuine"
        else:
            classification = "Uncertain"

        return {
            "classification": classification,
            "credibility_score": credibility_score,
            "fake_probability": round(combined_fake_prob, 4),
            "ml_prediction": ml_result,
            "rule_analysis": {
                "suspicion_score": text_analysis["suspicion_score"],
                "total_flags": text_analysis["total_flags"],
                "details": text_analysis["details"]
            },
            "flags": flags,
            "review_text": review_text,
            "review_length": len(review_text),
            "model_available": ml_result is not None
        }

    def reload_rules(self):
        """Reload detection rules from database."""
        self.text_analyzer.reload_rules()
