"""
Yuhan Corporation SAP prompts — v1.

Each key in PROMPTS_DICTIONARY maps to a Jinja2 template tag in
yuhan_sap_template_v1.0.docx and to a PromptRegister entry in
generate_yuhan_template.py.

Tag names must be identical across all three files.
"""


def system_message(protocol_text: str) -> str:
    """Return the system message that provides the protocol context to the LLM.

    The protocol_text argument may be the full protocol or a targeted context
    assembled by ContextAssembler (containing only relevant sections).
    """
    return (
        "You are an expert biostatistician specialising in pharmaceutical clinical trials. "
        "You are given a clinical trial protocol and will be asked to write sections for "
        "a Statistical Analysis Plan (SAP) following Yuhan Corporation's standard template.\n\n"
        "Rules:\n"
        "- Only include content appropriate for the specific SAP section requested.\n"
        "- Be concise. Use paragraphs for analysis descriptions; use bullet points only where specified.\n"
        "- Do not invent information not present in the protocol.\n"
        "- Follow ICH E9(R1) estimand framework where applicable.\n"
        "- Write in English unless instructed otherwise.\n"
        "- Use terminology consistent with CDISC standards (SDTM/ADaM) where appropriate.\n\n"
        "CRITICAL FORMATTING RULES:\n"
        "- Do NOT use any markdown formatting: no #, ##, **, *, -, ```, or other markdown syntax.\n"
        "- Write in plain text only. No headings with # symbols.\n"
        "- For emphasis, simply use UPPERCASE or write naturally without markup.\n"
        "- For lists, use plain numbered lists (1. 2. 3.) or lettered lists (a. b. c.).\n"
        "- Do NOT repeat the section title — go straight to the content.\n"
        "- Write as if composing a formal Word document, not a markdown file.\n\n"
        f"The protocol is:\n\n{protocol_text}"
    )


# ---------------------------------------------------------------------------
# Prompt dictionary — keys must match PromptRegister.variable values
# ---------------------------------------------------------------------------

# Section 1: List of Abbreviations (auto-generated)
PROMPTS_ABBREVIATIONS = {
    "abbreviations": """
Generate a List of Abbreviations for this SAP based on the protocol.

Extract all abbreviations and acronyms used in the protocol and their definitions.
Common clinical trial abbreviations to include (if applicable):
AE (adverse event), AUC (area under the curve), BMI (body mass index), CI (confidence interval),
Cmax (maximum observed concentration), CRF/eCRF (case report form), CTCAE (Common Terminology Criteria for Adverse Events),
ECG (electrocardiogram), FAS (full analysis set), GCP (Good Clinical Practice),
ICH (International Council for Harmonisation), IP (investigational product),
ITT (intent-to-treat), MedDRA (Medical Dictionary for Regulatory Activities),
PD (pharmacodynamics), PK (pharmacokinetics), PPS (per-protocol set),
SAE (serious adverse event), SAP (statistical analysis plan), SD (standard deviation),
SOC (system organ class), PT (preferred term), SRC (Safety Review Committee),
TEAE (treatment-emergent adverse event), WHO (World Health Organization).

Add any study-specific abbreviations found in the protocol.
Present as a two-column list: Abbreviation followed by Definition, one per line.
Sort alphabetically by abbreviation.
Do not include abbreviations not relevant to this study.
""",
}

# Section 2: Introduction
PROMPTS_INTRODUCTION = {
    "introduction": """
Write the Introduction section for a Yuhan Corporation SAP.

Include:
- A brief background and rationale for the study.
- The study design (e.g., randomized, double-blind, active-controlled, multicenter, phase).
- A brief description of the treatment arms and comparators.
- The overall study duration and major periods (screening, treatment, follow-up).
- Reference to the study schedule of evaluations (state "The schedule of evaluations is presented in Table 2–1.").

Do not include:
- Specific study objectives (these belong in Section 3).
- Detailed statistical methods.

Write in full paragraphs. Be concise. Do not invent information not present in the protocol.
""",
}

