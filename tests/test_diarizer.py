import pytest
from src.core.diarizer import HeuristicDiarizer
from src.core.types import TranscriptSegment

def test_parse_text_transcript_timestamps():
    sample = """[00:10] Alex: Hello team.
[00:25] Sarah: Hi Alex, I have an update."""
    segments = HeuristicDiarizer.parse_text_transcript(sample)
    assert len(segments) == 2
    assert segments[0].speaker == "Alex"
    assert segments[0].start == 10.0
    assert segments[1].speaker == "Sarah"
    assert segments[1].start == 25.0

def test_diarize_pause_detection():
    diarizer = HeuristicDiarizer(["Alice", "Bob"])
    segments = [
        TranscriptSegment(start=0.0, end=2.0, text="First statement"),
        # Gap > 1.8s should trigger turn
        TranscriptSegment(start=5.0, end=7.0, text="Second statement after pause"),
    ]
    diarized = diarizer.diarize_segments(segments)
    assert len(diarized) == 2
    assert diarized[0].speaker == "Alice"
    assert diarized[1].speaker == "Bob"

def test_self_intro_detection():
    diarizer = HeuristicDiarizer(["Speaker A", "Speaker B"])
    segments = [
        TranscriptSegment(start=0.0, end=3.0, text="Hello everyone, this is Jordan speaking today.")
    ]
    diarized = diarizer.diarize_segments(segments)
    assert diarized[0].speaker == "Jordan"

