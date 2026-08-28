import re
import difflib
from typing import List, Optional, Tuple, Dict, Any
from app.models.domain import TranscriptTurn, EvidenceCitation

class EvidenceEngine:
    def __init__(self, turns: List[TranscriptTurn]):
        self.turns = turns
        self.turns_map: Dict[int, TranscriptTurn] = {t.turn_id: t for t in turns}

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalizes text for robust comparison."""
        text = text.lower()
        text = re.sub(r'[\'"“”‘’`.,;:!?()[\]{}]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def verify_citation(self, citation: EvidenceCitation) -> EvidenceCitation:
        """
        Verifies whether the quote cited in `citation` exists in the referenced turn,
        or locates the exact turn across the transcript, computing a rigorous grounding score.
        """
        norm_quote = self.normalize_text(citation.verbatim_quote)
        if not norm_quote:
            citation.is_verified = False
            citation.grounding_score = 0.0
            citation.verification_notes = "Empty quote provided."
            return citation

        # 1. First check if there is an EXACT verbatim match anywhere across all turns
        for turn in self.turns:
            norm_turn = self.normalize_text(turn.text)
            if norm_quote in norm_turn:
                citation.is_verified = True
                citation.grounding_score = 1.0
                citation.speaker = turn.speaker
                if turn.turn_id == citation.turn_id:
                    citation.verification_notes = f"Exact verbatim match in Turn {turn.turn_id} ({turn.speaker})."
                else:
                    citation.turn_id = turn.turn_id
                    citation.verification_notes = f"Exact verbatim match located in Turn {turn.turn_id} ({turn.speaker}) [relocated from original citation]."
                return citation

        # 2. Check targeted turn for strong fuzzy match
        target_turn = self.turns_map.get(citation.turn_id)
        if target_turn:
            norm_turn = self.normalize_text(target_turn.text)
            similarity = difflib.SequenceMatcher(None, norm_quote, norm_turn).quick_ratio()
            
            words_quote = norm_quote.split()
            words_turn = norm_turn.split()
            quote_len = len(words_quote)
            
            best_sub_ratio = 0.0
            if quote_len <= len(words_turn):
                for i in range(len(words_turn) - quote_len + 1):
                    window = " ".join(words_turn[i : i + quote_len + 3])
                    ratio = difflib.SequenceMatcher(None, norm_quote, window).ratio()
                    if ratio > best_sub_ratio:
                        best_sub_ratio = ratio
            
            effective_score = max(similarity, best_sub_ratio)
            if effective_score >= 0.82:
                citation.is_verified = True
                citation.grounding_score = round(effective_score, 3)
                citation.speaker = target_turn.speaker
                citation.verification_notes = f"High-confidence fuzzy match ({round(effective_score*100, 1)}%) in Turn {target_turn.turn_id}."
                return citation

        # 3. Fuzzy search across all turns to find best matching turn
        best_match_turn: Optional[TranscriptTurn] = None
        highest_score = 0.0

        for turn in self.turns:
            norm_turn = self.normalize_text(turn.text)
            words_turn = norm_turn.split()
            words_quote = norm_quote.split()
            quote_len = len(words_quote)
            
            best_turn_ratio = difflib.SequenceMatcher(None, norm_quote, norm_turn).ratio()
            if quote_len <= len(words_turn):
                for i in range(len(words_turn) - quote_len + 1):
                    window = " ".join(words_turn[i : i + quote_len + 3])
                    ratio = difflib.SequenceMatcher(None, norm_quote, window).ratio()
                    if ratio > best_turn_ratio:
                        best_turn_ratio = ratio
            
            if best_turn_ratio > highest_score:
                highest_score = best_turn_ratio
                best_match_turn = turn

        if best_match_turn and highest_score >= 0.78:
            citation.turn_id = best_match_turn.turn_id
            citation.speaker = best_match_turn.speaker
            citation.is_verified = True
            citation.grounding_score = round(highest_score, 3)
            citation.verification_notes = f"Relocated and verified in Turn {best_match_turn.turn_id} ({round(highest_score*100, 1)}% match)."
            return citation

        # 4. Failed verification / Hallucinated quote
        citation.is_verified = False
        citation.grounding_score = round(highest_score, 3)
        citation.verification_notes = f"Quote could not be grounded in transcript (Best match: {round(highest_score*100, 1)}%). Flagged as unverified."
        return citation

    def batch_verify_citations(self, citations: List[EvidenceCitation]) -> List[EvidenceCitation]:
        return [self.verify_citation(c) for c in citations]

