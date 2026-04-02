"""
SAP tag → Protocol section mapping table.

Each SAP tag maps to a list of protocol section IDs (with prefix matching).
For example, "10" matches sections 10, 10.1, 10.2, 10.2.1, etc.

Mapping is based on general ICH/CDISC clinical protocol structure,
not specific to any single protocol.
"""

# Sections included in every SAP tag call as shared context
# Protocol Synopsis (1.1) contains study design, treatment arms, objectives, endpoints
GLOBAL_CONTEXT_SECTIONS: list[str] = ["1.1"]

# SAP tag → relevant protocol sections
# Each prompt's information needs are traced from prompts_yuhan_v1.py
SAP_TO_PROTOCOL_MAP: dict[str, list[str]] = {
    # Section 2: Introduction
    # Needs: background, study design, treatment arms, duration
    "introduction": ["3", "5.1", "5.2"],

    # Section 3: Objectives
    # Needs: primary/secondary/exploratory objectives
    "objectives": ["4"],

    # Section 4: Analysis Sets
    # Needs: population definitions, randomization, analysis set definitions
    "screened_set": ["6", "10.1"],
    "randomized_set": ["6", "7.6", "10.1"],
    "safety_set": ["6", "7.6", "10.1"],
    "fas_definition": ["6", "10.1"],
    "pps_definition": ["6", "10.1"],

    # Section 5: Subject Disposition
    # Needs: analysis sets, discontinuation criteria
    "subject_disposition": ["8", "10.1"],

    # Section 6: Demographics & Baseline
    # Needs: population, screening assessments, baseline characteristics
    "demographics": ["6", "9.1", "9.3"],

    # Section 7: Exposure & Compliance
    # Needs: dosing, administration, compliance measures
    "ip_exposure": ["7.1", "7.2", "7.3"],
    "treatment_compliance": ["7.2", "7.7"],

    # Section 8: Medical History & Medication
    # Needs: medical history collection, concomitant meds
    "medical_history": ["6", "9.1"],
    "concomitant_medication": ["7.8", "9.1"],

    # Section 9: Efficacy Analysis — needs objectives, endpoints, statistical methods
    "primary_efficacy": ["4", "5.1", "9.2", "9.5", "10"],
    "secondary_efficacy": ["4", "5.1", "9.2", "9.5", "10"],
    "additional_efficacy": ["4", "9.2", "9.5", "9.6", "10.4", "10.5"],

    # Section 10: Safety Analysis
    # Needs: AE definitions, safety assessments, statistical methods for safety
    "adverse_events": ["9.4", "10.2"],
    "lab_parameters": ["9.3.4", "10.2.5"],
    "vital_signs": ["9.3.2", "10.2.3"],
    "ecg": ["9.3.3", "10.2.2"],
    "physical_exam": ["9.3.1", "10.2.4"],
    "other_safety": ["9.3.5", "10.2", "10.5"],

    # Section 11: Interim Analysis
    "interim_analysis": ["10.7"],

    # DMC Analysis
    "dmc_analysis": ["7.3.2", "10.7"],

    # Section 12: Sample Size
    # Needs: objectives, design rationale, sample size section
    "sample_size": ["4", "5.1", "5.2", "10.8"],

    # Section 13: Statistical Software
    "statistical_software_version": ["10"],

    # Statistical Considerations
    "statistical_considerations": ["10"],

    # Section 14: Data Handling Conventions
    # Needs: visit schedule, assessments, data handling rules
    "visit_windows": ["2.1", "9"],
    "derived_variables": ["4", "9.2", "9.5"],
    "repeated_assessments": ["9.3", "10.2"],
    "missing_last_dose_date": ["7.2", "9.4"],
    "missing_ae_severity": ["9.4.10"],
    "missing_causality": ["9.4.11"],
    "missing_dates": ["9.4"],
    "lab_char_values": ["9.3.4", "10.2.5"],

    # Protocol Deviation (added in Phase 4)
    # Needs: discontinuation criteria, protocol deviation definitions
    "protocol_deviation": ["8", "10.9"],

    # Baseline Definition (added in Phase 4)
    # Needs: assessment schedule, screening/baseline procedures
    "baseline_definition": ["2.1", "9.1", "9.3"],

    # Subgroup Analysis (added in Phase 4)
    # Needs: population, objectives, statistical considerations
    "subgroup_analysis": ["6", "10"],

    # Section 15: Changes to Protocol Analysis
    "protocol_changes": ["10.9"],
}
