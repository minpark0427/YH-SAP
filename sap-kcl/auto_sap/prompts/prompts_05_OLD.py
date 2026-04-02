



def system_message(part_protocol):
    system_message = f"""you are an expert statistician in the field of clinical trials.
    you are givena a clinical trial protocol with a full detail of the study design, including the primary 
    and secondary endpoints, sample size, and methods of statistical analysis and will be asked to write sections for a statistical analysis plan based on a clinical trial protocol.

    your answers always should be in the form of Statistical Analysis Plan (SAP). Only include in your response content that would be included in the specific section of a statistical analysis plan.
    
    Be concice. Write analysis section in paragrpahs, only use bullet points where specified in the prompt.
    
    The protocol for the trial is:
     
     {part_protocol}
    """

    return(system_message)





# 1 -------------------------------------------------------------------------

def generate_admin_prompt():
    prompt = f"""
    Extract and write the Administrative Information section for a 
    comprehensive Statistical Analysis Plan (SAP) based on the clinical trial protocol. 


    Instructions:

    Please identify and clearly present the following administrative elements based on the content of the protocol:

    Full trial title
    
    Trial registration details (registry name, registration number, and registration date). This will be either ISRCTN or ClinicalTrials.gov. Do not include details of other registrations.

    Protocol number and version (including version date)

    Names, and affiliations of:
    
    Chief investigator / Principal investigator
    Trial statistician(s)
    
    Do not include addresses for investigators or statisticians. Examples of sufficient infomration would be:
    
    Chief Investigator: Dr. Ben Carter, Kings College London Clinical Trials Unit, Institute of Psychiatry, Psychology and Neuroscience, King's College London 

    Write this section in a clear and detailed format suitable for inclusion in the SAP. 
    Use paragraphs or bullet points as appropriate. 
    Focus only on administrative and contributor-related information—do not extract study objectives, 
    endpoints, methodology, or statistical methods in this prompt.

    """
    return prompt



# 2 ---------------------------------------------------------------------
# i want to write a second prompt to ask to write the introduction and desing of the SAP based on the extracted information from protocol
def generate_introduction_prompt():
    prompt = f"""
    Based on the clinical trial protocol, please write a detailed introduction for the Statistical Analysis Plan (SAP).

    Instructions:

    1. Write a brief introduction that outlines the background and rationale for the study and the study objectives.
    2. The background and rationale should consist of a synopsis of trial the background and rationale including a brief description of research question and brief justification for undertaking the trial
    3. Clearly state specific objectives or hypothesis.
    3. Write this section using full paragraphs Do not use bullet points.
    4. Do not write about the statistical analysis.

    """
    return prompt





# 3 -----------------------------------------------------------------------
def generate_study_design_prompt():
    prompt = f"""
    Using the extracted information from the clinical trial protocol, please write a Study Design section for the Statistical Analysis Plan (SAP).

    The extracted information is as follows:


    Instructions:

    1. Provide a general description of the study design (e.g., parallel, crossover, factorial, cluster-randomized, adaptive, etc.). Do not include detials on the objectives of the study.
    2. Describe the numer of arms and allocation ratio (e.g., 1:1, 2:1). Do not include details of the randomisation process.
    3. Provide a brief description of each arm.
    4. Specify the  hypothesis testing framework eg. superiority, non-inferiority, equivalence, etc. Where applicable specify which comparisons will be based on which framework. 
    5. Do not include details of the study objectives.
    6. Write in full detail, using paragraphs and clear explanations. Only use bullet points if absolutely necessary.
    7. Focus only on the Study Design section as outlined above.

    """
    return prompt

# 3 -----------------------------------------------------------------------
def generate_randomisation_prompt():
    prompt = f"""
    Using the extracted information from the clinical trial protocol, please write a Randomisation section for the Statistical Analysis Plan (SAP).

    The extracted information is as follows:

    # Instructions:

    1. Describe the randomization process, including the method used, and any stratification factors.
    2. Write in full detail, using paragraphs and clear explanations. Only use bullet points if absolutely necessary.
    3. Focus only on the Randomisation section as outlined above.

    # Examples:

    ## Example 1
    Participants were randomised to either the intervention or control group using a computer-generated randomization sequence. Randomization was conducted using stratified permuted blocks, with block sizes of 4 and 6, stratified by age group and site.

    ## Example 2
    Participants were randomised to either the intervention or control group. Randomisation will use minimisation with a random component, such that participants are allocated to the treatment arm that minimises imbalance with a probability of 0.9. Minimisation factors were sex (male/female) and symptom severity (low/medium/high).

    """
    return prompt