# Section 3: Objectives
PROMPTS_OBJECTIVES = {
    "objectives": """
Write the Objectives section for the SAP.

- Extract and state the primary objective(s) exactly as specified in the protocol.
- Extract and state the secondary objective(s) exactly as specified in the protocol.
- If exploratory objectives exist, include them as well.
- Present each objective clearly, labeling them as Primary, Secondary, or Exploratory.

Write concisely. Do not add commentary or reword objectives.
Do not invent information not present in the protocol.
""",
}

# Section 4: Analysis Sets
PROMPTS_ANALYSIS_SETS = {
    "screened_set": """
Write the definition of the Screened Set for the SAP.
The Screened Set typically consists of all subjects who signed written informed consent and received a screening number.
Extract the exact definition from the protocol if available. If the protocol does not define a Screened Set, use the standard definition above.
Write as a single concise paragraph. Do not invent information.
""",

    "randomized_set": """
Write the definition of the Randomized Set for the SAP.
The Randomized Set typically consists of all subjects in the Screened Set who were randomized to a treatment group.
Extract the exact definition from the protocol. Write as a single concise paragraph.
Do not invent information not present in the protocol.
""",

    "safety_set": """
Write the definition of the Safety Set for the SAP.
The Safety Set typically consists of all randomized subjects who received at least one dose of the investigational product (IP). Subjects are analyzed according to the treatment actually received.
Extract the exact definition from the protocol. Write as a single concise paragraph.
Do not invent information not present in the protocol.
""",

    "fas_definition": """
Write the definition of the Full Analysis Set (FAS) for the SAP.
The FAS is typically based on the intent-to-treat principle and includes all randomized subjects who received at least one dose of double-blind IP and have both a baseline and at least one post-baseline measurement of the primary variable.
Extract the exact definition from the protocol. Write as a single concise paragraph.
Do not invent information not present in the protocol.
""",

    "pps_definition": """
Write the definition of the Per-Protocol Set (PPS) for the SAP.
The PPS typically consists of all subjects in the FAS who meet the main inclusion/exclusion criteria, do not have major protocol violations, and satisfy conditions such as:
- Completion of certain pre-specified minimal exposure to the treatment regimen
- Availability of measurements of the primary variable(s)
- Absence of any major protocol violations including violation of entry criteria

Extract the exact definition and list of conditions from the protocol. Write concisely.
Do not invent information not present in the protocol.
""",
}

# Section 5: Subject Disposition
PROMPTS_DISPOSITION = {
    "subject_disposition": """
Write the Subject Disposition section for the SAP.

Describe how subject disposition will be summarized:
- The number and percentage of subjects in each analysis set (Randomized, Safety, FAS, PPS) will be summarized by treatment group.
- Screen-failure subjects and associated reasons for failure to randomize will be tabulated.
- The number of subjects who complete the study and discontinue, along with reasons for discontinuation, will be summarized by treatment group.

Write in full paragraphs. Be concise. Adapt the details to match what the protocol specifies.
Do not invent information not present in the protocol.
""",
}

# Section 6: Demographics & Baseline
PROMPTS_DEMOGRAPHICS = {
    "demographics": """
Write the Demographics and Other Baseline Characteristics section for the SAP.

Describe how demographics and baseline characteristics will be summarized:
- Demographics (e.g., age, sex, race, ethnicity, weight, height, BMI) will be summarized descriptively by treatment group and overall for the FAS (or the analysis set specified in the protocol).
- Continuous variables: present N, mean, SD, median, min, max.
- Categorical variables: present frequency counts and percentages.
- Specify any disease-specific baseline characteristics that will be summarized (e.g., baseline blood pressure, disease severity, duration of disease).

Write in full paragraphs. Be concise. Extract specific variables from the protocol where listed.
Do not invent information not present in the protocol.
""",
}

