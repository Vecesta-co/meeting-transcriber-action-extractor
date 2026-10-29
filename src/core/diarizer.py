import re
from typing import List, Optional
from .types import TranscriptSegment

class HeuristicDiarizer:
    """Assigns and clusters conversational speaker turns based on acoustic pauses and conversational cues."""

    def __init__(self, known_speakers: Optional[List[str]] = None):
        self.known_speakers = known_speakers or ["Speaker A", "Speaker B"]

    def diarize_segments(self, segments: List[TranscriptSegment]) -> List[TranscriptSegment]:
        if not segments:
            return []

        diarized: List[TranscriptSegment] = []
        current_speaker_idx = 0
        current_speaker = self.known_speakers[current_speaker_idx]
        last_end_time = 0.0

        for seg in segments:
            text = seg.text.strip()

            # Check if speaker explicitly introduces themselves: "Hi everyone, Alex here" or "This is Sarah"
            intro_match = re.search(r'\b(?:this is|I am|it\'s|name is)\s+([A-Z][a-z]+)\b', text, re.IGNORECASE)
            if intro_match:
                speaker_name = intro_match.group(1).title()
                if speaker_name not in self.known_speakers:
                    self.known_speakers.append(speaker_name)
                current_speaker = speaker_name
            else:
                # Acoustic pause turn detection: A pause > 1.8s strongly indicates a speaker change in meetings
                pause_gap = seg.start - last_end_time if last_end_time > 0 else 0
                if pause_gap > 1.8:
                    current_speaker_idx = (current_speaker_idx + 1) % len(self.known_speakers)
                    current_speaker = self.known_speakers[current_speaker_idx]

            diarized.append(TranscriptSegment(
                start=seg.start,
                end=seg.end,
                speaker=current_speaker,
                text=seg.text
            ))

            last_end_time = seg.end

        return diarized

    @staticmethod
    def parse_text_transcript(raw_text: str) -> List[TranscriptSegment]:
        """Parses a raw formatted meeting text file (e.g. '[00:15] Alex: Hello everyone') into structured segments."""
        segments: List[TranscriptSegment] = []
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        current_time = 0.0
        for line in lines:
            # Pattern 1: [00:15] Alex: text OR [01:23 - 01:45] Sarah: text
            m_time_speaker = re.match(r'^(?:\[?(\d{1,2}):(\d{2})(?:\s*-\s*(\d{1,2}):(\d{2}))?\]?)\s*(?:([A-Za-z0-9_\s]+?):)?\s*(.+)$', line)
            if m_time_speaker:
                start_m, start_s = int(m_time_speaker.group(1)), int(m_time_speaker.group(2))
                start_sec = start_m * 60 + start_s

                if m_time_speaker.group(3) and m_time_speaker.group(4):
                    end_m, end_s = int(m_time_speaker.group(3)), int(m_time_speaker.group(4))
                    end_sec = end_m * 60 + end_s
                else:
                    end_sec = start_sec + 5.0

                speaker = m_time_speaker.group(5).strip() if m_time_speaker.group(5) else "Speaker A"
                text = m_time_speaker.group(6).strip()

                segments.append(TranscriptSegment(
                    start=float(start_sec),
                    end=float(end_sec),
                    speaker=speaker,
                    text=text
                ))
                current_time = end_sec
                continue

            # Pattern 2: SpeakerName: text
            m_speaker = re.match(r'^([A-Z][A-Za-z0-9_\s]{1,20}):\s*(.+)$', line)
            if m_speaker:
                speaker = m_speaker.group(1).strip()
                text = m_speaker.group(2).strip()
                segments.append(TranscriptSegment(
                    start=current_time,
                    end=current_time + 5.0,
                    speaker=speaker,
                    text=text
                ))
                current_time += 5.0
                continue

            # Pattern 3: Bare speech line
            segments.append(TranscriptSegment(
                start=current_time,
                end=current_time + 5.0,
                speaker="Speaker A",
                text=line
            ))
            current_time += 5.0

        return segments