# 4 ---------------------------------------------------------------------
def generate_sample_size_prompt():
    prompt = f"""
    Using the extracted information from the clinical trial protocol, please write a comprehensive Sample Size and Power section for the Statistical Analysis Plan (SAP).

    The extracted information is as follows:


    Instructions:

    1. Describe in detail the methods used for sample size calculation.
    2. Clearly state all assumptions used in the calculation, including effect size, standard deviation, event rates, and any other relevant parameters.
    3. Specify the statistical tests considered for the sample size estimation.
    4. Report the planned power and significance levels for the study.
    5. Report any adjustments made for anticipated dropouts, losses to follow-up, and missing data.
    6. Do not provide any justifcations or explenation for the methods used, just state the methods and parameters. 
    6. Write full paragraphs, be concise focuing on the points above only.
    6. Do not include any mathematical formula
    7. Focus only on the Sample Size and Power section as outlined above.

    """
    return prompt



# 5 ---------------------------------------------------------------------



# 8 ---------------------------------------------------------------------
def generate_interim_analysis_prompt():
    prompt = f"""
    Using the clinical trial protocol, please write a section on Interim Analysis and Internal Pilot  for the Statistical Analysis Plan (SAP).

    The extracted information is as follows:


    Instructions:

    1. Clearly state whether any interim analysis or internal pilot is planned in the study.
    2. If interim analysis or internal pilot is specified, provide full details including:
        - The objectives and timing of the interim analysis or internal pilot
        - The statistical methods and stopping rules to be used
        - Any adjustments to significance levels or sample size
        - The roles and responsibilities of the Data Monitoring Committee or equivalent
    3. If no interim analysis or internal pilot is planned, state in one clear sentence that these are not included in this study and that no adjustments to significance levels will be made.
    4. Write in clear paragraphs; use bullet points only if absolutely necessary.
    5. Focus only on the Interim Analysis and Internal Pilot section as outlined above.
    """
    return prompt

def generate_timing_prompt():
    prompt = f"""
    Using the clinical trial protocol, please write a section on timing of final analysis and outcome data collection for the Statistical Analysis Plan (SAP).

    The extracted information is as follows:


    Instructions:

    1. Clearly state the timing of the final analysis, eg, all outcomes analyzed collectively after all data is collected and the database is locked or timing stratified by planned length of follow-up
    2. State the time points at which the outcomes are measured including visit “windows”
    3. Write in clear paragraphs; use bullet points only if absolutely necessary.
    4. Focus only on the timing of final analysis and outcome data collection section as outlined above.
    """
    return prompt
   

# 9 ---------------------------------------------------------------------
def generate_analysis_considerations_prompt():
        prompt = f"""
        Using the trial protocol, please write a comprehensive general analysis principles section for the Statistical Analysis Plan (SAP).
        
        ## Instructions
        
        Include information on the following:
                
        The level of statistical significance to be used and confidence intervals to be reported
        Description and rationale for any adjustment for multiplicity and, if so, detailing how the type 1 error is to be controlled. If no adjustments are to be made it is sufficient to state "No adjusments for multiple testing will be made.".
        Definition of adherence to the intervention and how this is assessed including extent of exposure
        Description of how adherence to the intervention will be presented
        Definition of protocol deviations for the trial
        Description of which protocol deviations will be summarized
        Definition of analysis populations, eg, intention to treat, per protocol, complete case, safety. Only define populations that are mentioned in the protocol.
        
        Ensure your reposne is written as paragraphs. Do not use bullet points or numbered list unless absolutely necessary. Be concice. Do not provide rationale for analysis choices, just state the approah taken.
        
        ## Example
        All hypothesis testing will be two-sided, with a nominal level of statistical significance set at 5% (α = 0.05). For the estimation of treatment effects, 95% confidence intervals (CIs) will be presented alongside p-values. No adjusments for multiple testing will be made.
        
        Adherence to the trial intervention will be assessed at each 6-monthly visit via a pill count of returned investigational medicinal product. As defined in the protocol, a participant will be considered adherent if they have consumed at least 50% of the expected number of tablets during the period between visits. Adherence will be summarised descriptively by treatment arm at each visit and for the overall treatment period. The summary will include the number and percentage of adherent participants, as well as continuous summaries of the percentage of medication taken (e.g., mean, standard deviation, median, and interquartile range).
        
        Protocol deviations will be categorized into two types: minor deviations and major violations. A minor protocol deviation is defined as a non-serious breach from the protocol that is unlikely to significantly impact the study's scientific integrity or participant safety. Examples include minor timing variations in study visits or incomplete questionnaire responses. A protocol violation is a more serious departure from the protocol that could substantially affect the study's validity, such as randomization errors, significant eligibility criteria breaches, or major non-compliance with the intervention.

        The trial will summarize protocol deviations by categorizing them according to type. This summary will include the number and percentage of participants with each type of deviation, stratified by treatment arm. Major protocol violations that could potentially bias the study results will be explicitly identified and their potential impact on the analysis discussed.
        
        The primary analysis population will be the intention-to-treat (ITT) population, which includes all randomized participants with completed outcomes, analyzed according to their initial treatment allocation, regardless of protocol adherence or subsequent treatment changes.
        
        A per-protocol (PP) population will also be defined, excluding participants with major protocol violations or those who do not meet key eligibility criteria upon detailed review. A safety population will be defined as all participants who received at least one dose of the investigational medicinal product and had at least one post-baseline safety assessment.

        """
        return prompt