# Section 7: Exposure & Compliance
PROMPTS_EXPOSURE = {
    "ip_exposure": """
Write the Investigational Product Exposure section for the SAP.

Describe how exposure to the IP will be summarized:
- Exposure for the Safety Set during the double-blind treatment period will be summarized as treatment duration, total dose, and related parameters.
- Specify descriptive statistics to be used (N, mean, SD, median, min, max).
- Include any study-specific exposure parameters (e.g., daily dose summaries, weekly and overall mean daily dose, overall modal daily dose, final daily dose) if mentioned in the protocol.

Write in full paragraphs. Be concise.
Do not invent information not present in the protocol.
""",

    "treatment_compliance": """
Write the Treatment Compliance section for the SAP.

Describe how treatment compliance will be measured and summarized:
- Define dosing compliance (e.g., the number of tablets actually taken divided by the number of tablets expected, expressed as a percentage).
- Describe how the total number of tablets taken is obtained (e.g., from CRF records of IP dispensing and return).
- Describe how descriptive statistics for IP compliance will be presented (by treatment group, by period between consecutive visits, and overall).

Write in full paragraphs. Adapt to the specific compliance measures described in the protocol.
Do not invent information not present in the protocol.
""",
}

# Section 8: Medical History & Medication
PROMPTS_MEDICAL = {
    "medical_history": """
Write the Medical History section for the SAP.

Describe how medical history will be coded and summarized:
- Medical history will be coded by system organ class and preferred term using MedDRA (specify version if stated in the protocol).
- The number and percentage of subjects with each medical history condition will be tabulated by treatment group for the Safety Set (or as protocol specifies).

Write as a single concise paragraph.
Do not invent information not present in the protocol.
""",

    "concomitant_medication": """
Write the Prior and Concomitant Medication section for the SAP.

Describe:
- The coding dictionary (e.g., WHO Drug Dictionary Enhanced) used to classify medications by ATC code and preferred name.
- The definition of prior medication (e.g., medication taken within a specified period before intake of double-blind IP).
- The definition of concomitant medication (e.g., medication taken on or after the date of first dose of double-blind IP).
- How prior and concomitant medications will be tabulated (by ATC classification, by treatment group, for the Safety Set).

Write in full paragraphs. Be concise.
Do not invent information not present in the protocol.
""",
}

# Section 9: Efficacy / PK / PD Analysis
# NOTE: These prompts are generalized for all trial phases.
# For Phase 1 studies without formal efficacy endpoints, these sections
# cover PK and PD analyses instead (the most common "primary analysis" in Phase 1).
PROMPTS_EFFICACY = {
    "primary_efficacy": """
Write the Primary Analysis Parameter(s) section for the SAP.

IMPORTANT: Adapt this section based on the study phase:
- For Phase 2/3 studies: describe the primary efficacy parameter and its statistical analysis.
- For Phase 1 studies: if there are no formal efficacy endpoints, describe the primary pharmacokinetic (PK) analysis plan instead, as PK characterization is typically the primary analytical objective after safety.

This is a critical section requiring detailed statistical reasoning. Include:
- State the primary analysis parameter (efficacy endpoint, or PK parameters for Phase 1).
- For PK analysis: list PK parameters to be estimated (e.g., Cmax, Tmax, AUClast, AUCinf, t1/2, CL/F, Vz/F), the analysis population (PK Analysis Set), and methods (e.g., non-compartmental analysis, descriptive statistics, dose proportionality assessment).
- For efficacy analysis: describe the primary analysis model in detail (e.g., MMRM, ANCOVA).
- State the analysis set used.
- Describe any sensitivity analyses planned.
- Describe how results will be presented (e.g., descriptive statistics, geometric means, dose-response plots, LS means with 95% CI).

Write in full paragraphs with sufficient detail for unambiguous implementation.
Follow ICH E9(R1) estimand framework if applicable.
Do not invent statistical methods not specified in the protocol.
""",

    "secondary_efficacy": """
Write the Secondary Analysis Parameter(s) section for the SAP.

IMPORTANT: Adapt based on study phase:
- For Phase 2/3: describe secondary efficacy parameters.
- For Phase 1: describe secondary PK analyses (e.g., food effect assessment, dose proportionality) and/or pharmacodynamic (PD) analyses (e.g., biomarker changes, PD parameters like AUEC, Emax).

Include:
- List each secondary parameter as defined in the protocol.
- For each parameter, describe the planned analysis method.
- State the analysis set and any multiplicity adjustments if specified.
- For PD analyses: describe biomarkers measured, summary statistics, and any PK/PD relationship exploration.

Write in full paragraphs. Be concise but complete.
Do not invent information not present in the protocol.
""",

    "additional_efficacy": """
Write the Additional/Exploratory Analysis Parameter(s) section for the SAP.

IMPORTANT: Adapt based on study phase:
- For Phase 2/3: describe additional or exploratory efficacy parameters.
- For Phase 1: describe exploratory analyses such as metabolite identification, CSF biomarkers, PK/PD modeling, or any other exploratory endpoints specified in the protocol.

Include:
- List any additional or exploratory parameters described in the protocol.
- Describe the analysis approach for each.
- These are typically descriptive or exploratory analyses.

If the protocol does not specify additional parameters, state: "No additional analysis parameters are specified in the protocol."

Write concisely. Do not invent information not present in the protocol.
""",
}

