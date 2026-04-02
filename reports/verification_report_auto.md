# SAP Quality Verification Report

**AI SAP**: `sap-kcl/SAPs_verify/YH_SAP_YH00000-101_Clinical Protocol_Ver1.0_22Feb2024_content.txt`
**Human SAP**: `YH00000-101_SAP ver1.0(20240827).docx`
**Generated**: 2026-04-02 14:44

---

## 1. Executive Summary

- **[SKIP] markers**: 28 across 22/46 sections
- **Total AI word count**: 9,877
- **Tables**: AI=19, Human=123 (gap: 104)

---

## 2. [SKIP] Marker Analysis

These are sections where the AI decided protocol content was insufficient.
Items marked ⚠️ indicate the human SAP DID provide content — meaning the AI should too.

### `baseline_definition` ⚠️ **Human SAP has content**
- Protocol does not explicitly define the baseline value definition for SAP analysis. While baseline assessments are scheduled on Day -1 (the day prior to first IP dose) and at screening, the protocol does not specify whether baseline should be defined as the last pre-dose assessment on Day -1, the screening assessment, or an average of multiple baseline measurements for particular variables.

### `blinded_analyses` ⚠️ **Human SAP has content**
- Specific procedures defining the separation of the biostatistician preparing SRC reports from those conducting final unblinded analyses are not detailed in the protocol.

### `concomitant_medication` ⚠️ **Human SAP has content**
- WHO Drug Dictionary Enhanced or other coding system not specified in protocol
- Specific tabulation by ATC classification and treatment group not detailed in protocol

### `derived_variables` ⚠️ **Human SAP has content**
- This is a Phase 1 first-in-human study evaluating safety, tolerability, pharmacokinetics, and pharmacodynamics in healthy volunteers. There are no clinical efficacy endpoints or derived efficacy variables. All primary endpoints (treatment-emergent adverse events) and secondary endpoints (pharmacokinetic parameters, pharmacodynamic markers) are pre-specified measurement variables. The protocol does not define derived efficacy variables, change from baseline calculations for efficacy, or responder definitions.

### `fas_definition` ⚠️ **Human SAP has content**
- The protocol does not explicitly define a Full Analysis Set (FAS). The protocol specifies a Randomized Set (무작위 배정 집단) as all subjects randomly assigned to treatment, a Safety Analysis Population as all subjects who received at least one dose of IP, and population-specific analysis sets (PK Analysis Set, PD Analysis Set), but does not provide an FAS definition with baseline and post-baseline measurement requirements.

### `ip_exposure`
- No within-subject dose adjustments are permitted per protocol; all dose modifications occur at the cohort level via Safety Review Committee decisions during dose escalation

### `lab_char_values` ⚠️ **Human SAP has content**
- The protocol does not specify handling conventions for non-numeric clinical laboratory values (e.g., BLQ, ND, '<' or '>' qualifiers). This detail is typically documented in the Statistical Analysis Plan methodology section based on the bioanalytical and clinical laboratory SOPs.

### `medical_history` ⚠️ **Human SAP has content**
- Protocol does not specify SAP procedures for medical history coding and analysis. The protocol describes extensive inclusion/exclusion criteria based on medical conditions and confirms collection of medical history at screening, but does not provide guidance on MedDRA coding version, summary procedures, or analysis populations for SAP reporting.

### `missing_ae_severity` ⚠️ **Human SAP has content**
- The protocol does not specify an imputation rule for missing AE severity. Handling of missing severity data should be documented in the statistical analysis plan.

### `missing_causality` ⚠️ **Human SAP has content**
- Protocol does not specify an imputation rule for missing causality assessments of pre-treatment adverse events

### `missing_dates` ⚠️ **Human SAP has content**
- Protocol does not specify imputation rules for incomplete dates in adverse events or medications. This section requires either protocol-defined rules or predefined statistical analysis specifications not provided in the source document.

### `missing_last_dose_date` ⚠️ **Human SAP has content**
- The protocol does not provide specific guidance on how to handle missing dates of last IP dose or any imputation rules for this data element. The protocol requires that all dosing dates and times be recorded in eCRF/subject diary but does not address procedures for imputation in case of missing last dose date.

### `pps_definition`
- Per-Protocol Set definition not specified in protocol. Protocol defines Randomized Set, Safety Analysis Population, Dose Escalation Evaluation Set, Pharmacokinetic Analysis Set, and Pharmacodynamic Analysis Set, but does not explicitly define PPS.

