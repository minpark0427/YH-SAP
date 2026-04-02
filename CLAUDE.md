# YH-SAP Project — Claude Code Guide

## What This Project Is

Adapting the open-source **sap-kcl** (KCL SAP auto-generation tool) to produce
Statistical Analysis Plans in **Yuhan Corporation's standard template format**.

## Project Structure

```
YH-SAP/
├── CLAUDE.md                          ← this file
├── SBS02T01 Ver02_...20251212.docx    ← Yuhan SAP template (reference)
├── Jafari 등 - 2026 - ...pdf          ← Reference paper (SAPAI pipeline)
├── SAP-AI 자동생성 프로그램 도입 계획서.md  ← Implementation plan
├── YH-SAP-venv/                       ← Python virtual environment
├── DEVELOPMENT_ROADMAP.md             ← Phased improvement plan + verification findings
├── reports/                           ← Verification reports output directory
├── scripts/
│   ├── create_yuhan_template.py       ← Script to generate tagged docx template
│   ├── verify_sap_quality.py          ← SAP quality verification (automated + LLM)
│   ├── validate_sap.py                ← LLM-based checklist validation
│   └── run_validation_5x.py           ← Multi-run consistency validation
│
└── sap-kcl/                           ← Open-source repo (upstream)
    ├── auto_sap/
    │   ├── classes/
    │   │   ├── template_class.py      ← Core: Template class (docxtpl rendering)
    │   │   ├── prompt_register_class.py ← PromptRegister dataclass
    │   │   ├── chat_classes.py        ← OpenAI chat wrappers
    │   │   └── protocol_classes.py    ← Protocol PDF reader
    │   ├── prompts/
    │   │   ├── prompts_06.py          ← KCL prompts (reference)
    │   │   └── prompts_yuhan_v1.py    ← ★ Yuhan prompts (36 tags, all filled)
    │   ├── generate_templates/
    │   │   ├── generate_kcl_template.py    ← KCL template config (reference)
    │   │   └── generate_yuhan_template.py  ← ★ Yuhan template config (36 PromptRegisters)
    │   └── templates/
    │       ├── sapai_kcl_template_v0.2_clean.docx  ← KCL template
    │       └── yuhan_sap_template_v1.0.docx        ← ★ Tagged Yuhan template (36 Jinja2 tags)
    │
    └── WriteSAPs/
        ├── yuhan_sap.py               ← ★ Yuhan runner script
        └── ...                         ← Other example runners
```

## How It Works

1. **Protocol PDF** → `Protocol` class extracts text
2. **System message** + **prompt dictionary** → LLM generates each SAP section
3. **PromptRegister** list defines which sections to generate and in what order
4. **Template class** renders the LLM output into a docx via `docxtpl` (Jinja2 tags)
5. The docx template must contain `{{ variable_name }}` tags matching the prompt keys

## What Has Been Done

- [x] Analyzed sap-kcl architecture (Template, PromptRegister, prompts, generate_templates)
- [x] Extracted all section headings from Yuhan SAP template docx
- [x] Created Python venv (`YH-SAP-venv/`) with all dependencies
- [x] Created `prompts_yuhan_v1.py` — prompts for all 36 SAP sections
- [x] Created `generate_yuhan_template.py` — 36 PromptRegister entries with reasoning_effort
- [x] Created `WriteSAPs/yuhan_sap.py` — runner script
- [x] Created `scripts/create_yuhan_template.py` — automated template tagging script
- [x] Created `yuhan_sap_template_v1.0.docx` — Jinja2-tagged template (36 tags)
- [x] Verified tag consistency across docx ↔ prompts ↔ register (all 36 match)
- [x] Smoke test passed: import and Template instantiation OK
- [x] Switched LLM backend from OpenAI to Anthropic Claude (claude-sonnet-4-5)
- [x] Added ClaudeCodeChat backend — calls `claude` CLI subprocess (no API key needed)
- [x] Added ProtocolSegmenter — heading-based protocol sectioning (126 sections)
- [x] Added SECTION_MAPPING — SAP tag → protocol section mapping (36 tags)
- [x] Added ContextAssembler — targeted context per tag (89% reduction, avg 12.5K vs 111K)
- [x] Added MultiStepGenerator — 2-step generation for high-complexity sections
- [x] Refactored template_class — per-tag targeted context, write_sap() API unchanged
- [x] E2E validated: 36/36 sections, 0 errors, 85s (test mode)
- [x] Added JSON structured output + python-docx rendering (B안) — no markdown in docx
- [x] GAP analysis: plan vs SAP template vs human-written SAP
- [x] PK/PD prompt generalization — Phase 1 studies now generate PK/PD analysis instead of "Not applicable"
- [x] Added 3 new tags: protocol_deviation, baseline_definition, subgroup_analysis (36→39 tags)
- [x] Added 7 more tags: abbreviations, general_considerations, special_tests, preliminary_pk, preliminary_pd, blinded_analyses, references (39→46 tags)
- [x] Default model updated to claude-sonnet-4-6

## What Still Needs To Be Done

### 1. ~~End-to-end validation with a real protocol~~ ✅ Done
- Validated with YH00000 protocol: 46/46 sections, 0 errors

### 2. ~~Verification process~~ ✅ Done
- Created `scripts/verify_sap_quality.py` — automated + LLM-based quality verification
- Compared AI SAP vs human-written SAP for YH00000-101
- Findings: 28 [SKIP] markers (16 false), 104 table gap, specificity gaps
- See `DEVELOPMENT_ROADMAP.md` for full analysis and improvement plan