# General Considerations for Data Summarization
PROMPTS_GENERAL = {
    "general_considerations": """
Write the General Considerations for Data Summarization and Analysis section for the SAP.

Describe the general rules that apply across all analyses:
- Continuous variables will be summarized using N, mean, standard deviation (SD), median, minimum, and maximum (and geometric mean/CV% for PK parameters if applicable).
- Categorical variables will be summarized using frequency counts and percentages.
- Percentages will be calculated based on the number of subjects in the relevant analysis set.
- State the significance level for all statistical tests (e.g., two-sided alpha = 0.05) unless otherwise specified.
- State that no formal hypothesis testing is planned if this is an exploratory/Phase 1 study.
- Describe the treatment group labeling convention.
- Note that all analyses will be performed by treatment group and, where appropriate, by study part (e.g., Part A SAD, Part B MAD).

Write in full paragraphs. Be concise.
Do not invent information not present in the protocol.
""",
}

# Special Tests (Phase 1 specific: breathalyzer, hepatitis/HIV, syphilis, drug screen)
PROMPTS_SPECIAL_TESTS = {
    "special_tests": """
Write the Special Screening Tests section for the SAP.

This section covers protocol-required screening tests that are not standard safety or efficacy parameters. Based on the protocol, describe how the following will be summarized (include only those specified in the protocol):

1. Breathalyzer/Alcohol Screen Test: how results will be listed or summarized.
2. Hepatitis and HIV Tests: how screening results (HBsAg, anti-HBs, anti-HBc, anti-HCV, HIV antibody) will be listed.
3. Syphilis Reagin Test: how results will be listed if applicable.
4. Urine Drug Screening Test: how results will be listed or summarized.

For each applicable test:
- State that results will be presented as a listing by subject and treatment group.
- Subjects with positive results at screening are typically excluded per protocol.

If any of these tests are not specified in the protocol, omit them.
Write concisely. Do not invent tests not present in the protocol.
""",
}

# Preliminary PK Analyses (Phase 1 specific)
PROMPTS_PRELIMINARY = {
    "preliminary_pk": """
Write the Preliminary PK Analyses section for the SAP.

This section describes analyses performed during the study to support dose escalation decisions by the Safety Review Committee (SRC).

Include:
- State that preliminary PK analyses will be conducted after each cohort to support SRC dose escalation decisions.
- Describe which PK parameters will be estimated for preliminary analysis (e.g., Cmax, AUClast, Tmax, t1/2).
- State the analysis population (e.g., PK Analysis Set for subjects in the completed cohort).
- Describe how preliminary results will be presented (e.g., descriptive statistics by dose group, individual concentration-time profiles, mean concentration-time plots).
- Note that preliminary analyses may use unvalidated data and will be finalized in the final PK analysis.

If the protocol does not describe preliminary PK analyses, state: "No preliminary PK analyses are planned."
Write concisely. Do not invent information not present in the protocol.
""",

    "preliminary_pd": """
Write the Preliminary PD Analyses section for the SAP.

This section describes preliminary pharmacodynamic analyses performed during the study.

Include:
- State whether preliminary PD analyses are planned to support dose escalation or study conduct decisions.
- Describe which PD biomarkers will be assessed (e.g., GL1, gangliosides, other glycosphingolipid pathway metabolites).
- State the analysis population.
- Describe how preliminary PD results will be presented (e.g., individual PD profiles, mean change from baseline by dose group).
- Note that these are preliminary and may use unvalidated data.

If the protocol does not describe preliminary PD analyses, state: "No preliminary PD analyses are planned."
Write concisely. Do not invent information not present in the protocol.
""",
}

