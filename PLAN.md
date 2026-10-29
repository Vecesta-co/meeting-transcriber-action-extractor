# PLAN.md: meeting-transcriber-action-extractor (Vecesta.co)

> **High-Performance Audio Meeting Transcriber & Action-Item Extractor with Owner & Deadline Grounding**  
> **Reference Baseline**: `SYSTRAN/faster-whisper`  
> **Author**: Vecesta.co (`vecesta.co@gmail.com`)  
> **Target Release**: v1.0.0 (MIT License)

---

## 1. Executive Summary & Scope

Engineering and executive teams waste hours manually reviewing meeting recordings to identify commitments, task assignments, and target deadlines. While `faster-whisper` offers fast, accurate speech-to-text powered by CTranslate2, it only outputs raw text and segment timestamps. It lacks speaker turn tracking, action item extraction, owner assignment, deadline normalization, and export capabilities. Commercial SaaS solutions (Otter.ai, Fireflies.ai) charge recurring monthly fees, require cloud audio uploads, and compromise corporate privacy.

`meeting-transcriber-action-extractor` is a high-performance, private, local-first meeting intelligence system. It wraps CTranslate2 / Whisper transcription with:
1. **Speaker Turn & Energy Diarization**: Associates transcribed segments with conversational speakers (`Speaker A`, `Speaker B`, or mapped real names).
2. **Context-Aware Action Item Extractor**: Extracts action items with active imperative task descriptions, assigned owners, explicit or relative deadlines ("by next Friday", "EOD tomorrow", ISO format), priority levels, and timestamped audio citations.
3. **Multi-Model & Offline Zero-Cost Intelligence**:
   - Local Ollama (`llama3.2`, `mistral`, `qwen2.5`) for 100% private processing.
   - Google Gemini API free tier.
   - OpenAI API.
   - **Deterministic Heuristic NLP Extractor**: Built-in grammatical pattern matcher (modal verbs: "I will handle...", "Can you deploy...", "We need this by Friday") that extracts action items with zero API keys and zero network access.
4. **Export Formats**: Markdown Meeting Minutes with summary and task tables, structured JSON, CSV (ready for Jira/Linear import), and SRT/VTT subtitles.

### In Scope
- Fast transcription pipeline with fallback and mock modes for environments without AV/GPU libraries.
- Heuristic speaker segmentation and conversational turn chunking.
- Action item extraction engine with owner and deadline resolution.
- Multi-format exporters: Markdown, JSON, CSV, SRT, VTT.
- Command-line interface (`meeting-transcriber transcribe <audio-file>` and `meeting-transcriber extract <transcript-file>`).
- 100% offline rule-based test fixtures and unit tests.

### Out of Scope (v1.0.0)
- Real-time live microphone streaming transcription (batch file processing first).
- Direct bi-directional OAuth calendar synchronization.

---

## 2. Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        Audio Input                          │
│               (.mp3, .wav, .m4a, .flac, .ogg)               │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Transcription & Diarization                 │
│  - WhisperModel (faster-whisper / CTranslate2)              │
│  - VAD (Voice Activity Detection) filter                    │
│  - Timestamped segments [start_s -> end_s]                  │
│  - Speaker turn heuristic attribution (Speaker A/B...)      │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Action-Item Extraction Engine               │
│  - Task: Imperative action verb ("Configure staging DB")    │
│  - Owner: Named attendee or explicit "Unassigned"           │
│  - Deadline: Extracted date/timeframe normalized            │
│  - Priority: HIGH | MEDIUM | LOW                            │
│  - Citation: Exact timestamp snippet in transcript          │
│                                                             │
│  Intelligence Providers:                                    │
│    ├── Ollama (Local offline)                               │
│    ├── Gemini API (Free tier)                               │
│    ├── OpenAI API                                           │
│    └── Deterministic NLP Heuristic Extractor (Offline)      │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Export & Publishing                      │
│  ├── Executive Meeting Minutes (Markdown Table)             │
│  ├── Machine-readable JSON Schema                           │
│  ├── CSV Task Table (Jira / Linear / Asana compatible)      │
│  └── Subtitles (.srt, .vtt)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack & Dependencies

| Component | Technology | Rationale & Version |
|---|---|---|
| **Runtime** | Python 3.10+ / 3.11+ | Industry standard for speech, ML, and NLP workflows. |
| **Speech-to-Text** | `faster-whisper` (CTranslate2) | 4x faster than vanilla Whisper, 70% lower memory usage. |
| **Data Validation** | `pydantic` (v2.0+) | Strict typed validation for action items and meeting metadata. |
| **CLI Framework** | `argparse` / `click` | Ergonomic command-line tool with zero bloat. |
| **Testing** | `pytest` & `pytest-cov` | Fast, extensible testing with branch coverage. |

---

## 4. Repository Structure

```
meeting-transcriber-action-extractor/
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── src/
│   ├── __init__.py
│   ├── cli.py                     # Command-line interface
│   ├── config.py                  # Environment settings & options
│   ├── core/
│   │   ├── __init__.py
│   │   ├── types.py               # Pydantic data schemas
│   │   ├── transcriber.py         # faster-whisper integration + mock mode
│   │   ├── diarizer.py            # Speaker segmentation heuristic
│   │   ├── extractor.py           # Action item extraction pipeline
│   │   ├── nlp_rules.py           # Deterministic offline rule extractor
│   │   └── exporter.py            # Markdown, JSON, CSV, SRT exporters
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       ├── gemini.py
│       ├── ollama.py
│       └── openai.py
├── tests/
│   ├── __init__.py
│   ├── test_types.py
│   ├── test_diarizer.py
│   ├── test_nlp_rules.py
│   ├── test_extractor.py
│   ├── test_exporter.py
│   └── test_cli.py
├── fixtures/
│   └── sample_meeting.txt
├── pyproject.toml
├── Dockerfile
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── PLAN.md
└── DEVLOG.md
```

---

## 5. "How We Are Different & More Capable"

| Feature | `SYSTRAN/faster-whisper` | Otter.ai / Fireflies (SaaS) | **`meeting-transcriber` (Vecesta.co)** |
|---|---|---|---|
| **Transcription Speed** | 4x Whisper (C++ engine) | Cloud queue delays | **High speed local CTranslate2** |
| **Action Items** | ❌ None (raw text only) | Proprietary cloud model | **✅ Structured Tasks, Owners, Deadlines** |
| **Privacy** | Local file | Audio uploaded to cloud servers | **✅ 100% Local-first (Air-gap friendly)** |
| **Cost** | Free (Open Source) | $18-$40 / user / month | **✅ 100% Free & Open Source (MIT)** |
| **Offline Fallback** | Transcription only | ❌ Requires internet | **✅ Built-in Deterministic NLP Extractor** |
| **Export Formats** | Raw text / segments | Restricted web view / PDF | **✅ Markdown, JSON, CSV, SRT, VTT** |
| **Owner Mapping** | ❌ None | Basic heuristic | **✅ Conversational turn-taking attribution** |

---

## 6. Test Strategy & Quality Assurance
- Target statement coverage: >= 85%.
- Hermetic test suite testing parsing, diarization, rule-based extraction, and export formatters.
- Zero external network dependency for standard test runs.

