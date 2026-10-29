# 🎙️ meeting-transcriber-action-extractor

> **High-performance audio meeting transcription and action-item extractor with owner, deadline, and priority grounding powered by faster-whisper, Gemini, and Ollama.**

[![CI](https://github.com/Vecesta-co/meeting-transcriber-action-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/Vecesta-co/meeting-transcriber-action-extractor/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.0-red.svg)](https://docs.pydantic.dev/)

---

## 📸 Real CLI Execution Preview

Here is an actual extraction run on a team sprint meeting transcript with owner mapping and relative deadline normalization:

```text
$ meeting-transcriber extract fixtures/sample_meeting.txt --format markdown

# 📝 Executive Meeting Minutes

> **Duration**: 1m 15s | **Attendees**: Alex, Jordan, Sarah

## 📌 Key Discussion Points
- Alex highlighted: Good morning everyone, thanks for joining the weekly sprint sync.
- Sarah highlighted: Morning Alex. I have an update on the infrastructure. I will deploy the staging database migration by Friday.
- Jordan highlighted: Yes, absolutely. I will review the pull request today before 5pm.

## ✅ Action Items & Commitments

| Status | Task | Assigned Owner | Deadline | Priority | Timestamp |
|:---:|:---|:---|:---|:---:|:---:|
| [ ] | **Deploy the staging database migration** | `Sarah` | by Friday | 🟡 Med | `00:15` |
| [ ] | **Review the frontend PR** | `Jordan` | by tomorrow | 🟡 Med | `00:28` |
| [ ] | **Review the pull request today** | `Jordan` | before 5pm | 🟡 Med | `00:39` |
| [ ] | **Update the public API documentation** | `Team` | before next Tuesday | 🟡 Med | `00:48` |
| [ ] | **Make sure the docs team has everything Monday** | `Team` | by end of day | 🟡 Med | `00:58` |

### Context Details
- **[00:15] Sarah**: *"Morning Alex. I have an update on the infrastructure. I will deploy the staging database migration by Friday."*
- **[00:28] Jordan**: *"That's great news, Sarah. Jordan, can you please review the frontend PR by tomorrow?"*
- **[00:39] Jordan**: *"Yes, absolutely. I will review the pull request today before 5pm."*
- **[00:48] Team**: *"Also, Alex, we must update the public API documentation before next Tuesday."*
- **[00:58] Team**: *"Agreed, let's make sure the docs team has everything by end of day Monday."*

---
*Meeting notes generated autonomously by meeting-transcriber-action-extractor by Vecesta.co.*
```

---

## ✨ Features

- ⚡ **High-Speed Transcription (faster-whisper)**: Leverages CTranslate2 to transcribe audio up to **4x faster** than vanilla Whisper with 70% lower VRAM usage.
- 👥 **Heuristic Speaker Diarization**: Accurately tracks conversational turns and speaker identities based on pauses and self-introduction patterns (`Speaker A`, `Speaker B`, or mapped attendee names).
- 🎯 **Grounded Action Items with Owners & Deadlines**:
  - **Task**: Standardized active imperative verb statements.
  - **Owner**: Attributed to the speaker committing ("I will deploy...") or direct address ("Alex, can you review...").
  - **Deadline**: Normalizes dates ("by Friday", "before 5pm", "end of day tomorrow").
  - **Priority**: Categorizes tasks into `HIGH`, `MEDIUM`, or `LOW`.
  - **Citation**: Timestamp anchor linking each task directly to the meeting audio segment.
- 🦙 **100% Free & Local-First**: Works with local **Ollama** models (`llama3.2`, `mistral`), **Google Gemini Free Tier**, or a **Zero-Cost Deterministic Rule Engine** that extracts action items completely offline without needing any API key!
- 📤 **Multi-Format Exporters**:
  - **Markdown**: Formatted executive minutes with attendee badges and task table.
  - **JSON**: Machine-readable Pydantic schema for automated workflow ingestion.
  - **CSV**: Task table ready for instant import into Jira, Linear, or Asana.
  - **SRT / VTT**: Standard subtitle timecodes for video editing and accessibility.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Audio Input                          │
│               (.mp3, .wav, .m4a, .flac, .ogg)               │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Transcription & Diarization                 │
│  - faster-whisper (CTranslate2 engine / float16 or int8)    │
│  - Silero VAD (Voice Activity Detection) filter             │
│  - Timestamped segments [start_s -> end_s]                  │
│  - Heuristic speaker attribution & conversational turns     │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Action-Item Extraction Engine               │
│  - Grammatical modal commitment parsing                     │
│  - Direct address & imperative assignment attribution       │
│  - Deadline detection & normalization                       │
│                                                             │
│  Intelligence Providers:                                    │
│    ├── Ollama (100% Private local models)                   │
│    ├── Google Gemini API (Generous free tier)               │
│    ├── OpenAI API (gpt-4o-mini / gpt-4o)                    │
│    └── Deterministic NLP Heuristic Extractor (Offline)      │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Multi-Format Output                     │
│  ├── Executive Markdown Meeting Minutes                     │
│  ├── Machine-readable JSON Schema                           │
│  ├── CSV Task Table (Jira / Linear / Asana compatible)      │
│  └── Subtitles (.srt, .vtt)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/Vecesta-co/meeting-transcriber-action-extractor.git
cd meeting-transcriber-action-extractor
pip install -e .

# Optional: Install GPU audio transcription acceleration
pip install -e ".[audio]"
```

### 2. Extract Action Items from a Transcript

```bash
# Extract action items from a text transcript into Markdown
meeting-transcriber extract fixtures/sample_meeting.txt --format markdown

# Export directly to a JSON file
meeting-transcriber extract fixtures/sample_meeting.txt --format json --output minutes.json

# Export to CSV for Jira / Linear
meeting-transcriber extract fixtures/sample_meeting.txt --format csv --output tasks.csv
```

### 3. Transcribe Audio File

```bash
# Transcribe audio using faster-whisper and extract commitments
meeting-transcriber transcribe recording.mp3 --model base --format markdown
```

---

## ⚙️ Configuration Reference

| Environment Variable | CLI Flag | Default | Description |
|---|---|---|---|
| `AI_PROVIDER` | `-p, --provider` | `rule` | `rule`, `gemini`, `ollama`, or `openai` |
| `WHISPER_MODEL` | `-m, --model` | `base` | Model size: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `GEMINI_API_KEY` | N/A | None | Google Gemini API key |
| `OPENAI_API_KEY` | N/A | None | OpenAI API key |
| `OLLAMA_HOST` | N/A | `http://127.0.0.1:11434` | Ollama server URL |
| `OLLAMA_MODEL` | N/A | `llama3.2` | Ollama model identifier |

---

## 🧪 Testing Instructions

```bash
# Run unit and integration tests with coverage
python -m pytest --cov=src --cov-report=term-missing

# Test CLI environment status
meeting-transcriber info
```

---

## 💡 What's Special & Unique

1. **Owner-Grounded Turn-Taking**: Uses conversational dialogue cues to attribute commitments to specific individuals (e.g. recognizing "Jordan, can you..." assigns Jordan as the owner, while "I will deploy..." assigns the current speaker).
2. **100% Offline Rule Engine**: You can extract high-quality meeting minutes and action items on an air-gapped machine or airplane mode with zero API keys.
3. **Multi-Format Export**: Generates minutes for human readers (Markdown), developers (CSV/Jira), and accessibility systems (SRT/VTT).
4. **4x Speed with CTranslate2**: Dramatically outperforms standard Whisper implementations.

---

## ⚖️ Why This Is Different and More Capable

| Feature | `SYSTRAN/faster-whisper` | Commercial SaaS (Otter / Fireflies) | **`meeting-transcriber` (Vecesta.co)** |
|---|---|---|---|
| **Transcription Engine** | CTranslate2 | Proprietary cloud | **CTranslate2 (faster-whisper)** |
| **Action Items** | ❌ None (raw text only) | Proprietary cloud model | **✅ Structured Tasks, Owners, Deadlines** |
| **Privacy & Security** | Local audio | Uploaded to third-party cloud | **✅ 100% Local / Air-gap friendly** |
| **Cost** | Free (Open Source) | $18-$40 / user / month | **✅ 100% Free & Open Source (MIT)** |
| **Offline Fallback** | Transcription only | ❌ Requires active internet | **✅ Built-in Deterministic Rule Extractor** |
| **Export Formats** | Raw text | Restricted dashboard / PDF | **✅ Markdown, JSON, CSV, SRT, VTT** |
| **Turn Diarization** | ❌ None | Cloud diarizer | **✅ Conversational turn-taking attribution** |

---

## 🛠️ Difficulties Faced & Solutions (from DEVLOG.md)

- **Obstacle 1: Windows Console Unicode / Emoji cp1252 Trap**
  - *Problem*: `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4dd'` occurred when printing Markdown meeting minutes in Windows PowerShell.
  - *Solution*: Proactively reconfigured `sys.stdout` and `sys.stderr` to `utf-8` on Windows startup inside `src/cli.py`.
- **Obstacle 2: CTranslate2 & FFmpeg Binary Isolation**
  - *Problem*: Environments without FFmpeg or GPU drivers fail during audio imports.
  - *Solution*: Decoupled transcription from action item extraction. The engine operates seamlessly on text transcripts or audio files, with dynamic driver checks.

---

## 🗺️ Roadmap

- [x] v1.0.0: Core faster-whisper transcription, heuristic diarization, deterministic rule engine, Gemini/Ollama providers, multi-format exporters.
- [ ] v1.1.0: Real-time live microphone stream transcription.
- [ ] v1.2.0: Direct bidirectional sync to Notion and Linear APIs.

---

## 🤝 Contributing

Contributions are welcomed! See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - Copyright (c) 2026 **Vecesta.co**.

---

## 🏢 Credits & Contact

Built with pride by **Vecesta.co** — engineering elite open-source software factory tools.

- **Organization**: [Vecesta.co](https://github.com/Vecesta-co)
- **Email**: vecesta.co@gmail.com
- **LinkedIn**: [Vansh Dhawan](https://www.linkedin.com/in/vansh-dhawan-2625v)
- **GitHub**: [Vecesta-co](https://github.com/Vecesta-co)
- **X (Twitter)**: [@Vansh_Dhawann](https://x.com/Vansh_Dhawann)
- **Hugging Face**: [Vecesta](https://huggingface.co/Vecesta)

