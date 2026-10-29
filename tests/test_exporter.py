import json
import pytest
from src.core.exporter import MeetingExporter
from src.core.types import MeetingSummary, ActionItem, TranscriptSegment

def test_markdown_exporter():
    summary = MeetingSummary(
        title="Sprint Sync",
        duration_seconds=125.0,
        attendees=["Alex", "Sarah"],
        summary_points=["Team discussed sprint progress"],
        action_items=[
            ActionItem(
                task="Deploy staging database",
                owner="Sarah",
                deadline="by Friday",
                priority="HIGH",
                context_quote="I will deploy the staging database migration by Friday.",
                timestamp="00:15"
            )
        ],
        segments=[
            TranscriptSegment(start=0.0, end=15.0, speaker="Sarah", text="I will deploy the staging database migration by Friday.")
        ]
    )

    md = MeetingExporter.to_markdown(summary)
    assert "# 📝 Sprint Sync" in md
    assert "Sarah" in md
    assert "Deploy staging database" in md
    assert "🔴 High" in md
    assert "Vecesta.co" in md

def test_json_exporter():
    summary = MeetingSummary(
        title="JSON Test",
        action_items=[ActionItem(task="Write tests", owner="Alex")]
    )
    raw_json = MeetingExporter.to_json(summary)
    data = json.loads(raw_json)
    assert data["title"] == "JSON Test"
    assert len(data["action_items"]) == 1
    assert data["action_items"][0]["owner"] == "Alex"

def test_csv_exporter():
    summary = MeetingSummary(
        action_items=[
            ActionItem(task="Fix bug", owner="Jordan", deadline="Tomorrow", priority="HIGH")
        ]
    )
    csv_str = MeetingExporter.to_csv(summary)
    assert "Task,Owner,Deadline,Priority" in csv_str
    assert "Fix bug,Jordan,Tomorrow,HIGH" in csv_str

def test_srt_exporter():
    summary = MeetingSummary(
        segments=[
            TranscriptSegment(start=1.5, end=4.2, speaker="Alex", text="Hello team")
        ]
    )
    srt = MeetingExporter.to_srt(summary)
    assert "1" in srt
    assert "00:00:01,500 --> 00:00:04,200" in srt
    assert "[Alex] Hello team" in srt

