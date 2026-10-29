from typing import List, Optional
from pydantic import BaseModel, Field

class TranscriptSegment(BaseModel):
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    speaker: str = Field(default="Speaker A", description="Identified speaker name or ID")
    text: str = Field(..., description="Transcribed spoken text")

class ActionItem(BaseModel):
    task: str = Field(..., description="Actionable task beginning with an active verb")
    owner: str = Field(default="Unassigned", description="Individual responsible for task completion")
    deadline: str = Field(default="None specified", description="Target completion date or timeframe")
    priority: str = Field(default="MEDIUM", description="Priority level: HIGH, MEDIUM, LOW")
    context_quote: str = Field(default="", description="Original quote where task was discussed")
    timestamp: str = Field(default="00:00", description="Timestamp location in the audio/transcript")

class MeetingSummary(BaseModel):
    title: str = Field(default="Meeting Notes", description="Generated or user-defined meeting title")
    date: Optional[str] = Field(default=None, description="Date of the meeting")
    attendees: List[str] = Field(default_factory=list, description="List of recognized attendees/speakers")
    agenda_topics: List[str] = Field(default_factory=list, description="Key discussion topics")
    summary_points: List[str] = Field(default_factory=list, description="High-level meeting summary bullets")
    action_items: List[ActionItem] = Field(default_factory=list, description="Extracted actionable commitments")
    duration_seconds: float = Field(default=0.0, description="Total meeting duration in seconds")
    segments: List[TranscriptSegment] = Field(default_factory=list, description="Underlying transcript segments")

