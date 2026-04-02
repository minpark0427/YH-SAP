"""
JSON-based SAP renderer — builds docx from structured JSON output.

Instead of docxtpl (which inserts plain text into tagged positions),
this renderer uses python-docx to create properly formatted paragraphs
from JSON-structured LLM output.

Expected JSON format per section:
{
    "paragraphs": [
        {"text": "...", "style": "body"},
        {"text": "...", "style": "body"},
        {"text": "item 1", "style": "bullet"},
        {"text": "item 2", "style": "bullet"},
    ]
}

Styles:
  "body" → Normal paragraph
  "bullet" → List Paragraph / bullet
  "bold" → Bold paragraph (for sub-labels within a section)
"""

import json
import re
import copy
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn


def parse_llm_json(text: str) -> list[dict]:
    """Parse LLM output as JSON. Falls back to plain text if JSON parsing fails."""
    text = text.strip()

    # Try to extract JSON from the response
    # LLM might wrap it in ```json ... ``` or have extra text
    json_match = re.search(r'\{[\s\S]*"paragraphs"[\s\S]*\}', text)
    if json_match:
        try:
            data = json.loads(json_match.group())
            if "paragraphs" in data:
                return data["paragraphs"]
        except json.JSONDecodeError:
            pass

    # Try to parse as JSON array directly
    array_match = re.search(r'\[[\s\S]*\]', text)
    if array_match:
        try:
            data = json.loads(array_match.group())
            if isinstance(data, list) and len(data) > 0:
                return data
        except json.JSONDecodeError:
            pass

    # Fallback: convert plain text to paragraph list
    return _plain_text_to_paragraphs(text)


def _plain_text_to_paragraphs(text: str) -> list[dict]:
    """Convert plain text (possibly with markdown) to paragraph dicts."""
    # Strip markdown
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

    paragraphs = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if re.match(r'^[-•]\s+', line):
            paragraphs.append({"text": re.sub(r'^[-•]\s+', '', line), "style": "bullet"})
        elif re.match(r'^\d+\.\s+', line):
            paragraphs.append({"text": line, "style": "body"})
        else:
            paragraphs.append({"text": line, "style": "body"})

    return paragraphs


class JsonSapRenderer:
    """Render SAP sections from JSON-structured LLM output into a docx."""

    def __init__(self, template_path: str | Path):
        """Initialize with the Yuhan template docx as base."""
        self.template_path = Path(template_path)

    def render(self, sap_content: dict[str, str], output_path: str | Path) -> None:
        """Render all SAP sections into the template docx.

        Args:
            sap_content: dict of tag → LLM response (JSON string or plain text)
            output_path: where to save the rendered docx
        """
        doc = Document(str(self.template_path))

        # Find and replace each {{ tag }} paragraph with formatted content
        paragraphs_to_process = []
        for i, p in enumerate(doc.paragraphs):
            text = p.text.strip()
            if '{{' in text and '}}' in text:
                # Extract tag name
                match = re.search(r'\{\{\s*(\w+)\s*\}\}', text)
                if match:
                    tag = match.group(1)
                    if tag in sap_content:
                        paragraphs_to_process.append((i, p, tag))

        # Process in reverse to preserve indices
        for i, para, tag in reversed(paragraphs_to_process):
            content = sap_content[tag]
            if content == "ERROR" or not content.strip():
                # Leave error marker
                for run in para.runs:
                    run.text = ""
                if para.runs:
                    para.runs[0].text = "[ERROR: Content generation failed]"
                continue

            parsed = parse_llm_json(content)
            self._replace_paragraph_with_content(doc, para, parsed)

        # Handle the statistical_software_version special case
        for p in doc.paragraphs:
            if '{{' in p.text and 'statistical_software_version' in p.text:
                version = sap_content.get('statistical_software_version', '9.4 (or later)')
                # Just do simple text replacement
                for run in p.runs:
                    if '{{' in run.text:
                        run.text = run.text.replace(
                            '{{ statistical_software_version }}', version
                        ).replace(
                            '{{statistical_software_version}}', version
                        )

        # Post-process: remove blue color from cover page placeholders
        self._fix_cover_page_colors(doc)

        # Save
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        print(f"SAP saved to {output_path}")

    def _replace_paragraph_with_content(self, doc, placeholder_para, content_items: list[dict]):
        """Replace a placeholder paragraph with formatted content paragraphs."""
        # Get the parent element and position
        parent = placeholder_para._element.getparent()
        placeholder_elem = placeholder_para._element

        # Get reference style from the placeholder paragraph
        base_style = placeholder_para.style

        # Insert new paragraphs after the placeholder
        last_elem = placeholder_elem
        for item in content_items:
            text = item.get("text", "").strip()
            style = item.get("style", "body")
            if not text:
                continue

            # Create new paragraph element
            new_p = copy.deepcopy(placeholder_elem)
            # Clear all runs
            for r in new_p.findall(qn('w:r')):
                new_p.remove(r)
            # Clear any existing text
            for child in list(new_p):
                if child.tag == qn('w:r'):
                    new_p.remove(child)

            # Set style
            pPr = new_p.find(qn('w:pPr'))
            if pPr is None:
                from docx.oxml import OxmlElement
                pPr = OxmlElement('w:pPr')
                new_p.insert(0, pPr)

            # Apply style based on type
            if style == "bullet":
                # Use list paragraph style if available
                pStyle = pPr.find(qn('w:pStyle'))
                if pStyle is None:
                    from docx.oxml import OxmlElement
                    pStyle = OxmlElement('w:pStyle')
                    pPr.append(pStyle)
                pStyle.set(qn('w:val'), 'ListParagraph')
            else:
                # Use Normal style
                pStyle = pPr.find(qn('w:pStyle'))
                if pStyle is not None:
                    pPr.remove(pStyle)

            # Add text run
            from docx.oxml import OxmlElement
            new_r = OxmlElement('w:r')

            # Set font properties
            rPr = OxmlElement('w:rPr')
            if style == "bold":
                b_elem = OxmlElement('w:b')
                rPr.append(b_elem)

            # Set font to match template (typically 10pt, Times New Roman or similar)
            sz = OxmlElement('w:sz')
            sz.set(qn('w:val'), '20')  # 10pt = 20 half-points
            rPr.append(sz)

            # Ensure black color
            color = OxmlElement('w:color')
            color.set(qn('w:val'), '000000')
            rPr.append(color)

            new_r.append(rPr)

            new_t = OxmlElement('w:t')
            new_t.text = text
            new_t.set(qn('xml:space'), 'preserve')
            new_r.append(new_t)
            new_p.append(new_r)

            # Insert after the last element
            last_elem.addnext(new_p)
            last_elem = new_p

        # Remove the original placeholder paragraph
        parent.remove(placeholder_elem)

    def _fix_cover_page_colors(self, doc):
        """Remove blue color from cover page placeholder text."""
        for p in doc.paragraphs[:30]:  # Cover page is in first ~30 paragraphs
            for run in p.runs:
                if run.font.color and run.font.color.rgb:
                    if str(run.font.color.rgb) == '0000FF':
                        run.font.color.rgb = RGBColor(0, 0, 0)  # Set to black
