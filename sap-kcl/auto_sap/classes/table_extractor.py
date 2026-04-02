"""
Protocol Table Extractor — extracts key tables from protocol DOCX for SAP insertion.

Identifies tables by content matching (header text, size) rather than position,
so it works across different protocol documents.

Usage:
    extractor = ProtocolTableExtractor("protocol.docx")
    tables = extractor.extract_all()
    # tables["objectives_sad"] = {"headers": [...], "rows": [[...], ...], "caption": "..."}
"""

import re
from pathlib import Path
from docx import Document


# Table identification rules: (key, match_function, caption)
# match_function receives (table, row_count, col_count) and returns True if match
def _match_objectives_sad(table, rows, cols):
    """Objectives & Endpoints table for SAD (Part A)."""
    if cols != 2 or rows < 5:
        return False
    h0 = table.rows[0].cells[0].text.strip()
    return "목적" in h0 or "Objectives" in h0

def _match_objectives_mad(table, rows, cols):
    """Objectives & Endpoints table for MAD (Part B)."""
    if cols != 2 or rows < 5:
        return False
    h0 = table.rows[0].cells[0].text.strip()
    return "목적" in h0 or "Objectives" in h0

def _match_overall_design(table, rows, cols):
    """Overall study design summary table."""
    if cols != 2 or rows < 5:
        return False
    h0 = table.rows[0].cells[0].text.strip()
    return "중재 유형" in h0 or "Intervention Model" in h0

def _match_schedule_of_activities(table, rows, cols):
    """Schedule of Activities (large procedure table)."""
    if cols < 10 or rows < 15:
        return False
    h0 = table.rows[0].cells[0].text.strip()
    return "절차" in h0 or "Procedure" in h0

def _match_ip_info(table, rows, cols):
    """Investigational Product information table."""
    if cols < 2 or rows < 3:
        return False
    h0 = table.rows[0].cells[0].text.strip()
    return "임상시험용의약품" in h0 or "Investigational Product" in h0

def _match_pk_parameters(table, rows, cols):
    """PK Parameters definition table."""
    if cols != 2 or rows < 10:
        return False
    h0 = table.rows[0].cells[0].text.strip()
    return "PK" in h0 and ("매개" in h0 or "parameter" in h0.lower())

def _match_lab_assessments(table, rows, cols):
    """Clinical laboratory assessments table."""
    if cols < 2 or rows < 3:
        return False
    h0 = table.rows[0].cells[0].text.strip()
    return "임상실험실" in h0 or "Laboratory" in h0 or "Clinical Laboratory" in h0

def _match_abbreviations(table, rows, cols):
    """Abbreviations list table."""
    if cols != 2 or rows < 20:
        return False
    h0 = table.rows[0].cells[0].text.strip()
    return "Abbreviation" in h0 or "약어" in h0


# Table type registry: (key, matcher, caption_template, allow_multiple)
TABLE_TYPES = [
    ("objectives", _match_objectives_sad, "Objectives and Endpoints", True),
    ("overall_design", _match_overall_design, "Overall Study Design", False),
    ("schedule_of_activities", _match_schedule_of_activities, "Schedule of Activities", True),
    ("investigational_products", _match_ip_info, "Investigational Products", False),
    ("pk_parameters", _match_pk_parameters, "Pharmacokinetic Parameters", False),
    ("lab_assessments", _match_lab_assessments, "Clinical Laboratory Assessments", False),
    ("abbreviations", _match_abbreviations, "List of Abbreviations", False),
]


class ProtocolTableExtractor:
    """Extract key tables from a protocol DOCX file."""

    def __init__(self, protocol_path: str | Path):
        self.doc = Document(str(protocol_path))
        self._tables: dict[str, list[dict]] = {}

    def extract_all(self) -> dict[str, list[dict]]:
        """Extract all identifiable key tables from the protocol.

        Returns dict mapping table_key → list of table dicts.
        Each table dict: {"headers": [str], "rows": [[str]], "caption": str, "row_count": int, "col_count": int}
        """
        if self._tables:
            return self._tables

        results: dict[str, list[dict]] = {}

        for table in self.doc.tables:
            rows = len(table.rows)
            cols = len(table.columns)
            if rows == 0 or cols == 0:
                continue

            for key, matcher, caption_template, allow_multiple in TABLE_TYPES:
                try:
                    if matcher(table, rows, cols):
                        table_data = self._table_to_dict(table, caption_template)
                        if key not in results:
                            results[key] = []
                        if allow_multiple or len(results[key]) == 0:
                            results[key].append(table_data)
                            count = len(results[key])
                            if count > 1:
                                table_data["caption"] = f"{caption_template} ({count})"
                        break  # matched, don't check other types
                except Exception:
                    continue

        self._tables = results
        return results

    def _table_to_dict(self, table, caption: str) -> dict:
        """Convert a docx table to a structured dict."""
        rows = []
        for row in table.rows:
            cells = []
            for cell in row.cells:
                text = cell.text.strip().replace("\n", " ")
                cells.append(text)
            rows.append(cells)

        headers = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []

        return {
            "headers": headers,
            "rows": data_rows,
            "caption": caption,
            "row_count": len(rows),
            "col_count": len(headers),
        }

    def get_table(self, key: str) -> list[dict] | None:
        """Get extracted tables by key."""
        tables = self.extract_all()
        return tables.get(key)

    def get_table_as_text(self, key: str, index: int = 0) -> str:
        """Get a table as pipe-delimited text for LLM context."""
        tables = self.get_table(key)
        if not tables or index >= len(tables):
            return ""

        t = tables[index]
        lines = [" | ".join(t["headers"])]
        lines.append("-" * len(lines[0]))
        for row in t["rows"]:
            lines.append(" | ".join(row))
        return "\n".join(lines)

    def summary(self) -> str:
        """Return a summary of all extracted tables."""
        tables = self.extract_all()
        lines = [f"Extracted {sum(len(v) for v in tables.values())} tables from protocol:"]
        for key, table_list in tables.items():
            for t in table_list:
                lines.append(f"  {key}: {t['caption']} ({t['row_count']}r x {t['col_count']}c)")
        return "\n".join(lines)
