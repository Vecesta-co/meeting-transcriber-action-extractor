import pytest
from src.core.extractor import extract_meeting_insights
from src.core.types import TranscriptSegment

def test_extract_meeting_insights_end_to_end():
    segments = [
        TranscriptSegment(start=0.0, end=5.0, speaker="Alex", text="Good morning everyone, let's start."),
        TranscriptSegment(start=10.0, end=15.0, speaker="Sarah", text="I will deploy the staging database migration by Friday."),
        TranscriptSegment(start=20.0, end=25.0, speaker="Alex", text="Jordan, can you please review the frontend PR by tomorrow?"),
    ]
    summary = extract_meeting_insights(segments, title="Test Sprint Sync")

    assert summary.title == "Test Sprint Sync"
    assert "Alex" in summary.attendees
    assert "Sarah" in summary.attendees
    assert summary.duration_seconds == 25.0
    assert len(summary.action_items) == 2

    owners = {item.owner for item in summary.action_items}
    assert "Sarah" in owners
    assert "Jordan" in owners

