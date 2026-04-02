"""
Yuhan Corporation SAP prompts — v1.

Each key in PROMPTS_DICTIONARY maps to a Jinja2 template tag in
yuhan_sap_template_v1.0.docx and to a PromptRegister entry in
generate_yuhan_template.py.

Tag names must be identical across all three files.
"""


def system_message(protocol_text: str) -> str:
    """Return the system message that provides the protocol context to the LLM."""
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
        f"The protocol is:\n\n{protocol_text}"
    )


# ---------------------------------------------------------------------------
# Prompt dictionary — keys must match PromptRegister.variable values
# ---------------------------------------------------------------------------

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

# Section 9: Efficacy Analysis
PROMPTS_EFFICACY = {
    "primary_efficacy": """
Write the Primary Efficacy Parameter(s) section for the SAP.

This is a critical section requiring detailed statistical reasoning. Include:
- State the primary efficacy parameter (e.g., change from baseline in a specific measure at a specific time point).
- Describe the primary analysis model in detail (e.g., MMRM with treatment group, visit, treatment-by-visit interaction, baseline value as covariates; or ANCOVA with specified factors).
- State the analysis set used (e.g., FAS as primary, PPS for sensitivity).
- Describe any sensitivity analyses planned for the primary endpoint.
- Describe how results will be presented (e.g., LS means, treatment differences with 95% CI, p-values).
- Mention any supportive plots or displays (e.g., plots by study visits by treatment group).

Write in full paragraphs with sufficient detail for unambiguous implementation.
Follow ICH E9(R1) estimand framework if applicable.
Do not invent statistical methods not specified in the protocol.
""",

    "secondary_efficacy": """
Write the Secondary Efficacy Parameter(s) section for the SAP.

Include:
- List each secondary efficacy parameter as defined in the protocol.
- For each secondary parameter, describe the planned analysis method.
- If secondary outcomes will be analyzed in the same way as the primary outcome, state this explicitly.
- If different methods are used, describe them with sufficient detail.
- State the analysis set and any multiplicity adjustments if specified.

Write in full paragraphs. Be concise but complete.
Do not invent information not present in the protocol.
""",

    "additional_efficacy": """
Write the Additional Efficacy Parameter(s) section for the SAP.

Include:
- List any additional or exploratory efficacy parameters described in the protocol.
- Describe the analysis approach for each.
- These are typically descriptive or exploratory analyses.

If the protocol does not specify additional efficacy parameters, state: "No additional efficacy parameters are specified in the protocol."

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
    PROMPTS_INTRODUCTION,
    PROMPTS_OBJECTIVES,
    PROMPTS_ANALYSIS_SETS,
    PROMPTS_DISPOSITION,
    PROMPTS_DEMOGRAPHICS,
    PROMPTS_EXPOSURE,
    PROMPTS_MEDICAL,
    PROMPTS_EFFICACY,
    PROMPTS_SAFETY,
    PROMPTS_INTERIM,
    PROMPTS_DMC,
    PROMPTS_SAMPLE_SIZE,
    PROMPTS_SOFTWARE,
    PROMPTS_STAT_CONSIDERATIONS,
    PROMPTS_DATA_HANDLING,
    PROMPTS_CHANGES,
]:
    PROMPTS_DICTIONARY.update(_d)
