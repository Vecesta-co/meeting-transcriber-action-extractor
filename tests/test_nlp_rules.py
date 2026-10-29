import pytest
from src.core.nlp_rules import (
    RuleBasedActionExtractor,
    extract_deadline,
    resolve_priority,
    clean_task,
)
from src.core.types import TranscriptSegment

def test_extract_deadline_patterns():
    text1, deadline1 = extract_deadline("Deploy the new database by Friday")
    assert "Friday" in deadline1
    assert "Deploy the new database" in text1

    text2, deadline2 = extract_deadline("Review the PR before end of day tomorrow")
    assert "tomorrow" in deadline2 or "end of day" in deadline2

    text3, deadline3 = extract_deadline("General discussion without date")
    assert deadline3 == "None specified"

def test_resolve_priority():
    assert resolve_priority("This is urgent and blocker") == "HIGH"
    assert resolve_priority("Nice to have when you have time") == "LOW"
    assert resolve_priority("Standard task for sprint") == "MEDIUM"

def test_direct_assignment_rule():
    segments = [
        TranscriptSegment(start=10.0, end=15.0, speaker="Alex", text="Jordan, can you please review the frontend PR by tomorrow?")
    ]
    items = RuleBasedActionExtractor.extract_from_segments(segments)
    assert len(items) == 1
    assert items[0].owner == "Jordan"
    assert "Review the frontend" in items[0].task
    assert "tomorrow" in items[0].deadline

def test_first_person_commitment_rule():
    segments = [
        TranscriptSegment(start=20.0, end=25.0, speaker="Sarah", text="I will deploy the staging database migration by Friday.")
    ]
    items = RuleBasedActionExtractor.extract_from_segments(segments)
    assert len(items) == 1
    assert items[0].owner == "Sarah"
    assert "Deploy the staging database" in items[0].task
    assert "Friday" in items[0].deadline