### 3. Phase 1 — Protocol Extraction Accuracy (Current Priority)
- Reduce false [SKIP] markers (16 sections where human SAP has content but AI skips)
- Improve specificity: extract exact formulas, version numbers, BLQ handling rules
- Better PK analysis detail (power model equation, food effect ANOVA)

### 4. Phase 2 — Expert Judgment Layer (Next)
- Generate standard FAS/PPS/baseline definitions using biostatistics conventions
- Generate missing data imputation rules (SAP-standard defaults)
- Generate protocol deviation classification framework
- See `DEVELOPMENT_ROADMAP.md` Phase 2

### 5. Phase 3 — Table Shell Generation (Future)
- Generate ~70 output table templates (the #1 value-add of a human SAP)
- Table shells for demographics, AE, PK, PD, labs, listings
- See `DEVELOPMENT_ROADMAP.md` Phase 3

### 6. Optional enhancements
- Korean language support (bilingual SAP generation)
- Auto-code pipeline integration (R/SAS code generation from SAP)
- ~~LLM provider flexibility~~ ✅ Done — 3 backends
- ~~Targeted-context generation~~ ✅ Done — 89% context reduction per LLM call

## Key Conventions

- **LLM backend**: Three backends available, set via `backend=` in Template init:
  - `"claudecode"` (default) — calls the `claude` CLI as a subprocess. No API key needed; uses your Claude subscription. Classes: `ClaudeCodeChat` / `ClaudeCodeChatAsync`.
  - `"anthropic"` — uses the Anthropic Python SDK directly. Requires `ANTHROPIC_API_KEY` env var. Classes: `AnthropicChat` / `AnthropicChatAsync`.
  - `"openai"` — uses the OpenAI Python SDK. Requires `OPENAI_API_KEY` env var. Classes: `OpenAIChat` / `OpenAIChatAsync`.
- **Virtual env**: activate with `source YH-SAP-venv/bin/activate`
- **Run from sap-kcl/**: `python -m WriteSAPs.yuhan_sap <protocol.pdf> --test`
- **Prompt keys** must be identical across: `PROMPTS_DICTIONARY`, `PromptRegister.variable`, and `{{ tags }}` in the docx
- Template uses `docxtpl` (Jinja2 in docx), not `python-docx` directly
- **Regenerate template**: `python scripts/create_yuhan_template.py` (reads original docx, inserts tags, saves to templates/)
- **Verify SAP quality**: `python scripts/verify_sap_quality.py --ai-sap <content.txt> --human-sap <reference.docx> --output reports/report.md`
  - Add `--skip-llm` for fast automated-only checks
  - Add `--sections tag1 tag2` to evaluate specific sections only

## Yuhan SAP Template Tags (46 total)

| # | Section | Tag | reasoning_effort |
|---|---------|-----|-----------------|
| 1 | Abbreviations | `abbreviations` | low |
| 2 | Introduction | `introduction` | medium |
| 3 | Objectives | `objectives` | low |
| — | General Considerations | `general_considerations` | medium |
| 4.1 | Screened Set | `screened_set` | minimal |
| 4.2 | Randomized Set | `randomized_set` | minimal |
| 4.3 | Safety Set | `safety_set` | minimal |
| 4.4 | Full Analysis Set | `fas_definition` | minimal |
| 4.5 | Per-Protocol Set | `pps_definition` | low |
| 5 | Subject Disposition | `subject_disposition` | low |
| 6 | Demographics | `demographics` | low |
| 7.1 | IP Exposure | `ip_exposure` | low |
| 7.2 | Treatment Compliance | `treatment_compliance` | low |
| 8.1 | Medical History | `medical_history` | minimal |
| 8.2 | Concomitant Medication | `concomitant_medication` | low |
| — | Special Screening Tests | `special_tests` | low |
| 9.1 | Primary Analysis (Efficacy/PK) | `primary_efficacy` | **high** |
| 9.2 | Secondary Analysis (Efficacy/PD) | `secondary_efficacy` | **high** |
| 9.3 | Additional/Exploratory Analysis | `additional_efficacy` | medium |
| — | Preliminary PK Analyses | `preliminary_pk` | medium |
| — | Preliminary PD Analyses | `preliminary_pd` | medium |
| — | Blinded Analyses | `blinded_analyses` | low |
| 10.1 | Adverse Events | `adverse_events` | medium |
| 10.2 | Lab Parameters | `lab_parameters` | low |
| 10.3 | Vital Signs | `vital_signs` | low |
| 10.4 | ECG | `ecg` | low |
| 10.5 | Physical Exam | `physical_exam` | minimal |
| 10.6 | Other Safety | `other_safety` | minimal |
| 11 | Interim Analysis | `interim_analysis` | low |
| — | DMC Analysis | `dmc_analysis` | minimal |
| 12 | Sample Size | `sample_size` | **high** |
| 13 | Statistical Software | `statistical_software_version` | minimal |
| — | Statistical Considerations | `statistical_considerations` | medium |
| 14.1 | Visit Windows | `visit_windows` | medium |
| 14.2 | Derived Variables | `derived_variables` | medium |
| 14.3 | Repeated Assessments | `repeated_assessments` | low |
| 14.4 | Missing Last Dose Date | `missing_last_dose_date` | low |
| 14.5 | Missing AE Severity | `missing_ae_severity` | minimal |
| 14.6 | Missing Causality | `missing_causality` | minimal |
| 14.7 | Missing Dates | `missing_dates` | medium |
| 14.8 | Lab Character Values | `lab_char_values` | low |
| — | Protocol Deviation | `protocol_deviation` | low |
| — | Baseline Definition | `baseline_definition` | low |
| — | Subgroup Analysis | `subgroup_analysis` | low |
| — | References | `references` | low |
| 15 | Protocol Changes | `protocol_changes` | low |