### `preliminary_pd` ⚠️ **Human SAP has content**
- Protocol does not specify whether preliminary PD analyses will utilize unvalidated assay data or the validation status of bioassays at the time of preliminary review.

### `preliminary_pk` ⚠️ **Human SAP has content**
- Protocol does not specify detailed procedures, data handling requirements, or standardized presentation methods for preliminary PK analyses.

### `protocol_deviation` ⚠️ **Human SAP has content**
- The protocol does not specify explicit criteria for classification of major versus minor protocol deviations, or provide a detailed framework for how deviations will be categorized and summarized by treatment group and analysis set.
- The protocol does not specify the timing or procedure for finalizing the list of major protocol deviations prior to database lock or unblinding.
- The protocol does not explicitly specify whether subjects with major protocol deviations will be excluded from the Per-Protocol Set.

### `references`
- Common Terminology Criteria for Adverse Events (CTCAE) version not specified in protocol.
- WHO Drug Dictionary version for medication coding not specified in protocol.

### `secondary_efficacy`
- protocol does not specify which primary or secondary endpoints will be evaluated for correlation with PK; this determination will be finalized in the Statistical Analysis Plan prior to database lock.
- no formal multiplicity adjustment or hierarchical testing strategy for secondary parameters is specified in the protocol.

### `statistical_considerations`
- Study conducted at a single site; multicenter analytical approaches not applicable
- No formal multiplicity adjustments planned; this is a Phase 1 exploratory study using descriptive analyses rather than confirmatory hypothesis testing

### `statistical_software_version` ⚠️ **Human SAP has content**
- Statistical software version (SAS) not specified in protocol. Protocol references WinNonlin Version 6.4 or higher for PK parameter calculation but does not specify SAS version. Details deferred to Statistical Analysis Plan (SAP).

### `visit_windows` ⚠️ **Human SAP has content**
- Protocol does not specify SAP-specific methodology for assigning visits to analysis windows, handling multiple visits within the same window, or visit window classification rules for statistical analysis. These are SAP decisions to be documented in the final analysis plan.

### `vital_signs`
- Protocol does not specify criteria for potentially clinically significant vital sign changes

---

## 3. Section-by-Section Evaluation

| Tag | Words | Fidelity | Complete | Specific | vs Human | Summary |
|-----|-------|----------|----------|----------|----------|---------|
| `abbreviations` | 744 | — | — | — | — | not evaluated |
| `introduction` | 378 | — | — | — | — | not evaluated |
| `objectives` | 232 | — | — | — | — | not evaluated |
| `general_considerations` | 407 | — | — | — | — | not evaluated |
| `screened_set` | 27 | — | — | — | — | not evaluated |
| `randomized_set` | 19 | — | — | — | — | not evaluated |
| `safety_set` | 44 | — | — | — | — | not evaluated |
| `fas_definition` | 78 | — | — | — | — | not evaluated |
| `pps_definition` | 44 | — | — | — | — | not evaluated |
| `subject_disposition` | 448 | — | — | — | — | not evaluated |
| `demographics` | 256 | — | — | — | — | not evaluated |
| `ip_exposure` | 459 | — | — | — | — | not evaluated |
| `treatment_compliance` | 255 | — | — | — | — | not evaluated |
| `medical_history` | 60 | — | — | — | — | not evaluated |
| `concomitant_medication` | 303 | — | — | — | — | not evaluated |
| `special_tests` | 180 | — | — | — | — | not evaluated |
| `primary_efficacy` | 143 | — | — | — | — | not evaluated |
| `secondary_efficacy` | 1056 | — | — | — | — | not evaluated |
| `additional_efficacy` | 270 | — | — | — | — | not evaluated |
| `preliminary_pk` | 139 | — | — | — | — | not evaluated |
| `preliminary_pd` | 250 | — | — | — | — | not evaluated |
| `blinded_analyses` | 206 | — | — | — | — | not evaluated |
| `adverse_events` | 310 | — | — | — | — | not evaluated |
| `lab_parameters` | 241 | — | — | — | — | not evaluated |
| `vital_signs` | 189 | — | — | — | — | not evaluated |
| `ecg` | 154 | — | — | — | — | not evaluated |
| `physical_exam` | 85 | — | — | — | — | not evaluated |
| `other_safety` | 21 | — | — | — | — | not evaluated |
| `interim_analysis` | 18 | — | — | — | — | not evaluated |
| `dmc_analysis` | 55 | — | — | — | — | not evaluated |
| `sample_size` | 432 | — | — | — | — | not evaluated |
| `statistical_software_version` | 45 | — | — | — | — | not evaluated |
| `statistical_considerations` | 729 | — | — | — | — | not evaluated |
| `visit_windows` | 382 | — | — | — | — | not evaluated |
| `derived_variables` | 73 | — | — | — | — | not evaluated |
| `repeated_assessments` | 213 | — | — | — | — | not evaluated |
| `missing_last_dose_date` | 66 | — | — | — | — | not evaluated |
| `missing_ae_severity` | 86 | — | — | — | — | not evaluated |
| `missing_causality` | 97 | — | — | — | — | not evaluated |
| `missing_dates` | 44 | — | — | — | — | not evaluated |
| `lab_char_values` | 52 | — | — | — | — | not evaluated |
| `protocol_deviation` | 203 | — | — | — | — | not evaluated |
| `baseline_definition` | 74 | — | — | — | — | not evaluated |
| `subgroup_analysis` | 118 | — | — | — | — | not evaluated |
| `references` | 168 | — | — | — | — | not evaluated |
| `protocol_changes` | 24 | — | — | — | — | not evaluated |

