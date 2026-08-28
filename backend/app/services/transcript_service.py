import re
from typing import List, Dict, Any, Optional
from app.models.domain import TranscriptTurn

class TranscriptService:
    @staticmethod
    def parse_raw_text_to_turns(raw_text: str) -> List[TranscriptTurn]:
        """
        Parses raw transcript text formatted like:
        Interviewer: Hello, let's start...
        Candidate: Sure, thank you...
        or [00:01:23] Interviewer: ...
        """
        lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
        turns: List[TranscriptTurn] = []
        turn_id = 1
        
        speaker_pattern = re.compile(
            r'^(?:\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*)?(Interviewer|Candidate|Panelist|Speaker\s*\d+|[A-Z][a-zA-Z\s]+):\s*(.*)', 
            re.IGNORECASE
        )
        
        current_speaker = "Interviewer"
        current_timestamp = None
        current_buffer = []

        for line in lines:
            match = speaker_pattern.match(line)
            if match:
                if current_buffer:
                    full_text = " ".join(current_buffer)
                    turns.append(TranscriptTurn(
                        turn_id=turn_id,
                        speaker=current_speaker,
                        timestamp_start=current_timestamp,
                        text=full_text,
                        token_count=len(full_text.split())
                    ))
                    turn_id += 1
                    current_buffer = []
                
                timestamp, speaker_label, content = match.groups()
                current_timestamp = timestamp
                norm_speaker = "Candidate" if "candidate" in speaker_label.lower() else "Interviewer"
                current_speaker = norm_speaker
                current_buffer.append(content)
            else:
                current_buffer.append(line)
                
        if current_buffer:
            full_text = " ".join(current_buffer)
            turns.append(TranscriptTurn(
                turn_id=turn_id,
                speaker=current_speaker,
                timestamp_start=current_timestamp,
                text=full_text,
                token_count=len(full_text.split())
            ))

        return turns

    @staticmethod
    def build_transcript_text(turns: List[TranscriptTurn]) -> str:
        formatted = []
        for t in turns:
            prefix = f"[Turn {t.turn_id}] {t.speaker}"
            if t.timestamp_start:
                prefix += f" ({t.timestamp_start})"
            formatted.append(f"{prefix}: {t.text}")
        return "\n\n".join(formatted)

    @staticmethod
    def get_turn_by_id(turns: List[TranscriptTurn], turn_id: int) -> Optional[TranscriptTurn]:
        for t in turns:
            if t.turn_id == turn_id:
                return t
        return None

