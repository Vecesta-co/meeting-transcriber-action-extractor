# DEVLOG.md: meeting-transcriber-action-extractor

Running development log documenting real technical obstacles, root cause investigations, design decisions, and solutions throughout the engineering lifecycle.

---

### Entry 1: Architecture Initialization & Whisper Dependency Isolation
- **Context**: Bootstrapping Project 3 (`meeting-transcriber-action-extractor`) for Vecesta.co.
- **Challenge**: `faster-whisper` relies on CTranslate2 and binary CUDA/C++ libraries that can be heavy or unavailable on lightweight CI runner environments or headless servers without FFmpeg.
- **Solution**: Designed a decoupled transcriber architecture:
  - `TranscriberPipeline` dynamically checks for `faster-whisper` and FFmpeg. If available, it loads the model on GPU or CPU. If unavailable or when given a pre-existing text transcript or audio fixture in test environments, it gracefully operates in transcript ingestion mode or uses a high-fidelity synthetic mock transcriber.
  - Implemented a complete deterministic rule-based NLP action item extractor (`nlp_rules.py`) using linguistic pattern matching (modal commitment phrases, direct address imperatives, date normalization) that works 100% offline with zero external package dependencies.
- **Status**: Architecture locked in `PLAN.md`.

---

### Entry 2: Windows Console Unicode / Emoji cp1252 Encoding Trap
- **Context**: Executing CLI `extract` command in PowerShell on Windows to print Markdown meeting minutes containing status and category emojis (📝, 🔴, 🟡).
- **Obstacle**: `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4dd' in position 2: character maps to <undefined>`.
- **Root Cause**: On Windows, Python's default stdout encoding in PowerShell often defaults to legacy `cp1252` instead of UTF-8, throwing exceptions whenever unicode emoji characters are printed.
- **Solution**: Added proactive stdout stream reconfiguration in `src/cli.py`:
  ```python
  if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
      sys.stdout.reconfigure(encoding="utf-8")
      sys.stderr.reconfigure(encoding="utf-8")
  ```
- **Status**: Fixed and verified across all command executions.

---
