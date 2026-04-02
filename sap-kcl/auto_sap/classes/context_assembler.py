"""
Context assembler — builds targeted context for each SAP tag.

For each SAP tag, assembles:
  1. Global context (Protocol Synopsis) — shared across all tags
  2. Tag-specific protocol sections from the mapping table

Falls back to full protocol text if mapped sections are empty.
"""

from auto_sap.classes.protocol_segmenter import ProtocolSegmenter


class ContextAssembler:
    """Assemble targeted protocol context per SAP tag."""

    def __init__(
        self,
        segmenter: ProtocolSegmenter,
        mapping: dict[str, list[str]],
        global_sections: list[str],
        full_protocol_text: str | None = None,
    ) -> None:
        self._segmenter = segmenter
        self._mapping = mapping
        self._global_sections = global_sections
        self._full_text = full_protocol_text or segmenter.full_text
        self._cache: dict[str, str] = {}

    def assemble(self, sap_tag: str) -> str:
        """Build context for a single SAP tag.

        Returns targeted context if mapping succeeds,
        or full protocol text as fallback.
        """
        if sap_tag in self._cache:
            return self._cache[sap_tag]

        # Global context (Protocol Synopsis)
        global_ctx = self._segmenter.get_sections(self._global_sections)

        # Tag-specific sections
        section_ids = self._mapping.get(sap_tag, [])
        specific_ctx = self._segmenter.get_sections(section_ids) if section_ids else ""

        # Fallback: if no specific content found, use full protocol
        if not specific_ctx.strip():
            print(f"WARNING: No mapped sections found for '{sap_tag}', falling back to full protocol")
            result = self._full_text
        else:
            result = (
                f"=== STUDY OVERVIEW ===\n{global_ctx}\n\n"
                f"=== RELEVANT PROTOCOL SECTIONS ===\n{specific_ctx}"
            )

        self._cache[sap_tag] = result
        print(f"  {sap_tag}: {len(result)} chars")
        return result

    def assemble_all(self) -> dict[str, str]:
        """Build context for all SAP tags in the mapping."""
        print("Assembling targeted context for all SAP tags...")
        result = {}
        for tag in self._mapping:
            result[tag] = self.assemble(tag)

        total = sum(len(v) for v in result.values())
        avg = total // len(result) if result else 0
        full_len = len(self._full_text)
        print(f"Context assembly complete: {len(result)} tags, "
              f"avg {avg} chars/tag (vs {full_len} full protocol, "
              f"{100 - avg * 100 // full_len}% reduction)")
        return result