# Blinded Analyses (Phase 1 specific)
PROMPTS_BLINDED = {
    "blinded_analyses": """
Write the Blinded Analyses section for the SAP.

Describe any analyses that will be performed while the study remains blinded:

- State whether any blinded analyses are planned during the conduct of the study.
- If the SRC reviews unblinded data, describe who has access and what safeguards maintain overall study blinding.
- Describe any blinded safety monitoring procedures.
- If applicable, state that the biostatistician preparing SRC reports will not be involved in the final unblinded analysis.

If no blinded analyses are specified, state: "No specific blinded analysis procedures are defined beyond standard SRC review processes."
Write concisely. Do not invent information not present in the protocol.
""",
}

# Section 10: Safety Analysis
PROMPTS_SAFETY = {
    "adverse_events": """
Write the Adverse Events section for the SAP.

Include:
- The coding system for AEs (e.g., MedDRA version) as specified in the protocol.
- The definition of a treatment-emergent adverse event (TEAE): an AE that occurs during the double-blind treatment period or worsens in severity during that period.
- How TEAEs will be tabulated: by system organ class and preferred term, by treatment group, showing number and percentage of subjects.
- Specify categories for summarization: overall TEAEs, drug-related TEAEs, serious AEs (SAEs), AEs leading to discontinuation, deaths.
- State the causal relationship categories (e.g., certain, probable/likely, possible, not likely/unlikely, not related).
- Mention listings to be presented (SAEs, AEs leading to discontinuation, deaths).

Write in full paragraphs. Be concise.
Do not invent information not present in the protocol.
""",

    "lab_parameters": """
Write the Clinical Laboratory Parameters section for the SAP.

Describe how laboratory data will be summarized:
- Descriptive statistics for laboratory values and changes from baseline at each assessment time point will be presented by treatment group for the Safety Set.
- Mention the categories of laboratory parameters (hematology, chemistry, urinalysis) as relevant.
- Describe any shift tables or clinically significant abnormality summaries if specified in the protocol.

Write as a concise paragraph.
Do not invent information not present in the protocol.
""",

    "vital_signs": """
Write the Vital Signs section for the SAP.

Describe how vital signs will be summarized:
- Descriptive statistics for vital signs (e.g., systolic and diastolic blood pressure, pulse rate, weight) and changes from baseline at each assessment time point will be presented by treatment group for the Safety Set.
- Mention any criteria for potentially clinically significant vital sign changes if specified in the protocol.

Write as a concise paragraph.
Do not invent information not present in the protocol.
""",

    "ecg": """
Write the Electrocardiogram (ECG) section for the SAP.

Describe how ECG data will be summarized:
- Shift tables for clinical significance from baseline to end of study for 12-lead ECG will be presented by treatment group.
- Any descriptive statistics or additional summaries as specified in the protocol.

Write as a concise paragraph.
Do not invent information not present in the protocol.
""",

    "physical_exam": """
Write the Physical Examination section for the SAP.

Describe how physical examination findings will be summarized:
- A listing of subjects with any new abnormal physical examination findings at each visit or early termination will be presented.

Write as a single concise sentence or short paragraph.
Do not invent information not present in the protocol.
""",

    "other_safety": """
Write the Other Safety Parameter(s) section for the SAP.

If the protocol specifies any other safety parameters not covered in the previous sections (e.g., immunogenicity, ophthalmologic exams, special monitoring), describe how they will be summarized.

If no other safety parameters are specified, state: "No other safety parameters are specified for this study."

Write concisely. Do not invent information not present in the protocol.
""",
}