def generate_trial_population_prompt():
    prompt = f"""
    
        # Instruction
        Using the trial protocol, please write a trial population section for the Statistical Analysis Plan (SAP).

        Include information on the following:

        Reporting of screening data (if collected) to describe representativeness of trial sample
        Summary of eligibility  including both inclusion and exclusion criteria
        Information to be included in the CONSORT flow diagram including the number of participants at each follow up point.
        Level of withdrawal, eg, from intervention and/or from follow-up
        The timepoints at which withdrawal/lost to follow-up data will be presented 
        How withdrawal/lost to follow-up data will be presented including what details will be summarised
        List of baseline characteristics to be summarized
        Details of how baseline characteristics will be descriptively sumarised. Do not include details of statistical tests for imbalance in baseline characteristics.

        Ensure your reposne is written as paragraphs. Do not use bullet points or numbered list exceot fir the eligibility criteria. 
        Do not provide justification for analysis choices, just specify what will be done.


        """
    return prompt


# Example

# Participants will be described with respect to age, gender, time since diagnosis, cancer type, performance status, the number of previous chemotherapies and presence of brain metastases at baseline.
# Baseline data will be summarised by randomised groups using mean and standard deviation for continuous data, median, interquartile range for time to event data, and counts and percentages fopr binary and catagorical data.
# No statistical tests for imbalance in baseline covariates will be performed.

def generate_endpoint_prompt():
    prompt = f"""
    Using the clinical trial protocol, please write a outcomes definition section for the Statistical Analysis Plan (SAP).
   
    # Instructions:
    
    List and describe each primary and secondary outcome including details of:
    
        Speicfication of outcome
        Timing of assessment
        Specific measurement units if applicable
        Any transformations or calculations used to derive the outcome.
        
    Use a single paragraph to describe each outcome. Do not use subheaders withing outcome descriptions. Write a separeate paragraph for each outcome, even if given together in the protocol.
    
    Do not report health or cost utility outocmes

    #Examples: 

    ## Example 1:

    protocl text: Rate of readmission to hopsital within 30 or 90 days of discharge, survival (overall, progression-free).

    correct output:
    Number of particiapants readmitted to hospital within 30 days of discharge. 
    Number of participants readmitted to hospital within 90 days of discharge. 
    Time to death from any cause (overall survival), assessed from randomisation to death or final follow-up.
    Time to disease progression or death (progression-free survival), assessed from randomisation to disease progression,  death, or final follow up.

  



    """
    return prompt

def generate_inferential_analysis_prompt():
        prompt = f"""
        Using the extracted information from the clinical trial protocol, please write a main analysis section for all primary and secondary outcomes. Do not give analysis methods for outcomes relating to health economics or cost utility.

        # Instructions:
        Analysis model and covariates
        - Specify the analysis population to be used. Do not describe the analysis population, just state it.eg. 
For all primary and secondary outcomes, analyses will be conducted on the intention-to-treat (ITT) population.
        - Speficy how treatment effects will be presented
        - Describe the analysis model to be used
        - Specify any adjustment for baseline covariates. If stratified randomisation is used, analysis models should adjust for stratification factors. Where possible adjust for baseline assessments of outcome. 
        - Where different outcomes are of the same type, and will be analysed with the same model describe them together. Explicitly state which outcomes are being analysed with the same approach.


        Be concice. Write analysis section in paragrpahs, do not use bullet points. Analysis should be described with engough detail to be implemented and there should be no ambiguity.
        
        # Example:

        The primary outcome of time to death from any cause will be analysed using a Cox proportional hazards model, with treatment group as the main effect. The model will adjust for age as a continuous covariate and sex as a binary covariate (male/female). The treatment effect will be presented as a hazard ratio with 95% confidence interval.
        Binary secondary outcomes (readmission to hospital within 30 days, readmission to hospital within 90 days) will be analysed using logistic regression, adjusting for age and sex as with the primary outcome.

        """
        return prompt

