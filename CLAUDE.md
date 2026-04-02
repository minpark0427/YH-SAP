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
├── scripts/
│   └── create_yuhan_template.py       ← Script to generate tagged docx template
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

## What Still Needs To Be Done

### 1. End-to-end validation with a real protocol
- Run with a test protocol PDF to verify the full pipeline works
- Check that all template tags are populated correctly
- Review generated SAP against Yuhan template for completeness and formatting

### 2. Prompt tuning
- Evaluate generated SAP quality against existing completed SAPs
- Tune prompts for sections with low accuracy (especially 9.1 Primary Efficacy)
- Consider adding few-shot examples to statistical reasoning prompts

### 3. Optional enhancements
- Korean language support (bilingual SAP generation)
- Table generation (Table shells are common in Yuhan SAPs)
- Auto-code pipeline integration (R/SAS code generation from SAP)
- ~~LLM provider flexibility~~ ✅ Done — 3 backends: `claudecode` (default, no API key), `anthropic`, `openai`

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

## Yuhan SAP Template Tags (36 total)

| # | Section | Tag | reasoning_effort |
|---|---------|-----|-----------------|
| 2 | Introduction | `introduction` | medium |
| 3 | Objectives | `objectives` | low |
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
| 9.1 | Primary Efficacy | `primary_efficacy` | **high** |
| 9.2 | Secondary Efficacy | `secondary_efficacy` | **high** |
| 9.3 | Additional Efficacy | `additional_efficacy` | medium |
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
| 15 | Protocol Changes | `protocol_changes` | low |
