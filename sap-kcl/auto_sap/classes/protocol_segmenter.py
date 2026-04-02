"""
Protocol text segmenter — splits protocol text into sections by heading.

Uses a two-pass approach:
  1. Parse TOC to extract section numbers and titles
  2. Find matching titles in body text to determine section boundaries
  3. Slice body text into sections keyed by section number

Prefix matching: get_section("10") returns 10 + 10.1 + 10.2 + ... all subsections.
"""

import re
from collections import OrderedDict


class ProtocolSegmenter:
    """Split protocol plain text into heading-keyed sections."""

    def __init__(self, protocol_txt: str) -> None:
        self._full_text = protocol_txt
        self._lines = protocol_txt.splitlines()
        self._toc_entries: list[tuple[str, str]] = []  # (section_num, title)
        self._body_start: int = 0
        self.sections: OrderedDict[str, str] = OrderedDict()

        self._parse_toc()
        self._find_body_start()
        self._segment_body()

    # ------------------------------------------------------------------
    # Step 1: Parse TOC
    # ------------------------------------------------------------------
    def _parse_toc(self) -> None:
        """Extract (section_number, title) pairs from the table of contents."""
        toc_start = None
        toc_end = None

        for i, line in enumerate(self._lines):
            stripped = line.strip()
            if toc_start is None and ("목차" in stripped or "TABLE OF CONTENTS" in stripped):
                toc_start = i
            # TOC ends at the last "그림 목차" / "LIST OF FIGURES" line before body
            if toc_start is not None and ("그림 목차" in stripped or "LIST OF FIGURES" in stripped):
                toc_end = i

        if toc_start is None:
            return

        # Scan TOC lines for numbered entries
        end = toc_end + 1 if toc_end else len(self._lines)
        for i in range(toc_start, end):
            line = self._lines[i].strip()

            # Match: "1." or "1.1." or "10.2.1." followed by tab and title
            m = re.match(r"^(\d+(?:\.\d+)*)\.\t(.+?)(?:\t\d+)?$", line)
            if m:
                sec_num = m.group(1)
                title = m.group(2).strip()
                self._toc_entries.append((sec_num, title))
                continue

            # Match Appendix entries
            m_app = re.match(r"^(Appendix\s+\d+)\s+(.+?)(?:\t\d+)?$", line)
            if m_app:
                sec_id = m_app.group(1).replace(" ", "_")
                title = m_app.group(2).strip()
                self._toc_entries.append((sec_id, title))

    # ------------------------------------------------------------------
    # Step 2: Find where the body text starts
    # ------------------------------------------------------------------
    def _find_body_start(self) -> None:
        """Find the first body section (after TOC, list of tables, list of figures)."""
        # Body starts after the last "그림 목차 [LIST OF FIGURES]" line
        # that is NOT part of the TOC (i.e., doesn't have a tab+page number)
        for i in range(len(self._lines) - 1, -1, -1):
            stripped = self._lines[i].strip()
            if ("그림 목차" in stripped or "LIST OF FIGURES" in stripped) and "\t" not in stripped:
                self._body_start = i + 1
                return
            # Also check for the variant with tab but no page number at the end of TOC area
            if stripped == "그림 목차 [LIST OF FIGURES]":
                self._body_start = i + 1
                return

        # Fallback: look for last TOC-style line (with tab+page number pattern)
        for i in range(len(self._lines) - 1, -1, -1):
            if re.match(r".*\t\d+$", self._lines[i].strip()):
                self._body_start = i + 1
                return

        self._body_start = 0

    # ------------------------------------------------------------------
    # Step 3: Segment the body
    # ------------------------------------------------------------------
    def _segment_body(self) -> None:
        """Find section boundaries in body text and slice into sections."""
        if not self._toc_entries:
            # No TOC found — store entire text as a single section
            self.sections["full"] = self._full_text
            return

        # Build title → section_num lookup (use first 25 chars of title for matching)
        title_to_sec: list[tuple[str, str, str]] = []  # (short_title, sec_num, full_title)
        for sec_num, title in self._toc_entries:
            # Use enough chars for unique matching but not so many that minor diffs break it
            short = title[:30].strip()
            title_to_sec.append((short, sec_num, title))

        # Find each section heading in body text
        section_starts: list[tuple[int, str]] = []  # (line_index, section_num)
        used_titles = set()

        for i in range(self._body_start, len(self._lines)):
            line = self._lines[i].strip()
            if not line:
                continue

            for short, sec_num, full_title in title_to_sec:
                if short in used_titles:
                    continue
                if short in line and len(line) < len(full_title) + 20:
                    # Match found — this line is a section heading
                    section_starts.append((i, sec_num))
                    used_titles.add(short)
                    break

        # Sort by line index (should already be sorted, but be safe)
        section_starts.sort(key=lambda x: x[0])

        # Slice text between consecutive section starts
        for idx, (start_line, sec_num) in enumerate(section_starts):
            if idx + 1 < len(section_starts):
                end_line = section_starts[idx + 1][0]
            else:
                end_line = len(self._lines)

            # Include the heading line, then all content until next heading
            section_text = "\n".join(self._lines[start_line:end_line])
            self.sections[sec_num] = section_text

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_section(self, section_id: str) -> str:
        """Get a section by ID with prefix matching.

        get_section("10") returns section 10 + 10.1 + 10.2 + ... all subsections.
        get_section("10.2") returns 10.2 + 10.2.1 + 10.2.2 + ...
        """
        parts = []
        prefix = section_id + "."  # "10" → "10."
        for key, text in self.sections.items():
            if key == section_id or key.startswith(prefix):
                parts.append(text)
            # Also match Appendix by prefix
            if key.startswith(section_id) and key == section_id:
                continue  # already handled above
        if not parts:
            # Exact match fallback
            if section_id in self.sections:
                return self.sections[section_id]
            return ""
        return "\n\n".join(parts)

    def get_sections(self, section_ids: list[str]) -> str:
        """Get multiple sections combined, each with prefix matching."""
        parts = []
        seen = set()
        for sid in section_ids:
            text = self.get_section(sid)
            if text and text not in seen:
                parts.append(text)
                seen.add(text)
        return "\n\n".join(parts)

    def get_global_summary(self) -> str:
        """Return Protocol Synopsis (section 1.1) as the global study overview."""
        return self.get_section("1.1")

    @property
    def full_text(self) -> str:
        """Return the original full protocol text."""
        return self._full_text
