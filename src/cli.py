import argparse
import sys
import os

# Ensure UTF-8 stdout on Windows terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from .config import TranscriberConfig
from .core.diarizer import HeuristicDiarizer
from .core.extractor import extract_meeting_insights
from .core.exporter import MeetingExporter
from .core.transcriber import FasterWhisperTranscriber

def main():
    parser = argparse.ArgumentParser(
        prog="meeting-transcriber",
        description="High-performance meeting transcription and action-item extractor by Vecesta.co"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Command: extract
    extract_p = subparsers.add_parser("extract", help="Extract action items and summary from a meeting transcript text file")
    extract_p.add_argument("file", help="Path to transcript text file (.txt, .vtt, etc.)")
    extract_p.add_argument("-p", "--provider", choices=["rule", "gemini", "ollama", "openai"], default="rule", help="AI provider (default: rule)")
    extract_p.add_argument("-f", "--format", choices=["markdown", "json", "csv", "srt"], default="markdown", help="Output format")
    extract_p.add_argument("-o", "--output", help="Optional output file path")
    extract_p.add_argument("-t", "--title", default="Executive Meeting Minutes", help="Meeting title")

    # Command: transcribe
    transcribe_p = subparsers.add_parser("transcribe", help="Transcribe audio file and extract action items")
    transcribe_p.add_argument("file", help="Path to audio file (.mp3, .wav, .m4a, etc.)")
    transcribe_p.add_argument("-m", "--model", default="base", help="faster-whisper model size (tiny, base, small, medium, large-v3)")
    transcribe_p.add_argument("-p", "--provider", choices=["rule", "gemini", "ollama", "openai"], default="rule", help="AI provider")
    transcribe_p.add_argument("-f", "--format", choices=["markdown", "json", "csv", "srt"], default="markdown", help="Output format")
    transcribe_p.add_argument("-o", "--output", help="Optional output file path")
    transcribe_p.add_argument("-t", "--title", default="Sprint Review & Commitments", help="Meeting title")

    # Command: info
    subparsers.add_parser("info", help="Show system environment and hardware capabilities")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    config = TranscriberConfig()

    if args.command == "info":
        tw = FasterWhisperTranscriber()
        print("\n=== Meeting Transcriber Environment (Vecesta.co) ===")
        print(f"• faster-whisper available: {tw.is_available}")
        print(f"• Default AI Provider:      {config.provider_name}")
        print(f"• Gemini Key configured:    {bool(config.gemini_api_key)}")
        print(f"• OpenAI Key configured:    {bool(config.openai_api_key)}")
        print(f"• Ollama Endpoint:          {config.ollama_host}")
        print("====================================================\n")
        return

    if args.command == "extract":
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()

        segments = HeuristicDiarizer.parse_text_transcript(content)
        provider = config.get_provider(args.provider)
        summary = extract_meeting_insights(segments, provider=provider, title=args.title)

        output_str = ""
        if args.format == "markdown":
            output_str = MeetingExporter.to_markdown(summary)
        elif args.format == "json":
            output_str = MeetingExporter.to_json(summary)
        elif args.format == "csv":
            output_str = MeetingExporter.to_csv(summary)
        elif args.format == "srt":
            output_str = MeetingExporter.to_srt(summary)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            print(f"✔ Exported {args.format.upper()} to: {args.output}")
        else:
            print(output_str)

    elif args.command == "transcribe":
        if not os.path.exists(args.file):
            print(f"Error: Audio file not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        tw = FasterWhisperTranscriber(model_size=args.model)
        if tw.is_available:
            print(f"Transcribing audio with faster-whisper [{args.model}]...", file=sys.stderr)
            segments = tw.transcribe_audio(args.file)
        else:
            print("Note: faster-whisper not installed; using deterministic speech fixture for demonstration.", file=sys.stderr)
            segments = tw.mock_transcribe(args.file)

        diarizer = HeuristicDiarizer()
        diarized_segments = diarizer.diarize_segments(segments)
        provider = config.get_provider(args.provider)
        summary = extract_meeting_insights(diarized_segments, provider=provider, title=args.title)

        output_str = ""
        if args.format == "markdown":
            output_str = MeetingExporter.to_markdown(summary)
        elif args.format == "json":
            output_str = MeetingExporter.to_json(summary)
        elif args.format == "csv":
            output_str = MeetingExporter.to_csv(summary)
        elif args.format == "srt":
            output_str = MeetingExporter.to_srt(summary)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            print(f"✔ Transcribed & Exported to: {args.output}")
        else:
            print(output_str)

if __name__ == "__main__":
    main()
