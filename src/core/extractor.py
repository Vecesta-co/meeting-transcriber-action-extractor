from typing import List, Optional
from .types import ActionItem, MeetingSummary, TranscriptSegment
from .nlp_rules import RuleBasedActionExtractor
from ..providers.base import BaseLLMProvider

def summarize_agenda_and_bullets(segments: List[TranscriptSegment]) -> List[str]:
    """Generates high-level discussion points from segment transcript text."""
    if not segments:
        return ["No discussion recorded."]
    
    bullets: List[str] = []
    # Identify key declarative sentences across speakers
    seen = set()
    for seg in segments:
        text = seg.text.strip()
        if len(text) > 30 and seg.speaker not in seen:
            bullets.append(f"{seg.speaker} highlighted: {text}")
            seen.add(seg.speaker)
        if len(bullets) >= 4:
            break

    if not bullets:
        bullets = [seg.text for seg in segments[:3]]
    return bullets

def extract_meeting_insights(
    segments: List[TranscriptSegment],
    provider: Optional[BaseLLMProvider] = None,
    title: str = "Sprint Review & Action Items"
) -> MeetingSummary:
    """End-to-end extraction from transcript segments into structured MeetingSummary."""
    if not segments:
        return MeetingSummary(title=title, duration_seconds=0.0)

    # Derive attendees from speakers
    attendees = sorted(list({seg.speaker for seg in segments if seg.speaker}))

    # Calculate total duration
    duration = max(seg.end for seg in segments) if segments else 0.0

    # Extract action items: Use LLM if available, otherwise deterministic rule extractor
    action_items: List[ActionItem] = []
    if provider:
        try:
            full_transcript = "\n".join(
                f"[{int(seg.start // 60):02d}:{int(seg.start % 60):02d}] {seg.speaker}: {seg.text}"
                for seg in segments
            )
            action_items = provider.extract_action_items(full_transcript)
        except Exception as e:
            # Fallback to rule engine if LLM fails
            action_items = RuleBasedActionExtractor.extract_from_segments(segments)
    else:
        action_items = RuleBasedActionExtractor.extract_from_segments(segments)

    # Derive high-level summary points
    summary_bullets = summarize_agenda_and_bullets(segments)

    return MeetingSummary(
        title=title,
        attendees=attendees,
        agenda_topics=["Sprint Progress", "Technical Blockers", "Action Assignments"],
        summary_points=summary_bullets,
        action_items=action_items,
        duration_seconds=duration,
        segments=segments
    )