# Section 11: Interim Analysis
PROMPTS_INTERIM = {
    "interim_analysis": """
Write the Interim Analysis section for the SAP.

- First, clearly state whether any interim analysis is planned.
- If planned, describe the objectives, timing, statistical methods, stopping rules, and alpha-spending adjustments.
- If not planned, state: "No interim analysis is planned for this study."

Write concisely. Do not invent information not present in the protocol.
""",
}

# DMC Analysis
PROMPTS_DMC = {
    "dmc_analysis": """
Write the DMC (Data Monitoring Committee) Analysis section for the SAP.

- State whether a DMC is established for this study.
- If yes, describe what analyses will be provided to the DMC and at what intervals.
- If not planned, state: "No DMC analysis is planned for this study."

Write concisely. Do not invent information not present in the protocol.
""",
}

# Section 12: Sample Size
PROMPTS_SAMPLE_SIZE = {
    "sample_size": """
Write the Determination of Sample Size section for the SAP.

This section requires careful extraction of numerical details. Include:
- State the primary efficacy parameter on which the sample size is based.
- Describe the statistical test or model used for the calculation (e.g., two-sample t-test, ANCOVA, MMRM).
- State all assumptions: effect size, standard deviation, event rates, or other parameters used.
- State the planned significance level (one-sided or two-sided) and target power.
- Report any adjustments for multiplicity, interim analyses, or dropout rates.
- State the final planned sample size per group and total.

Write in full paragraphs. Report numbers exactly as stated in the protocol.
Do not perform new calculations or invent assumptions not present in the protocol.
If certain details are not specified, state that they are not reported.
""",
}

# Section 13: Statistical Software (mostly fixed text — only version tag)
PROMPTS_SOFTWARE = {
    "statistical_software_version": """
Extract the version of the statistical software (SAS) specified in the protocol.
Return only the version number (e.g., "9.4" or "9.4 (or later)").
If not specified in the protocol, return "9.4 (or later)".
""",
}

# Statistical Considerations
PROMPTS_STAT_CONSIDERATIONS = {
    "statistical_considerations": """
Write the Statistical Considerations section for the SAP.

This may include:
- Description of covariates used across analyses.
- Approach for multicenter studies (e.g., pooling of centers).
- Multiplicity adjustments (e.g., Bonferroni, Hochberg, gatekeeping).
- Sensitivity analysis strategy.
- Subgroup analysis plans.
- Model assumption checks.

Extract what is described in the protocol. If the protocol does not detail these, provide brief standard statements.
Write in full paragraphs. Be concise.
Do not invent information not present in the protocol.
""",
}

