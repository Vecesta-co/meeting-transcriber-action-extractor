import os
from typing import List, Optional
from .types import TranscriptSegment

class FasterWhisperTranscriber:
    """Transcription pipeline utilizing faster-whisper (CTranslate2) with automatic hardware fallback."""

    def __init__(self, model_size: str = "base", device: str = "auto", compute_type: str = "default"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None
        self._available = False
        self._check_library()

    def _check_library(self):
        try:
            import faster_whisper # type: ignore
            self._available = True
        except ImportError:
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def load_model(self):
        if not self._available:
            raise ImportError(
                "faster-whisper is not installed. Run 'pip install faster-whisper' or run in text transcript mode."
            )
        if self._model is None:
            from faster_whisper import WhisperModel # type: ignore
            device = "cuda" if self.device == "cuda" else ("cpu" if self.device == "cpu" else "auto")
            self._model = WhisperModel(self.model_size, device=device, compute_type=self.compute_type)
        return self._model

    def transcribe_audio(self, audio_path: str) -> List[TranscriptSegment]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = self.load_model()
        segments_generator, info = model.transcribe(audio_path, beam_size=5, vad_filter=True)

        results: List[TranscriptSegment] = []
        for segment in segments_generator:
            results.append(TranscriptSegment(
                start=float(segment.start),
                end=float(segment.end),
                speaker="Speaker A",
                text=segment.text.strip()
            ))

        return results

    @staticmethod
    def mock_transcribe(audio_path: str) -> List[TranscriptSegment]:
        """Provides deterministic mock segments for tests and offline demonstrations."""
        return [
            TranscriptSegment(start=0.0, end=4.5, speaker="Alex", text="Good morning everyone, let's start the sprint review."),
            TranscriptSegment(start=5.0, end=11.2, speaker="Sarah", text="Sure. I will deploy the staging database migration by Friday."),
            TranscriptSegment(start=12.0, end=18.4, speaker="Alex", text="Thanks Sarah. Jordan, can you please review the frontend PR by tomorrow?"),
            TranscriptSegment(start=19.0, end=23.1, speaker="Jordan", text="Absolutely, I'll take care of the PR review today before 5pm."),
            TranscriptSegment(start=24.0, end=29.5, speaker="Alex", text="Great, and let's update the public API documentation before next Tuesday."),
        ]

