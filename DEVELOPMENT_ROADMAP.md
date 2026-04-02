# YH-SAP Development Roadmap

## Project Evolution

### Phase 0: Foundation (Completed)
- Analyzed sap-kcl architecture
- Created Yuhan SAP template with 46 Jinja2 tags
- Implemented 3 LLM backends (claudecode, anthropic, openai)
- Added ProtocolSegmenter + ContextAssembler (89% context reduction)
- JSON structured output with python-docx rendering
- E2E validated: 46/46 sections generated

### Phase 1: Protocol Extraction Accuracy (Current)

**Goal**: Maximize the quality of content faithfully extracted from the protocol.

**Status**: First verification against human-written SAP revealed:
- 28 [SKIP] markers across 22/46 sections
- Many [SKIP] items should NOT be skipped (human SAP provides content)
- AI content is generally accurate but less specific than human work
- Table count: AI=19, Human=123 (massive gap, mostly table shells)

**Key improvements needed**:

| Priority | Item | Current | Target |
|----------|------|---------|--------|
| P0 | Reduce false [SKIP]s | 28 markers, ~10 unnecessary | <5 unnecessary SKIPs |
| P0 | PK analysis specificity | Good narrative | Exact formulas, BLQ rules |
| P1 | Screening tests breakout | 1 combined section | 4 separate sections |
| P1 | Dose proportionality | Described verbally | Include power model equation |
| P1 | Food effect analysis | Described | Include ANOVA model, 90% CI details |
| P1 | IP compliance formula | Generic text | `(Actual/Planned)×100` |

**Approach**:
- Improve prompts to extract more specific details from protocol
- Add "extract exact formulas and version numbers" instruction to system message
- Reduce [SKIP] threshold — only SKIP when protocol truly has zero information

### Phase 2: Expert Judgment Layer (Next)

**Goal**: Fill gaps where the protocol is silent but biostatistics convention is clear.

The human statistician adds significant value by providing **standard content that isn't in the protocol** — definitions, conventions, and rules that are well-established in the field. The AI currently outputs [SKIP] for these items, but a human would confidently write them.

**Specific items**:

| Section | What Human Provides | How AI Should Generate |
|---------|--------------------|-----------------------|
| FAS definition | "All randomized subjects who received ≥1 dose of IP, analyzed by initial allocation" | Standard ICH E9 FAS definition, adapted to study |
| PPS definition | Exclusion criteria for PPS | Convention-based: major protocol deviations, compliance thresholds |
| Baseline definition | Per-parameter baseline rules (PE: Day 1 pre-dose, VS: Day 1 pre-dose, ECG: mean of Day 1 pre-dose, Lab: Day -1, PD: Day 1 pre-dose) | Extract from SoA + convention |
| Protocol deviation | Classification (major/minor), categories, pre-lock review process | SAP-standard framework |
| Statistical software | "SAS 9.4 or later, WinNonlin 6.4 or higher" | Standard versions + extract from protocol |
| Missing data imputation | Detailed rules for dates, severity, causality | ICH E9 + industry conventions |
| Lab character values | Coding table (<X → X/2, >X → X, BLQ → LLOQ/2) | Standard conventions |

**Implementation approach**:
1. Create a "convention library" — JSON/Python dict of standard SAP content
2. For each section: first try protocol extraction → if insufficient, fall back to convention
3. Mark convention-sourced content distinctly (e.g., blue text or annotation) so human reviewer knows what was protocol-derived vs convention-derived
4. Two-pass generation: Pass 1 extracts protocol content, Pass 2 fills convention gaps

**This is a separate project**: Convention-based generation requires a different prompt strategy and possibly a reference database of approved SAP examples.

### Phase 3: Table Shell Generation (Future)

**Goal**: Generate output table templates — the primary deliverable for SAS/R programmers.

The human SAP contains ~70 table shells in its appendix. These are the actual tables that will appear in the Clinical Study Report, pre-formatted with:
- Column headers (treatment groups, statistics)
- Row labels (parameters, visits, SOC/PT)
- Footnotes and formatting conventions

**Categories of table shells needed**:

| Category | Count (Human SAP) | Examples |
|----------|-------------------|----------|
| Disposition/Demographics | ~5 | Analysis set summary, demographics, disposition flow |
| Safety - AE summaries | ~15 | TEAE by SOC/PT, by severity, by causality |
| Safety - Lab/VS/ECG | ~20 | Descriptive stats, shift tables, clinically significant |
| PK summaries | ~10 | Concentration stats, PK parameters, dose proportionality |
| PD summaries | ~5 | PD marker stats, AUEC/Emax summaries |
| Individual listings | ~15 | Subject-level data listings |

**Implementation approach**:
1. Define a table shell template system (python-docx based)
2. Map each SAP section to required output tables
3. Generate table shells based on protocol design (treatment groups, visits, parameters)
4. Insert into docx appendix

### Phase 4: Advanced Features (Future)

- **Korean language support**: Bilingual SAP generation
- **SAS/R code generation**: From SAP to analysis programs
- **Version tracking**: Track changes between SAP versions
- **Multi-protocol support**: Different Phase 2/3 templates
- **Quality scoring**: Automated quality metrics per run

---

## Verification Process

A reusable verification script exists at `scripts/verify_sap_quality.py`.

### Usage

```bash
# Full verification (automated + LLM evaluation)
python scripts/verify_sap_quality.py \
    --ai-sap "sap-kcl/SAPs_verify/YH_SAP_YH00000-101_Clinical Protocol_Ver1.0_22Feb2024_content.txt" \
    --human-sap "YH00000-101_SAP ver1.0(20240827).docx" \
    --output reports/verification_report.md

# Automated checks only (fast, no LLM cost)
python scripts/verify_sap_quality.py \
    --ai-sap "sap-kcl/SAPs_verify/YH_SAP_YH00000-101_Clinical Protocol_Ver1.0_22Feb2024_content.txt" \
    --human-sap "YH00000-101_SAP ver1.0(20240827).docx" \
    --skip-llm \
    --output reports/verification_report_auto.md

# Evaluate specific sections only
python scripts/verify_sap_quality.py \
    --ai-sap ... --human-sap ... \
    --sections primary_efficacy secondary_efficacy sample_size
```

### What it checks

1. **Automated** (instant):
   - [SKIP] marker count and locations
   - Word count per section (thin section detection)
   - Table count comparison (AI vs human docx)
   - Coverage analysis

2. **LLM-based** (takes ~5 min):
   - Protocol fidelity (0-5): does AI match protocol?
   - Completeness (0-5): all details captured?
   - Specificity (0-5): formulas, versions, exact values?
   - vs Human (0-5): quality comparison to human SAP

### Verification Findings Summary (YH00000-101)

| Metric | Value |
|--------|-------|
| [SKIP] markers | 28 across 22 sections |
| False SKIPs (human has content) | ~16 sections |
| AI table count | 19 |
| Human table count | 123 |
| Critical gaps | FAS def, baseline def, table shells |

---

## Architecture Notes

The current system follows a **single-pass protocol extraction** architecture:

```
Protocol PDF → ProtocolSegmenter → ContextAssembler → LLM (per tag) → JSON → python-docx → DOCX
```

Phase 2 will add a **convention layer**:

```
Protocol PDF → Extract → [Protocol Content] ──────────────────────→ Merge → DOCX
                                                                       ↑
Convention Library ─→ Fill Gaps ─→ [Convention Content] ──────────────┘
```

Phase 3 will add a **table generation layer**:

```
Protocol PDF → Extract Study Design ─→ Table Shell Generator ─→ Appendix Tables
                (arms, visits, params)
```