# Section 14: Data Handling Conventions
PROMPTS_DATA_HANDLING = {
    "visit_windows": """
Write the Visit Time Windows section for the SAP.

Describe:
- How visits are assigned for efficacy and safety analysis based on treatment day ranges.
- How study day is calculated (e.g., visit date minus date of first dose of double-blind IP, plus 1 for on-treatment visits).
- Rules for handling multiple visits within the same window (e.g., use the last visit with a nonmissing value).
- Reference a Visit Time Windows table if applicable (e.g., "Table 14.1–1 presents the visit time windows.").

Write in full paragraphs. Be concise.
Do not invent information not present in the protocol.
""",

    "derived_variables": """
Write the Derived Efficacy Variables section for the SAP.

Describe how key derived variables are calculated:
- Change from baseline calculation (e.g., endpoint value minus baseline value; if baseline is missing, change from baseline is set to missing).
- Any study-specific derived variables (e.g., duration of disease, percentage change, responder definitions).

Write concisely. Only include derivations specified in the protocol.
Do not invent information not present in the protocol.
""",

    "repeated_assessments": """
Write the Repeated or Unscheduled Assessments of Safety Parameters section for the SAP.

Describe standard rules for handling repeated/unscheduled assessments:
- For repeated assessments before start of double-blind treatment, use the final nonmissing assessment as baseline.
- For repeated assessments during treatment, specify which value is used for analysis.

Extract rules from the protocol. Write as a concise paragraph.
Do not invent information not present in the protocol.
""",

    "missing_last_dose_date": """
Write the Missing Date of the Last Dose of IP section for the SAP.

Describe the approach when the date of the last dose of double-blind IP is missing:
- All efforts should be made to determine the date.
- If unavailable, describe the imputation rule (e.g., use the date of the last visit where IP was dispensed, or another specified rule).

Write as a concise paragraph. Extract from the protocol.
Do not invent information not present in the protocol.
""",

    "missing_ae_severity": """
Write the Missing Severity Assessment for Adverse Events section for the SAP.

Describe the imputation rule for missing AE severity:
- If severity is missing for an AE that started before the first dose of double-blind IP, assign mild intensity.
- If severity is missing for an AE that started on or after the first dose of double-blind IP, assign the maximum severity.
- Adapt based on what the protocol specifies.

Write as a concise paragraph.
Do not invent information not present in the protocol.
""",

    "missing_causality": """
Write the Missing Causal Relationship section for the SAP.

Describe the imputation rule for missing causality assessment:
- If the causal relationship to the IP is missing for an AE that started on or after the first dose of double-blind IP, the AE will be considered as related to the IP.
- If missing for a pre-treatment AE, describe the rule if specified.

Write as a concise paragraph.
Do not invent information not present in the protocol.
""",

    "missing_dates": """
Write the Missing Date Information for Adverse Events and Medications section for the SAP.

This is a detailed section. Describe the imputation rules for incomplete dates:
- State that incomplete start dates and/or stop dates will be imputed.
- Describe rules for incomplete start dates:
  - Missing month and day: imputation based on the year relative to the first dose date.
  - Missing month only: treat day as missing and apply month+day rules.
  - Missing day only: imputation based on month/year relative to the first dose date.
- Describe rules for incomplete stop dates similarly.
- State the general rule: when the start date is needed, impute to the latest possible date that is on or after the first dose; when the stop date is needed, impute conservatively.

Extract the specific rules from the protocol. Write in full paragraphs with clear sub-rules.
Do not invent imputation rules not specified in the protocol.
""",

    "lab_char_values": """
Write the Character Values of Clinical Laboratory Parameters section for the SAP.

Describe how non-numeric laboratory values are handled:
- When a reported lab value cannot be used in statistical summaries because it is a character value (e.g., "<0.5", ">100", "BLQ"), describe the coding convention.
- Reference a table of examples if applicable (e.g., "Table 14.8–1 shows examples of how special character values should be coded.").

Write as a concise paragraph.
Do not invent information not present in the protocol.
""",
}

# Protocol Deviation
PROMPTS_PROTOCOL_DEVIATION = {
    "protocol_deviation": """
Write the Protocol Deviation section for the SAP.

Describe:
- How protocol deviations will be identified, classified, and documented.
- Categories of protocol deviations (e.g., major vs minor, or specific categories such as entry criteria violations, prohibited concomitant medication, dosing errors, visit window violations).
- How major protocol deviations will be summarized (by treatment group, by category, for the relevant analysis set).
- State that the list of major protocol deviations will be finalized and documented prior to database lock/unblinding.
- Note whether subjects with major protocol deviations will be excluded from the Per-Protocol Set.

Write concisely. Extract classification criteria from the protocol if available.
Do not invent information not present in the protocol.
""",
}

# Baseline Definition
PROMPTS_BASELINE = {
    "baseline_definition": """
Write the Definition of Baseline section for the SAP.

Describe:
- The general rule for defining the baseline value for each analysis variable.
- For most variables, the baseline is typically the last non-missing assessment prior to or on the date of first dose of investigational product.
- For safety parameters with repeated baseline assessments (e.g., vital signs, ECG), specify which measurement is used as baseline.
- If different baseline definitions apply to different endpoints, state each explicitly.
- Note any special cases (e.g., baseline for unscheduled assessments, baseline for subjects who did not receive IP).

Write as a concise paragraph or short section.
Do not invent information not present in the protocol.
""",
}

