import pytest
from src.core.types import TranscriptSegment, ActionItem, MeetingSummary

def test_transcript_segment_creation():
    seg = TranscriptSegment(start=1.5, end=4.2, speaker="Alice", text="Hello world")
    assert seg.start == 1.5
    assert seg.end == 4.2
    assert seg.speaker == "Alice"
    assert seg.text == "Hello world"

def test_action_item_defaults():
    item = ActionItem(task="Deploy staging environment")
    assert item.owner == "Unassigned"
    assert item.deadline == "None specified"
    assert item.priority == "MEDIUM"

def test_meeting_summary_model():
    summary = MeetingSummary(title="Weekly Standup", duration_seconds=120.5)
    assert summary.title == "Weekly Standup"
    assert summary.duration_seconds == 120.5
    assert summary.action_items == []

