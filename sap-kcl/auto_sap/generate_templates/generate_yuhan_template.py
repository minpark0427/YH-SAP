"""
Yuhan Corporation SAP template generator.

Mirrors generate_kcl_template.py but targets the Yuhan SAP template
and Yuhan-specific prompts.

Tag names must match exactly across:
  - PROMPTS_DICTIONARY in prompts_yuhan_v1.py
  - PromptRegister entries below
  - {{ tag }} placeholders in yuhan_sap_template_v1.0.docx
"""

from auto_sap.classes.template_class import Template
from auto_sap.classes.prompt_register_class import PromptRegister
from auto_sap.prompts import prompts_yuhan_v1 as prompts_file
from importlib.resources import files


# ---------------------------------------------------------------------------
# Prompt register — one entry per template tag
# (variable, reasoning_effort, verbosity)
#
# reasoning_effort levels:
#   "minimal" — simple extraction / standard text
#   "low"     — straightforward summarization
#   "medium"  — moderate complexity (data handling, sample size)
#   "high"    — statistical reasoning (efficacy models, estimands)
# ---------------------------------------------------------------------------
prompt_tasks = [
    # Section 1: Abbreviations
    PromptRegister("abbreviations", "low", "low"),

    # Section 2: Introduction
    PromptRegister("introduction", "medium", "low"),

    # Section 3: Objectives
    PromptRegister("objectives", "low", "low"),

    # General Considerations for Data Summarization
    PromptRegister("general_considerations", "medium", "low"),

    # Section 4: Analysis Sets
    PromptRegister("screened_set", "minimal", "low"),
    PromptRegister("randomized_set", "minimal", "low"),
    PromptRegister("safety_set", "minimal", "low"),
    PromptRegister("fas_definition", "minimal", "low"),
    PromptRegister("pps_definition", "low", "low"),

    # Section 5: Subject Disposition
    PromptRegister("subject_disposition", "low", "low"),

    # Section 6: Demographics & Baseline
    PromptRegister("demographics", "low", "low"),

    # Section 7: Exposure & Compliance
    PromptRegister("ip_exposure", "low", "low"),
    PromptRegister("treatment_compliance", "low", "low"),

    # Section 8: Medical History & Medication
    PromptRegister("medical_history", "minimal", "low"),
    PromptRegister("concomitant_medication", "low", "low"),

    # Special Screening Tests (Phase 1 specific)
    PromptRegister("special_tests", "low", "low"),

    # Section 9: Efficacy / PK / PD Analysis — HIGH reasoning
    PromptRegister("primary_efficacy", "high", "low"),
    PromptRegister("secondary_efficacy", "high", "low"),
    PromptRegister("additional_efficacy", "medium", "low"),

    # Preliminary Analyses (Phase 1 specific)
    PromptRegister("preliminary_pk", "medium", "low"),
    PromptRegister("preliminary_pd", "medium", "low"),

    # Blinded Analyses
    PromptRegister("blinded_analyses", "low", "low"),

    # Section 10: Safety Analysis
    PromptRegister("adverse_events", "medium", "low"),
    PromptRegister("lab_parameters", "low", "low"),
    PromptRegister("vital_signs", "low", "low"),
    PromptRegister("ecg", "low", "low"),
    PromptRegister("physical_exam", "minimal", "low"),
    PromptRegister("other_safety", "minimal", "low"),

    # Section 11: Interim Analysis
    PromptRegister("interim_analysis", "low", "low"),

    # DMC Analysis
    PromptRegister("dmc_analysis", "minimal", "low"),

    # Section 12: Sample Size — HIGH reasoning
    PromptRegister("sample_size", "high", "low"),

    # Section 13: Statistical Software (version extraction only)
    PromptRegister("statistical_software_version", "minimal", "low"),

    # Statistical Considerations
    PromptRegister("statistical_considerations", "medium", "low"),

    # Section 14: Data Handling Conventions
    PromptRegister("visit_windows", "medium", "low"),
    PromptRegister("derived_variables", "medium", "low"),
    PromptRegister("repeated_assessments", "low", "low"),
    PromptRegister("missing_last_dose_date", "low", "low"),
    PromptRegister("missing_ae_severity", "minimal", "low"),
    PromptRegister("missing_causality", "minimal", "low"),
    PromptRegister("missing_dates", "medium", "low"),
    PromptRegister("lab_char_values", "low", "low"),

    # Protocol Deviation (added in Phase 4 — gap analysis)
    PromptRegister("protocol_deviation", "low", "low"),

    # Baseline Definition (added in Phase 4 — gap analysis)
    PromptRegister("baseline_definition", "low", "low"),

    # Subgroup Analysis (added in Phase 4 — gap analysis)
    PromptRegister("subgroup_analysis", "low", "low"),

    # References
    PromptRegister("references", "low", "low"),

    # Section 15: Changes to Protocol Analysis
    PromptRegister("protocol_changes", "low", "low"),
]


# ---------------------------------------------------------------------------
# Template instance
# ---------------------------------------------------------------------------
yuhan_template_v1 = Template(
    template_path=files("auto_sap").joinpath("templates/yuhan_sap_template_v1.0.docx"),
    system_message_function=prompts_file.system_message,
    prompt_register=prompt_tasks,
    prompts_dictionary=prompts_file.PROMPTS_DICTIONARY,
    template_name="yuhan_sap_template_v1.0.docx",
    prompts_name="yuhan_v1, 2026-04-01",
    backend="claudecode",
)
