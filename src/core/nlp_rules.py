import re
from typing import List, Tuple
from .types import ActionItem, TranscriptSegment

DEADLINE_PATTERNS = [
    r'\b(?:by|before|until|due)\s+(?:the\s+)?(?:end\s+of\s+(?:the\s+)?(?:day|week|month|sprint)|eod|eow|tomorrow|tonight|next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|week|month)|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2}/\d{1,2}(?:/\d{2,4})?|\d{1,2}\s*(?:am|pm))\b',
    r'\b(?:asap|immediately|first thing tomorrow)\b',
]

def format_timestamp(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def extract_deadline(text: str) -> Tuple[str, str]:
    """Extracts deadline phrase if present and returns (cleaned_text, deadline_string)."""
    for pattern in DEADLINE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            deadline_str = match.group(0).strip()
            cleaned = text[:match.start()] + text[match.end():]
            return cleaned.strip(' ,.;'), deadline_str
    return text.strip(' ,.;'), "None specified"

def resolve_priority(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ['urgent', 'critical', 'asap', 'blocker', 'immediately', 'p0', 'high priority']):
        return "HIGH"
    if any(k in lower for k in ['low priority', 'nice to have', 'when you have time', 'no rush', 'backlog', 'p3']):
        return "LOW"
    return "MEDIUM"

def clean_task(text: str) -> str:
    cleaned = re.sub(r'^(?:to|and|also|just|please|make sure to|be sure to)\s+', '', text.strip(), flags=re.IGNORECASE)
    cleaned = cleaned.strip(' ,.;')
    if not cleaned:
        return ""
    return cleaned[0].upper() + cleaned[1:]

class RuleBasedActionExtractor:
    """Deterministic, zero-cost, offline rule-based action item extractor."""

    @classmethod
    def extract_from_segments(cls, segments: List[TranscriptSegment]) -> List[ActionItem]:
        items: List[ActionItem] = []

        for seg in segments:
            text = seg.text.strip()
            speaker = seg.speaker or "Speaker A"
            timestamp = format_timestamp(seg.start)

            # Rule 1: Direct Assignment ("Alex, can you / please deploy the database by Friday")
            m1 = re.search(
                r'\b([A-Z][a-z]+),\s*(?:can you|could you|please|you should|will you|you need to)\s+([^.?!]+)',
                text,
                re.IGNORECASE
            )
            if m1:
                assigned_name = m1.group(1).title()
                raw_task = m1.group(2)
                task_clean, deadline = extract_deadline(raw_task)
                task_final = clean_task(task_clean)
                if len(task_final) > 5:
                    items.append(ActionItem(
                        task=task_final,
                        owner=assigned_name,
                        deadline=deadline,
                        priority=resolve_priority(text),
                        context_quote=text,
                        timestamp=timestamp
                    ))
                    continue

            # Rule 2: Explicit third-person ownership ("Alex will handle the deployment")
            m2 = re.search(
                r'\b([A-Z][a-z]+)\s+(?:will|is going to|agreed to)\s+(?:handle|take care of|own|lead|prepare|build|ship|review|fix|investigate|deploy)\s+([^.?!]+)',
                text,
                re.IGNORECASE
            )
            if m2:
                owner = m2.group(1).title()
                raw_task = m2.group(0).split(owner, 1)[1].strip()
                task_clean, deadline = extract_deadline(raw_task)
                task_final = clean_task(task_clean)
                if len(task_final) > 5:
                    items.append(ActionItem(
                        task=task_final,
                        owner=owner,
                        deadline=deadline,
                        priority=resolve_priority(text),
                        context_quote=text,
                        timestamp=timestamp
                    ))
                    continue

            # Rule 3: First-person commitment ("I will deploy the fix by tomorrow")
            m3 = re.search(
                r'\b(?:I will|I\'ll|I am going to|I can)\s+(?:handle|take care of|do|prepare|build|ship|review|fix|write|implement|investigate|deploy|send|check)\s+([^.?!]+)',
                text,
                re.IGNORECASE
            )
            if m3:
                raw_task = m3.group(0)
                task_clean, deadline = extract_deadline(raw_task)
                # Strip leading I will / I'll
                task_action = re.sub(r'^(?:I will|I\'ll|I am going to|I can)\s+', '', task_clean, flags=re.IGNORECASE)
                task_final = clean_task(task_action)
                if len(task_final) > 5:
                    items.append(ActionItem(
                        task=task_final,
                        owner=speaker,
                        deadline=deadline,
                        priority=resolve_priority(text),
                        context_quote=text,
                        timestamp=timestamp
                    ))
                    continue

            # Rule 4: Team imperative ("We need to / We should / Let's update the docs by Friday")
            m4 = re.search(
                r'\b(?:Let\'s|We need to|We must|We should|Action item:?)\s+([^.?!]+)',
                text,
                re.IGNORECASE
            )
            if m4:
                raw_task = m4.group(1)
                task_clean, deadline = extract_deadline(raw_task)
                task_final = clean_task(task_clean)
                if len(task_final) > 5:
                    items.append(ActionItem(
                        task=task_final,
                        owner="Team",
                        deadline=deadline,
                        priority=resolve_priority(text),
                        context_quote=text,
                        timestamp=timestamp
                    ))
                    continue

        return items

