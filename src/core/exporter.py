import csv
import io
import json
from .types import MeetingSummary

class MeetingExporter:
    @staticmethod
    def to_markdown(summary: MeetingSummary) -> str:
        duration_min = int(summary.duration_seconds // 60)
        duration_sec = int(summary.duration_seconds % 60)
        duration_str = f"{duration_min}m {duration_sec}s"

        md = f"# 📝 {summary.title}\n\n"
        md += f"> **Duration**: {duration_str} | **Attendees**: {', '.join(summary.attendees) if summary.attendees else 'None specified'}\n\n"

        md += "## 📌 Key Discussion Points\n"
        for point in summary.summary_points:
            md += f"- {point}\n"
        md += "\n"

        md += "## ✅ Action Items & Commitments\n\n"
        if not summary.action_items:
            md += "🎉 *No pending action items were identified in this meeting session.*\n\n"
        else:
            md += "| Status | Task | Assigned Owner | Deadline | Priority | Timestamp |\n"
            md += "|:---:|:---|:---|:---|:---:|:---:|\n"
            for item in summary.action_items:
                pri_badge = "🔴 High" if item.priority == "HIGH" else ("🟡 Med" if item.priority == "MEDIUM" else "🟢 Low")
                md += f"| [ ] | **{item.task}** | `{item.owner}` | {item.deadline} | {pri_badge} | `{item.timestamp}` |\n"
            md += "\n"

            md += "### Context Details\n"
            for item in summary.action_items:
                if item.context_quote:
                    md += f"- **[{item.timestamp}] {item.owner}**: *\"{item.context_quote}\"*\n"
            md += "\n"

        md += "---\n*Meeting notes generated autonomously by [meeting-transcriber-action-extractor](https://github.com/Vecesta-co/meeting-transcriber-action-extractor) by **Vecesta.co**.*"
        return md

    @staticmethod
    def to_json(summary: MeetingSummary, indent: int = 2) -> str:
        return summary.model_dump_json(indent=indent)

    @staticmethod
    def to_csv(summary: MeetingSummary) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Task", "Owner", "Deadline", "Priority", "Timestamp", "Context Quote"])
        for item in summary.action_items:
            writer.writerow([
                item.task,
                item.owner,
                item.deadline,
                item.priority,
                item.timestamp,
                item.context_quote
            ])
        return output.getvalue()

    @staticmethod
    def to_srt(summary: MeetingSummary) -> str:
        """Generates standard SubRip Subtitle (.srt) format from segments."""
        srt_lines = []
        for i, seg in enumerate(summary.segments, 1):
            start_h = int(seg.start // 3600)
            start_m = int((seg.start % 3600) // 60)
            start_s = int(seg.start % 60)
            start_ms = int((seg.start - int(seg.start)) * 1000)

            end_h = int(seg.end // 3600)
            end_m = int((seg.end % 3600) // 60)
            end_s = int(seg.end % 60)
            end_ms = int((seg.end - int(seg.end)) * 1000)

            time_str = f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}"
            srt_lines.append(f"{i}\n{time_str}\n[{seg.speaker}] {seg.text}\n")

        return "\n".join(srt_lines)

