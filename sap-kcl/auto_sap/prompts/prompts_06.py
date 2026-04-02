def system_message(part_protocol):
    system_message = f"""you are an expert statistician in the field of clinical trials.
    you are givena a clinical trial protocol with a full detail of the study design, including the primary 
    and secondary endpoints, sample size, and methods of statistical analysis and will be asked to write sections for a statistical analysis plan based on a clinical trial protocol.

    Only include in your response content that would be included in the specific section of a statistical analysis plan.
    
    Be concice. Write analysis section in paragrpahs, only use bullet points where specified in the prompt.
    
    The protocol for the trial is:
     
     {part_protocol}
    """

    return(system_message)



"""
Each function returns a single prompt string for extracting content from a clinical trial protocol to populate the SAP template tags.
"""



# NOTE: Keep outputs concise, paragraph-first; use bullets only when the field is inherently a list.

# 1. Put all your prompt texts in a single dict.

PROMPTS_TITLE_ADMIN = {

    
        "title": """
        - Extract the full trial title from the protocol. 
        - Give the title only, do not include the trial acronym, even if included in the protocol title.
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        - Example protocl text for title: Finding unecessary never events (FUN), a randomised trial.
        - Correct response: Finding unecessary never events, a randomised trial.
        """,

        "trial_acronym": """
        - Extract the trial acronym from the protocol and return it exactly as it is given in the trial protcol. 
        - Do not include the word trial after the acronym
        - Good: ACTISSIST
        - Bad: ACTISSIST Trial
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "isrctn_number": """
        - Extract the ISRCTN (or equivalent single registry identifier if specified) from the protocol and return it exactly as it is given in the trial protcol. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "protocol_version_date": """
        - Extract the protocol version and date from the protocol. 
        - If multiple versions exist, select the current/most recent (usually the biggest number with most recent date). 
        - Only include the version number and date
        - Do not include the word version
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        - Example protocol text: Version 3.0, 31st June 2022
        - Correct response: 3.0, 31st June 2022
        """,
        
        "protocol_date": """
        - Extract the protocol version date from the protocol and return it exactly as it is given in the trial protcol.
        - If multiple versions exist, select the current/most recent (usually the most recent date). 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
}

def get_people_prompt(who, one_person = False):
        single_person = "If more than one relevant person given in the protocol, use one line per person."
        if one_person:
              single_person = "- Only give a single person. If more than one person is given, make a judgement as to who seems most relevant."
        
        prompt = f""" 
        - Using the clinical trial protocol, list the {who} to be named in the SAP, presenting each as “Name, Affiliation”. 
        - Do not include addresses or emails. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        - If there are no {who} listed in the protocol, return "No {who} specified in the protocol.""
        {single_person}

        - Example: Dr. Ben Carter, Kings College London Clinical Trials Unit, Institute of Psychiatry, Psychology and Neuroscience, King's College London 

        """
        return(prompt)

PROMPTS_PEOPLE = {
           "investigators": get_people_prompt("investigators") + "\n - Do not include the chief investigator \n - Do not include the trial statistician.",
           "name_of_cheif_investigator": get_people_prompt("Chief/Principal Investigator", one_person=True),
           "senior_statistician": get_people_prompt("senior statisticin", one_person=True),
           "trial_statisticians": get_people_prompt("statisticians"),
           "trial_manager": get_people_prompt("trial manager"),
           "health_economist": get_people_prompt("health economist"),


}



PROMPTS_INTRO_AND_DESIGN = {        
        "description_of_trial": """
        - Write a brief introduction that outlines the background and rationale for the study.
        - do not give details of the trial design
        - Breiefly mention the trial intervention and control arms.
        - include a brief description of the research question
        - Do not give specific objectives of the trial.
        - Write this section using full paragraphs Do not use bullet points.
        - Do not write about the statistical analysis.
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,

        
        "primary_objectives": """
        - From the protocol, write the trial’s primary objective(s) exactly as specified. 
        - Present each primary objective as a separate sentence on its own line; do not add commentary.
        - Do not add additional line breaks between objectives
        - Do not add additional punctiation or bullet points
        - Be concise. 
        - Only include what belongs to this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "secondary_objectives": """
        - From the protocol, write the trial’s secondary objective(s) exactly as specified. 
        - Present each secondary objective as a separate sentence on its own line; do not add commentary. 
        - Do not add additional line breaks between objectives
        - Be concise. 
        - Only include what belongs to this field. 
        - Do not invent information not present in the protocol.
        """,


        "trial_design": """
        - Using the clinical trial protocol, write a concise description of the overall trial design 
        - Provide a  description of the study design (e.g., parallel, crossover, factorial, cluster-randomised, adaptive, etc.)
        - Describe the number of arms and provide a brief description of each arm.
        - Specify the hypothesis testing framework (e.g., superiority, non-inferiority, equivalence); where applicable, specify which comparisons will be based on which framework.
        - Include a description of blinding, specifying which members of the research team are blinded. Timing of when statisticians and other members of team will be unblinded should also be included. 
        - Do not include randomisation mechanics here.
        - Do not include details on the objectives of the study.
        - Write in paragrpahs using full sentences
        - Be concise.
        - Do not include any content outside of this field, provide only the content detailed above
        - Use only information about the trial from the protocol, do not invent information not present in the protocol.
        """,

        "randomisation_method": """
        - Using the clinical trial protocol, write a desciption of the randomisation method.
        - Include the allocation ratio and arms randomised to, the level of randomisation (eg. individual, cluster), and method of randomisation (simple randomisation, stratifified permuted blocks, minimisation)
        - Where stratified permuted blocks are used give the stratification factors and block sizes used. If given in the protocol, provide levels of catagorical stratification factors (eg. sex (male, female), ethnicity (white british, non-white britich, other))
        - where minmisation is used, give the minimisation factors and random component
        - Write a single, concice, paragrpah.
        - Do not give any justfication for the method used.
        - Do not invent information not present in the protocol.
        - Example 1: Participants will be randomised useing a 1:1 ratio to treatment and control. Randomisation is at the individual level. Randomisation will be conducted using stratified permuted blocks with block sizes 4, 6, and 8. Stratification factors are sex (male, female), and site.  
        - Example 2: Hospitals will be randomised useing a 3:1:1 ratio to hizomabab, paracetamol, or placebo. Randomisation is at the hospital level (cluster randomised). Randomisation will be conducted uminmisation with a random component, with the probability of being allocated to the arm which minimises imbalance of 0.9. Minimisation factors are sex (male, female), and site. 
        """,

          "randomisation_implementation": """
        - Using the clinical trial protocol, write a desciption of how treatment is allocated based on the output of the randomisation system.
        - Write a single, concice, paragrpah.
        - Mention who the information will be passed to and how this will result in allocation of treatment. 
        - Example: The randomisation system records the results of randomisation and automaticly notifies the pharmacy, who dispense the required medicaiton to the particiapnt.
        """,
        
        
        "duration_of_treatment": """
        - Using the clinical trial protocol, state the duration of treatment for each arm as applicable if the two arms are different, otherwise metion it is the same in both arms. 
        - Use sentences and include timing units exactly as specified. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "follow_up_timepoints": """
        - Using the clinical trial protocol, list all follow-up time points at which outcomes are measured. 
        - Present each timepoint on a new line, in chronological order.
        - Do not use bullet points or dashes to introduce new lines. 
        - Do not add additional line breaks between timepoints
        - Be concise. 
        - Do not invent information not present in the protocol.
        - Do not include details on visit windows.
        """,
        
        "visit_windows": """
        - Using the clinical trial protocol, describe the visit windows for assessments timepoints exactly as specified. 
        - Use sentences/lines or a compact list if the protocol lists discrete windows.
        - If a list is used, present each itim in the list on a new line.
        - Do not use bullet points or dashes to introduce new lines.  
       - Do not add additional line breaks between visit windows
        - If no visit windows are given state "visit windows not defined in protocol".
        - Be concise. 
        - Only provide detils of visit windows around follow up timepoints - for example do not include details about the ammount of time between consent and randomisation.
        - Do not invent information not present in the protocol.
        """,
        
        "data_collection_procedures": """
        - Using the clinical trial protocol, summarise the data collection procedures relevant to the SAP (sources, systems, and timing) in one short paragraph. 
        - Be concise and factual. 
        - Do not include details about how randomisation is carried out.
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "inclusion_criteria": """
        - From the protocol, list the inclusion criteria
        - Give each criteria on a separate line - do not add any bullet points or other punctuation to indicate new lines.
        - Remove any enumeration given to the criteria
        - Where sub criteria exist add leading spaces to the lines.
        - Do not add commentary or reorder 
        - Be concise. 
        - Do not invent information not present in the protocol.
        """,
        
        "exclusion_criteria": """
        - From the protocol, list the exclusion criteria
        - Give each criteria on a separate line - do not add any bullet points or other punctuation to indicate new lines.
        - Where sub criteria exist add leading spaces to the lines.
        - Remove any enumeration given to the criteria
        - Do not add commentary or reorder 
        - Be concise. 
        - Do not invent information not present in the protocol.
        """,
}
PROMPTS_OUTCOMES_AND_ANALYSIS = {
       
        "primary_outcome_measures": """
        - Using the clinical trial protocol, identify all primary outcome(s) and provide a complete definition for each.
        - For each primary outcome, write a single paragraph that includes:
          • Specification of outcome (what is being measured)
          • The measurement instrument or method (e.g., questionnaire name, lab test, clinical assessment)
          • Timing of assessment (timepoint or window). Do not mention assessments at baseline.
          • Specific measurement units if applicable. If not units relevant do not mention units.
          • For outcomes measured at multiple timepoints, clearly state which timepoint is the PRIMARY timepoint for the main analysis and state that other timepoints will be analysed as secondary outcomes.
          • Any transformations or calculations used to derive the outcome. If no transformations or calculations are used do not mention this.
        - Write each outcome as a separate paragraph, even if outcomes are listed together in the protocol.
        - For time to event outcomes, clearly state the starting point (e.g., randomisation), the event definition, and censoring approach if specified.
        - For composite outcomes, list all components and specify how they combine (e.g., "time to first occurrence of death, myocardial infarction, or stroke").
        - Do not report health economic or cost utility outcomes.
        - Be concise and use terminology from the protocol.
        - Do not invent information not present in the protocol.
        - Do not include any information about the analysis of the outcome.
        - Do not mention assessments at baseline in the outcome section.
        
        Example:          
        Severity of persecutory delusions as measured by the Psychotic Symptoms Rating Scale - Delusions (PSYRATS-Delusions) total score at 6 months post-randomisation (primary timepoint), with assessments at, 3 months, and 9 months analysed as secondary outcomes.
        """,
        
        "secondary_outcome_measures": """
        - Using the clinical trial protocol, identify all secondary outcome(s) and provide a complete definition for each.
        - For each secondary outcome, write a single paragraph that includes:
          • Specification of outcome (what is being measured)
          • The measurement instrument or method (e.g., questionnaire name, lab test, clinical assessment)
          • Timing of assessment (timepoint or window)
          • Specific measurement units if applicable. If not units relevant do not mention units.
          • Any transformations or calculations used to derive the outcome. If no transformations or calculations are used do not mention transformations.
        - Write each outcome as a separate paragraph, even if outcomes are listed together in the protocol.
        - For time to event outcomes, clearly state the starting point (e.g., randomisation), the event definition, and censoring approach if specified.
        - For composite outcomes, list all components and specify how they combine (e.g., "time to first occurrence of death, myocardial infarction, or stroke").
        - Do not report health economic or cost utility outcomes.
        - Be concise and use terminology from the protocol.
        - Do not invent information not present in the protocol.
        - Do not include any information about the analysis of the outcome.
        - Do not mention units or transformations if not relevant to the particular outcome. Do not write "no utis or transformations" or similar.
        - Do not mention assessments at baseline in the outcome section.


        Example:
        Severity of persecutory delusions as measured by the Psychotic Symptoms Rating Scale - Delusions (PSYRATS-Delusions) total score at 3 and 6, and 9 months post-randomisation, .
        """,

    
        
        "mediator_of_treatment": """
        - Using only the clinical trial protocol, identify variables that are explicitly specified as mediators of treatment effects or described as lying on the causal pathway between treatment and the primary or key secondary outcomes.
        - Include only variables that are pre-specified in the protocol; do not introduce post hoc mediators.
        - For each such variable, write one paragraph that states: the variable name, how it is assessed (instrument, scale, or units), and planned measurement timepoints, if stated.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent variables, timepoints, or measurement details that are not present in the protocol.
        - Do not describe or propose any mediation analysis; only list and describe the mediator variables.
        - If no mediators are specified, output: "No mediators of treatment effects are explicitly specified in the protocol."
        """,
        
        "moderator_of_treatment": """
        - Using only the clinical trial protocol, identify variables that are explicitly specified as moderators of treatment effects, effect modifiers, or subgroup defining variables for assessing differential treatment effects.
        - Include only variables that are pre-specified in the protocol; do not introduce post hoc moderators.
        - For each such variable, write one paragraph that states: the variable name, whether it is baseline or time varying, how it is assessed (instrument, scale, units, or categories), and any relevant categories or cut points if stated.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent variables, categories, or measurement details that are not present in the protocol.
        - Do not describe or propose any moderation, interaction, or subgroup analysis; only list and describe the moderator variables.
        - If no moderators are specified, output: "No moderators of treatment effects are explicitly specified in the protocol."
        """,
        
        "process_indicators": """
        - Using only the clinical trial protocol, identify variables specified as process indicators to be summarised (e.g., fidelity, exposure, adherence, engagement, reach, implementation quality).
        - Include only process indicators that are pre-specified in the protocol; do not introduce post hoc indicators.
        - For each such variable, write one paragraph that states: the indicator name, what aspect of the process it reflects (e.g., fidelity, exposure), how it is assessed (instrument, measure, units, or categories), and planned measurement timepoints, if stated.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent indicators, categories, or measurement details that are not present in the protocol.
        - Do not describe or propose any statistical analysis of process indicators; only list and describe the indicators to be summarised.
        - If no process indicators are specified, output: "No process indicators are explicitly specified in the protocol."
        """,


        
        "adverse_events": """
        - If adverse events of special interest (AESIs) are defined in the protocol, state the wording from the protocol where possible.
        - State the coding system or dictionary for adverse events (e.g., MedDRA and version) if specified in the protocol.
        - State the severity or grading system (e.g., CTCAE version 5.0, mild/moderate/severe) if specified in the protocol.
        - Describe the reporting period for adverse events (e.g., from first dose until 30 days after last dose, during treatment period and follow up) if specified in the protocol.
        - Summarise which adverse event summaries and tabulations are planned according to the protocol (e.g., overall incidence, by treatment arm, by system organ class and preferred term, by severity, by relationship to treatment, serious vs non-serious events, AESIs, and relevant time windows such as on treatment or follow up), without adding new analyses.
        - Be concise and write in continuous prose (one to two short paragraphs), not bullet points.
        - Do not repeat definitions of adverse events, serious adverse events, etc. We are only interested in repeating protocol text if adverse events of special interest are defined.
        - Do not comment on safety reporting procedures to TSC/DMC or regulatory bodies, etc.
        - Do not infer or invent definitions, coding systems, grading systems, time windows, or analyses that are not present in the protocol.
        - If the protocol does not specify adverse event definitions, coding system, or planned summaries, write a single short paragraph stating that the protocol does not provide detailed specifications for adverse event reporting.
        """,

        "table_outcomes": """
        - Using only the information available from the clinical trial protocol and any previously extracted measure descriptions, construct a text list of all outcome-related measures defined in the protocol (e.g., primary, secondary, additional follow-up, process indicators, and any other pre-specified outcome measures).
        - Output the list as plain text using bullet points, with one top-level bullet per distinct measure and indented sub-bullets for its details.
        - For each measure, use the following structure in this exact order:
          - Top-level bullet: a brief identifier for the measure (e.g., its title or a short label).
          - Indented sub-bullets:
            - Outcome type (Primary/Secondary etc.): state the type as defined in the protocol (e.g., Primary, Secondary, Exploratory, Process, Follow-up).
            - Title: use the exact name or short label of the measure/scale from the protocol.
            - Timescale: state when the measure is collected or analysed (e.g., Baseline, 6 months, 12 months, all follow-up visits), using protocol wording where possible.
            - Items: briefly describe the number/nature of items (e.g., "10-item questionnaire", "Single item", "Subscale of XYZ scale") if specified.
            - Scoring description: provide a short description of how the measure is scored (e.g., total score range, subscale scores, higher vs lower values) as described in the protocol or instrument guidance.
            - How to handle missing items: summarise any specified rules for missing items within the scale/subscale (e.g., prorating rules, required proportion of completed items); if no rules are given, write "Not specified in protocol".
            - Interpretation (direction): state how to interpret the score direction if stated (e.g., "Higher scores = better outcome", "Higher scores = worse symptoms"); if not given, write "Not specified in protocol".
        - If some details cannot be completed from the protocol, use your best ability to complete these fields.".
        """,

       "sample_size": """
        - write a Sample Size and Power section suitable for inclusion in the Statistical Analysis Plan (SAP) using information from the protocol.
        - Describe in detail the methods used for sample size calculation.
        - Clearly state all assumptions used in the calculation, including effect size, standard deviation, event rates, control-group rates, variability parameters, correlations (e.g., for clustering or repeated measures), and any other explicitly reported inputs.
        - Specify the statistical test(s) or model(s) on which the sample size estimation is based (e.g., two-sample t-test, chi-square test, log-rank test, Cox model, mixed model), using the terminology from the protocol.
        - Report the planned power and significance level(s), stating whether the alpha level is one-sided or two-sided, as described in the protocol.
        - Describe any adjustments to the sample size for multiplicity, interim analyses, clustering (e.g., design effect, ICC, average cluster size), stratification, or unequal allocation, if these are specified.
        - Report any inflation or adjustment for anticipated dropouts, losses to follow-up, missing data, non-adherence, or other forms of attrition, including the target sample size after such adjustments.
        - Do not provide any justifications, critiques, or explanations for the methods or assumptions used; simply report the methods and parameters as described in the extracted information.
        - Write full paragraphs (not bullet points), be concise, and focus only on the Sample Size and Power section as outlined above.
        - Do not include any mathematical formulae or perform any new calculations beyond what is stated in the protocol.
        - If not stated in the protocol, assume two-sided significance level. State that this is assumed.
        - Do not describe analysis methods.
        - Do not invent methods or parameter values that are not present in the extracted information; if key details (e.g., certain assumptions or adjustments) are not specified, state briefly that these are not reported in the protocol.
        """,

        "timing_of_analysis": """
        - Clearly state when the final analysis will be conducted (e.g., after completion of follow-up for all participants and database lock, or at specific calendar dates or follow-up durations), using the terminology and conditions described in the protocol.
        - If interim, safety, or other scheduled analyses are described in the protocol and are relevant to the timing of the final analysis, briefly summarise their timing and relationship to the final analysis as described in the protocol.
        - Write in clear prose as one or more short paragraphs; do not use bullet points in the output unless the protocol itself presents timing information as a list that must be preserved.
        - Do not describe statistical methods, endpoints, or analysis sets in detail.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent any analysis timings, measurement occasions, or visit windows that are not explicitly reported in the protocol.
        - If key details about the timing of the final analysis are not specified in the protocol, state briefly that these details are not reported.
        """,
        
        "adherence_to_treatment": """
        - Using only the clinical trial protocol, write a concise description of how adherence to the allocated treatment/intervention will be assessed and summarised for inclusion in the Statistical Analysis Plan (SAP).
        - Clearly define adherence as specified in the protocol (e.g., threshold for being considered adherent, extent of exposure, allowed deviations), and describe how adherence is measured (e.g., pill counts, infusion records, self-report, electronic monitoring, clinic attendance).
        - State when adherence is assessed (e.g., at each visit, at specific follow-up timepoints, over the full treatment period), including any relevant assessment windows if these are reported.
        - Describe how adherence will be presented in the SAP (e.g., descriptively by treatment arm and timepoint, numbers and percentages adherent, summaries of continuous adherence measures such as percentage of doses taken), using the terminology from the protocol where possible.
        - Write the output as a single short paragraph (no bullet points in the output itself), be concise, and do not provide any justification or discussion beyond stating what is planned.
        - Do not infer or invent adherence definitions, thresholds, assessment methods, timepoints, or summaries that are not explicitly reported in the protocol; if details of adherence assessment or presentation are not specified, state briefly that these are not reported.
        """,

        "descriptive_of_intervention": """
        - Using only the clinical trial protocol, write a concise paragraph describing the planned descriptive summaries of the intervention(s) (and, if applicable, control arms) and the people who deliver them for inclusion in the Statistical Analysis Plan (SAP).
        - Describe what aspects of the intervention(s) will be summarised (e.g., dose, number and duration of sessions, components delivered, mode of delivery, setting), and indicate how these will be summarised (e.g., means and standard deviations, medians and interquartile ranges, counts and percentages) and by which groups or arms, as specified in the protocol.
        - If applicable, describe what characteristics of the people delivering the intervention(s) (e.g., therapists, clinicians, facilitators) will be summarised (e.g., role, professional background, training, experience, number of patients treated) and how these summaries will be presented, according to the protocol.
        - Write the output as a single concise paragraph (no bullet points in the output itself), using the terminology from the protocol where possible.
        - Do not describe or propose any statistical tests; focus only on descriptive summaries of the intervention(s) and those delivering them.
        - Do not infer or invent intervention characteristics, provider characteristics, or descriptive summaries that are not explicitly reported in the protocol; if certain details are not specified, state briefly that these are not reported.
        """,


        "descriptive_concomitant_medications": """
        - If the protocol states that data on concomitant medications will be collected, write a brief paragraph to summarise how this information will be summarised. Do not describe or propose any statistical tests, only focus on descriptive summaries.
        - Do not infer or invent concomitant medication variables, coding systems, time periods, or summary methods that are not explicitly reported in the protocol; if certain details are not specified, state briefly that these are not reported.
        - If the protocol does not say that data on concomitant medications will be collected, return this statement: 'The protocol does not mention collection of concomitant medication data.'
        - Write the output as a single concise paragraph (no bullet points in the output itself), using the terminology from the protocol where possible.
        """,

        "visit_window_deviation": """
        - Using only the clinical trial protocol, write a single short descriptive clause (not a full sentence) that can directly follow the words 'classified as protocol deviation as' in the SAP text.
        - The clause should describe how visit-window deviations will be handled or classified for reporting (e.g., within or outside pre-specified visit windows, minor vs major deviations, inclusion/exclusion from specific analyses), using the terminology from the protocol where possible.
        - Do not start the clause with a capital letter and do not end it with a full stop, so that it reads grammatically within the sentence: 'All visit window deviations will be classified as protocol deviation as {{visit_window_deviation}}.'
        - Be concise and keep the clause brief (no more than one short line of text).
        - Do not infer or invent any visit-window rules, classifications, or handling strategies that are not explicitly reported in the protocol.
        - If the protocol does not specify how visit-window deviations are handled or classified, return the clause: 'per the visit-window deviation rules specified in the protocol, which are not detailed here'
        """,

        "primary_estimand": """
        - If the trial is a pilot trial, just return the following statement: The primary goal is to assess the feasibility of delivering a full-scale trial. Such a future trial may be defined using the following estimand framework.
        - Using only the clinical trial protocol, briefly state the primary question of interest. For example: "What is the mean difference in MADRS scores at 12 months between patients with treatment-resistant depression allocated to psilocybin versus placebo?"
        """,

        "estimand_population": """
        - For the Population, describe the target population for the primary estimand as defined in the protocol (e.g., all randomised participants, all participants who received at least one dose, specific subgroups), using the protocol terminology. If not defined, simply mention target disease area. For example: "Patients with severe chronic eczema (as defined by trial inclusion/exclusion criteria)"
        - Do not describe methods, models, focus only on a simple statement.
        - Do not infer or invent any missing details.
        - Do not include anything for secondary outcomes.
        """,

        "estimand_endpoint": """
        - For the Endpoint, state the outcome(s) and timepoint(s) relevant to the primary estimand, including any composite or derived measures, exactly as specified in the protocol.
        - Do not describe methods, models, focus only on a simple statement.
        - Do not infer or invent any missing details.
        """,

        "estimand_tcond": """
        - For the Treatment condition, describe the treatment regimens or arms being contrasted (including dose, duration, and any relevant co-interventions) as they are defined for the primary estimand in the protocol.
        - Do not describe methods, models, focus only on a simple statement.
        - Do not infer or invent any missing details.
        - Do not include anything for secondary outcomes.
        """,

        "estimand_popsum": """
        - For the Population-level summary, state the contrast or summary measure for the primary estimand (e.g., difference in means, ratio of means, risk difference, risk ratio, odds ratio, hazard ratio, difference in restricted mean survival time), and the time horizon or follow-up if specified.
        - Do not describe methods, models, focus only on a simple statement.
        - Do not infer or invent any missing details.
        - Do not include anything for secondary outcomes.
        """,

        "estimand_intercurrent": """
        - For Intercurrent events, list the intercurrent events considered relevant to the primary estimand (e.g., treatment discontinuation, rescue medication, death, switch to alternative therapy) and, where stated, describe the handling strategy for each (e.g., treatment-policy, hypothetical, composite, while-on-treatment, principal stratum), using the protocol wording where possible and not inventing strategy labels.  
        - Do not describe methods, models, focus only on a simple statement.
        - Do not infer or invent any missing details.
        - Do not include anything for secondary outcomes.
        """,

        "effect_size": """
        - Using only the clinical trial protocol, describe any additional effect sizes (beyond those implied by the primary estimand) that are planned to be reported in the Statistical Analysis Plan (SAP).
        - For each additional effect size, state what measure will be reported (e.g., risk difference, risk ratio, odds ratio, mean difference, standardised mean difference, hazard ratio, number needed to treat), the outcome(s) and timepoint(s) to which it applies, and the comparison (e.g., experimental vs control).
        - Briefly describe how each effect size will be obtained in words (e.g., derived from a specified model, based on proportions at a given timepoint, based on mean change from baseline), without giving mathematical formulae or performing any new calculations.
        - Write the output as one concise paragraph; if there are several distinct effect sizes, they may be listed in sentences within the same paragraph.
        - Do not provide any justification or interpretation of the effect sizes; only state what will be reported and how they will be calculated according to the protocol.
        - Do not infer or invent any effect sizes, outcomes, timepoints, or calculation methods that are not explicitly reported in the protocol; if no additional effect sizes are specified, write a single sentence: "No additional effect sizes beyond those used for the primary analysis are explicitly specified in the protocol."
        """,
        
        "primary_analysis_model": """
        - Using only the extracted information from the clinical trial protocol, write a main analysis section for the primary outcome (excluding health economic and cost-utility outcomes), suitable for inclusion in the Statistical Analysis Plan (SAP).
        - Begin by stating the analysis population for the primary outcome exactly as defined in the protocol (e.g., intention-to-treat (ITT), modified ITT, per-protocol, safety); do not describe or justify the population, just name it.
        - For the primary outcome(s), clearly describe the planned analysis model(s), including the outcome type, the regression or modelling approach (e.g., linear regression, logistic regression, Cox proportional hazards model, mixed-effects model, repeated-measures model), and how the treatment effect will be parameterised and presented (e.g., mean difference, odds ratio, risk atio, hazard ratio, with corresponding confidence intervals).
        - Describe how time will enter the analysis models where relevant (e.g., as discrete visit factors, continuous time, follow-up duration in survival models, repeated-measures over visits), using the terminology from the protocol.
        - Specify any planned adjustment for baseline covariates, including stratification factors used in randomisation (if applicable) and baseline values of the outcome where stated; use the terminology and factor definitions from the protocol.
        - If an ITT or modified ITT approach is not taken in the first instance, state briefly what these populations are (i.e. per-protocol) and state that analyses on these populations are described later with other sensitivity analyses.
        - Do not provide analysis methods for outcomes relating to health economics or cost-utility; if such outcomes are mentioned in the protocol, state briefly that their analysis is described elsewhere.
        - Write the output as one or more concise paragraphs, without bullet points, with enough detail that the analysis could be implemented unambiguously (e.g., clearly identifying the outcome, treatment variable, covariates, and general model structure), but ithout mathematical formulae.
        - Do not introduce new analysis models, covariates, transformations, or populations beyond those explicitly described in the protocol; if important details (e.g., covariate adjustments or specific model forms) are not specified, state briefly that these are ot clearly specified in the protocol.
        - Be concise and focus only on the analysis models and covariate adjustments for the primary outcome as described above.
        """,

        
        "intercurrent_events_and_analysis": """
        - Using only the clinical trial protocol, describe the anticipated intercurrent events and any planned supplementary analyses using different strategies or estimands, for inclusion in the Statistical Analysis Plan (SAP).
        - List all anticipated intercurrent events that are explicitly mentioned in the protocol (e.g., treatment discontinuation, treatment switch, use of rescue medication, protocol-prohibited medication, withdrawal from follow-up, death), using the protocol’s terminology.
        - Where reported, state perceived or estimated rates of occurrence of each intercurrent event and, if described, any expected differences in rates between treatment arms and the reasons for these expectations.
        - If the protocol provides explanations of why particular events are considered intercurrent events, briefly summarise these explanations in short sentences.
        - Describe any supplementary analyses planned to address these intercurrent events (e.g., analyses using alternative strategies such as treatment-policy, hypothetical, composite, while-on-treatment, or principal stratum) and/or any analyses corresponding to different estimands, as outlined in the protocol, without introducing new strategies or estimands.
        - Write the output as concise prose; where the protocol lists intercurrent events or analyses as items, it is acceptable to present them as bullet points or short sentences mirroring that structure.
        - Do not describe or propose new intercurrent events, rates, handling strategies, or supplementary analyses that are not explicitly reported in the protocol; if no anticipated intercurrent events or related supplementary analyses are specified, write a single sentence stating that these are not explicitly specified in the protocol.
        """,

        "secondary_analysis": """
        - Using only the clinical trial protocol, describe the planned analysis approach for secondary outcomes, for inclusion in the Statistical Analysis Plan (SAP), ensuring consistency with the defined secondary estimands.
        - If the primary and secondary outcomes will be analysed in similar ways, just state that secondary outcomes will be analysed in the same way as the primary outcome.
        - If the secondary outcome will not be analysed in the same ways as the primary outcome, do the following:
        - Summarise the analysis models to be used for each group of secondary outcomes, specifying the outcome type, the model or method (e.g., linear regression, logistic regression, Cox proportional hazards model, mixed-effects model, repeated-measures model), and how treatment effects will be presented (e.g., mean differences, odds ratios, risk ratios, hazard ratios, with confidence intervals), as described in the protocol.
        - Identify groups of secondary outcomes that share the same model structure and covariate adjustments, and explicitly state which outcomes are analysed with each shared approach.
        - State any planned covariate adjustments for secondary outcomes, including stratification factors and baseline values of the outcome or other prognostic variables, using the terminology and factor definitions from the protocol.
        - If different analysis populations are specified for some secondary outcomes (e.g., safety or per-protocol analyses), briefly state these where relevant, without redefining them.
        - Write the output as one or more concise paragraphs (no bullet points in the output itself), providing sufficient detail for the analyses to be implemented unambiguously, but without mathematical formulae or new methods.
        - Do not introduce new models, covariates, transformations, or analysis populations beyond those explicitly described in the protocol; if the protocol does not clearly specify the analysis approach for certain secondary outcomes, state briefly that the analysis method for those outcomes is not clearly specified.
        """,

        
        "missing_items_in_scales": """
        -  Write a concise paragraph describing how missing items within multi-item scales and subscales will be handled for inclusion in the Statistical Analysis Plan (SAP).
        - State whether the proportion of participants with complete data on each scale/subscale will be reported (e.g., number and percentage with complete responses), if this is specified in the protocol.
        - Explicitly distinguish between handling missing items (partial completion of a questionnaire) and missing forms (where the entire questionnaire or visit is missing). Ensure this paragraph focuses only on the former (item-level missingness).
        - If the protocol provides scale-specific missing data guidance or scoring rules (e.g., from instrument manuals), briefly summarise these rules (such as allowable numbers/proportions of missing items and how scores are to be calculated) and refer to them in general terms rather than reproducing full scoring instructions.
        - If prorating or similar approaches are specified (e.g., replacing missing items based on averages of completed items when a certain percentage or number of items is missing), describe these rules clearly in words, including any thresholds for applying prorating, as stated in the protocol.
        - If a threshold for prorating is mentioned (e.g., 'if < 80% of items are missing'), explicitly state what happens when that threshold is exceeded (e.g., 'the total score will be set to missing').
        - Make clear whether different scales/subscales use different missing-item rules, and, if so, summarise these differences briefly.
        - If the protocol specifies rounding rules for calculated scores (e.g., rounding imputed averages to the nearest integer), include this detail.
        - Check for specific instructions regarding "Not Applicable" responses (e.g., if they are treated as missing or zero) and include if present.
        - Write the output as a single concise paragraph (no bullet points in the output itself), using the terminology from the protocol where possible.
        - Do not infer or invent prorating rules, thresholds, or other missing-item handling procedures that are not explicitly described in the protocol; if the protocol does not specify how missing items within scales are handled, state briefly that the handling of missing items in scales/subscales is not clearly specified.
        """,

        "missing_data_sensitivity_analysis": """
        - Write a concise paragraph outlining any planned sensitivity analyses for missing outcome data for inclusion in the Statistical Analysis Plan (SAP).
        - Describe which outcomes and timepoints the sensitivity analyses apply to and indicate which primary analysis they are intended to assess the robustness of (e.g., mixed-model analyses under a MAR assumption).
        - Summarise the general approach to each planned sensitivity analysis (e.g., alternative modelling assumptions, multiple imputation under different imputation models, pattern-mixture or selection models, delta-based or tipping-point analyses) and the underlying assumptions about the missing data mechanism (e.g., MAR vs MNAR), using the terminology from the protocol and without mathematical formulae.
        - If sensitivity analyses are planned specifically to examine scenarios where data may be missing not at random (MNAR), briefly describe the nature of these analyses and how they differ from the primary analysis, in general terms.
        - You should NOT provide a default for Sensitivity Analysis (like "Last Observation Carried Forward" or "Tipping Point") if the protocol is silent.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Missing outcome data” section of the SAP.
        - Do not infer or invent additional sensitivity analyses, missing data mechanisms, or modelling strategies that are not explicitly described in the protocol; if no sensitivity analyses for missing outcome data are specified, write a single sentence stating that no such sensitivity analyses are explicitly specified in the protocol.
        """,

        "multiple_comparisons": """
        - Write a concise paragraph describing the planned approach to handling multiple comparisons/multiplicity for inclusion in the Statistical Analysis Plan (SAP).
        - State whether any formal adjustment for multiplicity will be applied, and if so, describe the method (e.g., Bonferroni, Holm, Hochberg, gatekeeping procedures, family-wise error control, false discovery rate) and the scope of outcomes or comparisons to which it applies (e.g., co-primary outcomes, key secondary outcomes, multiple treatment arm comparisons).
        - If no adjustment for multiple comparisons is planned, state this explicitly and, where described in the protocol, briefly summarise how results from multiple outcomes or comparisons are intended to be interpreted (e.g., separate interpretation of each secondary outcome, emphasis on estimation and confidence intervals rather than strict hypothesis testing).
        - If different multiplicity strategies are specified for different sets of outcomes (e.g., co-primary vs secondary outcomes, primary vs exploratory comparisons), summarise these distinctions clearly.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Method for handling multiple comparisons/multiplicity” section of the SAP.
        - Do not infer or invent multiplicity adjustment methods, outcome groupings, or interpretative strategies that are not explicitly reported in the protocol; if the approach to multiplicity is not specified, write a single sentence stating that no explicit strategy for handling multiple comparisons is described in the protocol.
        """,

        "analysis_for_noncompliance": """
        - Write a concise paragraph describing any planned analyses to address non-compliance with the allocated treatment for inclusion in the Statistical Analysis Plan (SAP).
        - State whether a per-protocol, as-treated, complier-average causal effect (CACE), or other non-compliance–focused analysis is planned, and briefly describe the general approach in words (e.g., analysis restricted to participants meeting predefined adherence criteria, instrumental variable methods using randomisation as an instrument), as specified in the protocol.
        - Make clear which outcomes these non-compliance analyses will apply to (e.g., primary outcome only, primary and key secondary outcomes) and how their role is positioned relative to the primary intention-to-treat analysis (e.g., supplementary or sensitivity analyses).
        - If non-compliance thresholds or definitions (e.g., minimum dose, number of sessions, or proportion of medication taken) are specified, summarise these briefly using the protocol terminology.
        - If the protocol mentions non-compliance analyses but does not define thresholds, populations, or methods clearly, state this explicitly rather than attempting to complete missing details.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Method for handling non-compliance (per protocol/CACE analyses)” section of the SAP.
        - Do not infer or invent additional non-compliance analyses, definitions, thresholds, or modelling strategies that are not explicitly described in the protocol; if no specific analyses for non-compliance are planned, write a single sentence stating that no additional analyses addressing non-compliance are explicitly specified in the protocol.
        """,


        "model_assumption_checks": """
        - Write a concise paragraph describing the planned checks of model assumptions and any pre-specified remedies if assumptions are not met, for inclusion in the Statistical Analysis Plan (SAP).
        - Summarise which assumptions will be checked for the main analysis models (e.g., normality of residuals, homoscedasticity, linearity, proportional hazards, independence, appropriate link function) and how these will be assessed (e.g., residual plots, Q–Q plots, tests of proportional hazards), using the terminology from the protocol.
        - Where specified, describe planned actions if assumptions appear to be violated (e.g., data transformation, use of robust standard errors, alternative link functions or distributions, non-parametric methods, alternative time-to-event models), without introducing new methods.
        - If the protocol states that certain diagnostics will be performed when describing the data (e.g., checking normality of residuals, inspection for outliers), briefly include these as part of the assumption-checking description.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Model assumption checks” section of the SAP.
        - Do not infer or invent additional assumptions, diagnostics, or remedial methods that are not explicitly reported in the protocol; if the protocol does not clearly specify model assumption checks or remedies, state briefly that these are not clearly specified.
        """,


        "other_sensitivity_analysis": """
        - Using only the clinical trial protocol, write a concise paragraph describing any planned sensitivity analyses beyond those specifically addressing missing data, for inclusion in the Statistical Analysis Plan (SAP).
        - For each planned sensitivity analysis, briefly state what is being varied or examined (e.g., alternative analysis populations, different covariate adjustment sets, alternative outcome definitions, alternative model specifications, different handling of protocol deviations or non-compliance) and why it is being done (e.g., to assess robustness of primary results to particular assumptions or design choices), using the protocol’s wording where possible.
        - Summarise the general analytical approach for each sensitivity analysis in words (e.g., repeating the primary analysis in the per-protocol population, re-estimating the model excluding specific subgroups, using an alternative link function or distribution), without giving mathematical formulae or introducing new methods.
        - Do not repeat sensitivity analyses that are solely concerned with missing outcome data if these are described elsewhere; focus on other types of sensitivity analyses.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Sensitivity analyses” section of the SAP.
        - Do not infer or invent additional sensitivity analyses, rationales, or methods that are not explicitly reported in the protocol; if no additional sensitivity analyses beyond those for missing data are specified, write a single sentence stating that no further sensitivity analyses are explicitly specified in the protocol.
        """,


        "subgroup_analysis": """
        - Using only the clinical trial protocol, write a concise description of any planned subgroup analyses for inclusion in the Statistical Analysis Plan (SAP).
        - Identify all pre-specified subgroups (e.g., by age, sex, baseline severity, centre, biomarker status) and state clearly which outcomes they apply to, using the terminology from the protocol.
        - Describe how subgroup analyses will be implemented in brief, typically as interaction terms between treatment and subgroup variables within the main analysis model(s), or as separate models by subgroup if this is what the protocol specifies.
        - If the protocol comments on the purpose or interpretation of subgroup analyses (e.g., exploratory vs confirmatory), or on whether these are adjusted for multiplicity, summarise this briefly without adding new rationale.
        - Write the output as one short paragraph (no bullet points in the output itself), providing enough detail that the planned subgroup analyses could be implemented unambiguously.
        - If the protocol explicitly states that no subgroup analyses are planned, or if no subgroup analyses are described, return exactly the sentence: "No subgroup analysis will be conducted."
        - Do not infer or invent subgroup factors, outcomes, models, or interaction structures that are not explicitly reported in the protocol.
        """,

        
        "any_exploratory_mediator_and_moderator_analysis": """
        - Using only the clinical trial protocol, write a concise description of any planned exploratory mediation or moderation analyses for inclusion in the Statistical Analysis Plan (SAP).
        - For each exploratory mediation analysis, briefly state the outcome(s), mediator(s), and the general analytical approach or model in words (e.g., regression-based mediation, longitudinal mediation), using the terminology from the protocol and without mathematical formulae.
        - For each exploratory moderation analysis, briefly state the outcome(s), moderator(s), and how moderation will be examined in general terms (e.g., inclusion of treatment-by-moderator interaction terms in the relevant model), as described in the protocol.
        - Make clear that these analyses are exploratory and, if stated in the protocol, note whether they are intended for the main statistical report/primary paper or for separate reporting/SAP.
        - Write the output as one short paragraph (no bullet points in the output itself), providing enough detail to convey the planned outcomes, mediators/moderators, and general model structure, but without introducing new methods.
        - If the protocol does not describe any exploratory mediation or moderation analyses, return exactly the sentence: "No exploratory mediation or moderation analyses are planned."
        - Do not infer or invent outcomes, mediators, moderators, or analytical approaches that are not explicitly reported in the protocol.
        """,

        
        "interim_analysis": """
        - Using only the extracted information from the clinical trial protocol, write a section on Interim Analysis for inclusion in the Statistical Analysis Plan (SAP).
        - First, clearly state whether any interim analysis is planned in the study.
        - If an interim analysis is planned, describe in concise prose:
          - the objectives and timing of the interim analysis or internal pilot (e.g., information fraction, calendar time, recruitment milestones, or follow-up duration),
          - the statistical methods and any stopping rules or decision criteria to be used (e.g., for efficacy, futility, or safety),
          - any adjustments to significance levels or sample size (e.g., alpha spending, group-sequential design, sample size re-estimation),
          - and, where specified, the roles and responsibilities of the Data Monitoring Committee or equivalent oversight body.
        - Write the output as one or more short paragraphs; do not use bullet points in the output itself unless the protocol presents key elements as a list that must be preserved.
        - If no interim analysis is planned, return exactly the sentence: "No interim analyses are planned, and no adjustments to significance levels will be made."
        - Do not infer or invent interim analyses, timings, stopping rules, or alpha/sample-size adjustments that are not explicitly reported in the protocol; if certain aspects are mentioned but not detailed (e.g., stopping boundaries), state briefly that further details are not specified in the protocol.
        """,





    }

PROMPTS_DICTIONARY = PROMPTS_TITLE_ADMIN | PROMPTS_INTRO_AND_DESIGN |PROMPTS_PEOPLE | PROMPTS_OUTCOMES_AND_ANALYSIS