# Subgroup Analysis
PROMPTS_SUBGROUP = {
    "subgroup_analysis": """
Write the Subgroup Analysis section for the SAP.

Describe:
- Whether subgroup analyses are planned for this study.
- If planned, list the subgroup variables (e.g., age group, sex, race, baseline disease severity, geographic region, weight category).
- Describe the analysis approach for subgroups (e.g., same model as primary analysis with subgroup as an additional factor, forest plots, descriptive summaries by subgroup).
- State that subgroup analyses are exploratory and not powered for statistical significance unless otherwise specified.

If no subgroup analyses are planned, state: "No formal subgroup analyses are planned for this study." and briefly explain why (e.g., small sample size in Phase 1).

Write concisely. Do not invent information not present in the protocol.
""",
}

# References
PROMPTS_REFERENCES = {
    "references": """
Write the Reference List section for the SAP.

List the key references cited in or relevant to this SAP. Standard references typically include:
1. The study protocol (with protocol number and version).
2. ICH E9 "Statistical Principles for Clinical Trials" (1998).
3. ICH E9(R1) "Addendum on Estimands and Sensitivity Analysis" (2019), if applicable.
4. CTCAE version used for AE severity grading (extract version from protocol).
5. MedDRA version used for AE coding (extract version from protocol if stated).
6. WHO Drug Dictionary version used for medication coding (if stated).
7. Any statistical methodology references cited in the protocol (e.g., dose proportionality methods, PK analysis guidelines).

Extract specific version numbers from the protocol where available.
Present as a numbered list. Do not include references not relevant to this study.
""",
}

# Section 15: Changes to Protocol Analysis
PROMPTS_CHANGES = {
    "protocol_changes": """
Write the Changes to Analysis Specified in Protocol section for the SAP.

State the major changes to the analysis specified in the original protocol. Typical categories include:
- Addition or deletion of any primary or secondary efficacy parameters.
- Changes in the statistical methodology for efficacy parameters.
- Changes in the statistical models (e.g., inclusion of covariates).
- Changes in the definition of efficacy parameters.
- Changes in the multiple comparison procedure.
- Inclusion of an interim analysis not originally planned.

If no changes have been made, state: "No changes to the analyses specified in the protocol have been made."

Extract from the protocol. Write concisely.
Do not invent information not present in the protocol.
""",
}


# ---------------------------------------------------------------------------
# Combined dictionary — this is what Template() consumes
# ---------------------------------------------------------------------------
PROMPTS_DICTIONARY: dict[str, str] = {}
for _d in [
    PROMPTS_ABBREVIATIONS,
    PROMPTS_INTRODUCTION,
    PROMPTS_OBJECTIVES,
    PROMPTS_GENERAL,
    PROMPTS_ANALYSIS_SETS,
    PROMPTS_DISPOSITION,
    PROMPTS_DEMOGRAPHICS,
    PROMPTS_SPECIAL_TESTS,
    PROMPTS_EXPOSURE,
    PROMPTS_MEDICAL,
    PROMPTS_EFFICACY,
    PROMPTS_PRELIMINARY,
    PROMPTS_BLINDED,
    PROMPTS_SAFETY,
    PROMPTS_INTERIM,
    PROMPTS_DMC,
    PROMPTS_SAMPLE_SIZE,
    PROMPTS_SOFTWARE,
    PROMPTS_STAT_CONSIDERATIONS,
    PROMPTS_DATA_HANDLING,
    PROMPTS_PROTOCOL_DEVIATION,
    PROMPTS_BASELINE,
    PROMPTS_SUBGROUP,
    PROMPTS_REFERENCES,
    PROMPTS_CHANGES,
]:
    PROMPTS_DICTIONARY.update(_d)