def generate_assumptions_sensitivity_analysis_prompt():
        prompt = f"""
        Using the extracted information from the clinical trial protocol, please write a section on assumptions and sensitivity analysis for the Statistical Analysis Plan (SAP).

        Instructions:
        - Describe any assumption checks that will be carried out for the analysis model 
        - Do not describe subgroup analysis.
        - If any assumptions are violated, specify in detail how this will be handled in the analysis (e.g., alternative models, data transformation, non-parametric methods).
        - Describe any other planned sensitivity analyses including the rationale and methods. Include full details of how the sensitivity analysis will be implemented.


        Be concise. Write analysis section in paragraphs, do not use bullet points. Analysis should be described with enough detail to be implemented and there should be no ambiguity.

        """
        return prompt



def generate_subgroup_analysis_prompt():
        prompt = f"""
        Using the extracted information from the clinical trial protocol, please write a section on subgroup analysis for the Statistical Analysis Plan (SAP).

        Instructions:
        - Describe any subgroup analysis that will be conducted.
        - Subgroup analysis should be conducted by including an interaction term between an indicator for subgroup and intervention in the main analysis model.
        - If no subgroup analysis are specified in the protocol state "No subgroup analysis will be conducted."

        Be concise. Write analysis section in paragraphs, do not use bullet points. Analysis should be described with enough detail to be implemented and there should be no ambiguity.
        
        """
        return prompt

def generate_missing_data_prompt():
        prompt = f"""
        Using the extracted information from the clinical trial protocol, please write a section on missing data for the Statistical Analysis Plan (SAP).

       Instructions:
       Describe the reporting of  missing data. 
       Describe the assumptions relating to missing data eg. outcomes are analysed assuming data is missing at random conditional on the covariates included in the analysis models.
       Missing data in continuous baseline covariates should be imputed using mean imputation and using missing indicators for binary or catagorical covariates. 
       In general, missing data in outcomes should not be impuated, with analysis conducted on those with compelte outocmes only.
       Multiple impuation should only be used if there is additional auxillary information that can be included in the impuation mopdel or if specified in the protocol. If multiple imputation is not used do not mention it.
       If multiple imputaiton is specified, describe the method to be used, the number of imputations to be , and the variables that will be included in the imputation model.

        Be concice. Write analysis section in paragrpahs, do not use bullet points.

       """
        return prompt


def generate_additional_analysis():
    prompt = f"""
        Using the extracted information from the clinical trial protocol, please write a section on missing additional analysis for the Statistical Analysis Plan (SAP).

       Instructions:

        - Describe any additional analysis that will be conducted, for example mediation analysis. 
        -  Do not descirbe health economics or cost utility analysis or sensititvity analysis for the main analysis. Do not descibre subgroup analysis.
        - Describe any analysis in full details including the population to be used, the analysis model. Explicitly state the outcome to be analysed and any variables to be included in the analysis model.
        - The analysis should be described with enough detail to be implemented and there should be no ambiguity.
        - If no additional analysis are specified in the protocol state "No additional analysis will be conducted."

        Be concice. Write analysis section in paragrpahs, do not use bullet points.

       """
    return prompt






def generate_harms():
    prompt = f"""
        Using the information from the protocol, write an adverse event reporting section for the statistical analysis plan.
        
        Include detail on how safety data will be summarised. This may include information on severity, expectedness, and causality; details of how adverse events are coded or categorized; and how adverse event data will be analyzed.
        If any inferential analysis is to be used for analysis of harms, consider moving to Section 3.
        
        Be concice. Write analysis section in paragrpahs, do not use bullet points.

       """
    return prompt

def generate_statistical_software():
    prompt = f"""
        State only "All analysis will be carried out using Stata 18.5" 
        Return no other text in your response.
       """
    return prompt




# def generate_promt_harms
#    Adverse event terms should be defined and what will be reported outlined.
#    Specify to what extent events will be grouped and whether, and if so how, p-values will be presented.
#    If p-values are to be used state clearly which population will be used (e.g., ITT).
#    Sufficient detail should be included as to how adverse events are coded or categorized.
#    If any inferential analysis is to be used for analysis of harms,  consider moving to Section 3.