---

## 4. Detailed Findings

### `abbreviations`

### `introduction`

### `objectives`

### `general_considerations`

### `screened_set`

### `randomized_set`

### `safety_set`

### `fas_definition`

### `pps_definition`

### `subject_disposition`

### `demographics`

### `ip_exposure`

### `treatment_compliance`

### `medical_history`

### `concomitant_medication`

### `special_tests`

### `primary_efficacy`

### `secondary_efficacy`

### `additional_efficacy`

### `preliminary_pk`

### `preliminary_pd`

### `blinded_analyses`

### `adverse_events`

### `lab_parameters`

### `vital_signs`

### `ecg`

### `physical_exam`

### `other_safety`

### `interim_analysis`

### `dmc_analysis`

### `sample_size`

### `statistical_software_version`

### `statistical_considerations`

### `visit_windows`

### `derived_variables`

### `repeated_assessments`

### `missing_last_dose_date`

### `missing_ae_severity`

### `missing_causality`

### `missing_dates`

### `lab_char_values`

### `protocol_deviation`

### `baseline_definition`

### `subgroup_analysis`

### `references`

### `protocol_changes`

---

## 5. Critical Gaps: Human SAP Content Missing from AI SAP

These are areas where the human statistician provided content that the AI SAP lacks.
These represent the highest-priority improvements.

| Priority | Gap | Human SAP Has | AI SAP Status |
|----------|-----|---------------|---------------|
| P0 | Table shells (output templates) | ~70 tables | 0 tables |
| P0 | FAS definition | Defined per convention | [SKIP] |
| P0 | Baseline definition per parameter | Explicit for each parameter type | [SKIP] |
| P1 | Protocol deviation classification | Defined criteria | Partial + [SKIP] |
| P1 | Statistical software versions | SAS, WinNonlin versions | [SKIP] |
| P1 | BLQ handling rules | Detailed (LLOQ/2, 0, etc.) | Present but less precise |
| P1 | IP compliance formula | (Actual/Planned)×100 | Generic |
| P1 | Missing data imputation rules | Detailed rules per type | Multiple [SKIP]s |
| P2 | Screening test breakout | 4 separate sections | 1 combined |
| P2 | Synopsis / Trial Schema / SoA | Full Section 3 | Not in template |
| P2 | Dose proportionality formula | Power model equation | Referenced |
| P2 | Preliminary PK deliverable format | File naming, templates | Generic |

---

## 6. Improvement Phases

### Phase 1 (Current): Protocol Extraction Accuracy
Focus: Maximize content faithfully extracted from the protocol.
- Reduce [SKIP] markers where protocol HAS the information
- Improve specificity (extract exact numbers, formulas, versions)
- Better BLQ handling, PK parameter, dose proportionality detail

### Phase 2 (Next): Expert Judgment Layer
Focus: Fill gaps where protocol is silent but convention is clear.
- Generate standard FAS/PPS definitions using biostatistics conventions
- Generate baseline definitions per parameter type
- Generate missing data imputation rules (SAP-standard defaults)
- Generate protocol deviation classification framework
- Generate statistical software standard text

### Phase 3 (Future): Table Shell Generation
Focus: Generate output table templates (the #1 value-add of a SAP).
- Table shells for demographics, disposition, AE summaries
- Table shells for PK parameter summaries
- Table shells for lab shift tables
- Table shells for individual listings
