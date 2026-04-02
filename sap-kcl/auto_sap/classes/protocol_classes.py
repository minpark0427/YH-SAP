import os
from typing import Iterable, Optional
import PyPDF2
import docx

class Protocol:
    """Load a clinical trial protocol from a PDF or TXT file and expose plain text via .protocol_txt.

    Typical usage:
    - Provide an absolute/relative path: Protocol(file_path)
    - Or locate within the repo's Protocols/ folder: Protocol.from_protocols_dir("boppp.pdf")
    """

    def __init__(self, file_path: str):
        if not file_path:
            raise ValueError("file_path must be provided")

        self.file_path = file_path
        ext = self.check_file_extension(file_path)
        if ext == ".pdf":
            self.load_pdf()
        elif ext == ".txt":
            self.load_txt()
        elif ext == ".docx":
            self.load_docx()

    def load_pdf(self) -> None:
        """Extract text from a PDF, joining pages with double newlines."""
        chunks = []
        with open(self.file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                # PyPDF2 can return None; guard for that
                text = page.extract_text() or ""
                chunks.append(text.rstrip())
        # Separate pages with blank lines to avoid word merges
        self.protocol_txt = "\n\n".join(chunks)

    def load_docx(self) -> None:
        """Extract text from a docx file, including both paragraphs and tables."""
        document = docx.Document(self.file_path)

        # Build a mapping of table elements for inline insertion
        table_texts = {}
        for table in document.tables:
            # Convert each table to a readable text representation
            rows = []
            for row in table.rows:
                cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                rows.append(" | ".join(cells))
            table_texts[table._element] = "\n".join(rows)

        # Walk document body in order, interleaving paragraphs and tables
        parts = []
        for child in document.element.body:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "p":
                text = child.text or ""
                # Reconstruct full paragraph text from all runs
                from docx.oxml.ns import qn
                runs = child.findall(qn("w:r"))
                if runs:
                    text = "".join(
                        (r.find(qn("w:t")).text or "") if r.find(qn("w:t")) is not None else ""
                        for r in runs
                    )
                if text.strip():
                    parts.append(text)
            elif tag == "tbl":
                if child in table_texts:
                    parts.append(table_texts[child])

        self.protocol_txt = "\n".join(parts)

    def load_txt(self) -> None:
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as file:
            self.protocol_txt = file.read()

    def save_protocol_txt(self, protocol_txt_path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(protocol_txt_path)), exist_ok=True)
        with open(protocol_txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(self.protocol_txt)

    def check_file_extension(self, filename: str) -> str:
        _, ext = os.path.splitext(filename)

        if ext.lower() not in [".txt", ".pdf", ".docx"]:
            raise ValueError(f"Unsupported file extension: {ext}. Must be .txt, .pdf, or .docx")

        return ext

    # ---------- Utilities for locating protocols in the repo ----------
    @staticmethod
    def _project_root() -> str:
        """Repo root assumed to be parent of the Classes/ directory."""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @classmethod
    def protocols_dir(cls) -> str:
        return os.path.join(cls._project_root(), "Protocols")

    @classmethod
    def list_protocols(
        cls,
        extensions: Iterable[str] = (".pdf", ".txt"),
        recursive: bool = True,
    ) -> list[str]:
        """List protocol files under Protocols/ matching given extensions."""
        prot_dir = cls.protocols_dir()
        if not os.path.isdir(prot_dir):
            return []

        matches: list[str] = []
        if recursive:
            for root, _, files in os.walk(prot_dir):
                for f in files:
                    if os.path.splitext(f)[1].lower() in {e.lower() for e in extensions}:
                        matches.append(os.path.join(root, f))
        else:
            for f in os.listdir(prot_dir):
                p = os.path.join(prot_dir, f)
                if os.path.isfile(p) and os.path.splitext(f)[1].lower() in {e.lower() for e in extensions}:
                    matches.append(p)
        return sorted(matches)

    @classmethod
    def find_in_protocols(cls, filename: str) -> Optional[str]:
        """Find a file by name (case-insensitive) under Protocols/ and return its full path."""
        target = filename.lower()
        for p in cls.list_protocols():
            if os.path.basename(p).lower() == target:
                return p
        return None

    @classmethod
    def from_protocols_dir(cls, filename: str) -> "Protocol":
        """Convenience constructor to load a protocol by filename from Protocols/.

        Example: Protocol.from_protocols_dir("boppp.pdf")
        """
        full = cls.find_in_protocols(filename)
        if not full:
            prot_dir = cls.protocols_dir()
            raise FileNotFoundError(
                f"Could not find '{filename}' under {prot_dir}. "
                f"Available: {[os.path.basename(p) for p in cls.list_protocols()]}"
            )
        return cls(full)
