from auto_sap.classes.template_class import Template
from auto_sap.classes.prompt_register_class import PromptRegister

from auto_sap.prompts import prompts_06 as prompts_file
from importlib.resources import files

import time 

#reasoning_effort ="high", "medium", or "low", "minimal"
# verbosity = "high", "medium", or "low"
#PromptRegister(variable, prompt_function, reasoning_effort, verbosity)
prompt_tasks = [
    PromptRegister("title", "low","low"),
    PromptRegister("trial_acronym", "minimal","low"),
    PromptRegister("isrctn_number", "minimal","low"),
    PromptRegister("protocol_version_date", "minimal", "low"),
    PromptRegister("name_of_cheif_investigator", "low","low"),
    PromptRegister("senior_statistician", "low","low"),
    PromptRegister("trial_statistician", "low","low"),
    PromptRegister("description_of_trial", "medium","low"),
    PromptRegister("investigators", "low","low"),
    PromptRegister("trial_manager", "low","low"),
    PromptRegister("trial_statisticians", "low","low"),
    PromptRegister("health_economist", "low","low"),
    PromptRegister("primary_objectives", "minimal","low"),
    PromptRegister("secondary_objectives", "minimal","low"), 
    PromptRegister("trial_design", "minimal","low"),
    PromptRegister("randomisation_method", "minimal","low"),
    PromptRegister("randomisation_implementation", "minimal","low"),
    PromptRegister("duration_of_treatment", "minimal","low"),
    PromptRegister("follow_up_timepoints", "minimal","low"),
    PromptRegister("visit_windows", "low","low"),
    PromptRegister("data_collection_procedures", "minimal","low"), 
    PromptRegister("inclusion_criteria", "minimal","low"),
    PromptRegister("exclusion_criteria", "minimal","low"), # end of first section - trial design
    PromptRegister("primary_outcome_measures", "medium","low"),
    PromptRegister("secondary_outcome_measures", "medium","low"),
    PromptRegister("mediator_of_treatment", "low","low"),
    PromptRegister("moderator_of_treatment", "low","low"), 
    PromptRegister("process_indicators", "low","low"),
    PromptRegister("adverse_events", "low","low"),
    #PromptRegister("only_baseline_measures", "low","low"),
    #PromptRegister("additional_follow_up_measures", "low","low"),
    PromptRegister("sample_size", "low","low"),
    PromptRegister("timing_of_analysis", "low","low"),
    #PromptRegister("screening_recruitment_consort", "minimal","low"),
    #PromptRegister("treatment_compliance_definitition", prompts_file.generate_treatment_compliance_definitition_prompt,"minimal","low"),
    PromptRegister("adherence_to_treatment", "minimal","low"),
    #PromptRegister("descriptive_statistics", "minimal","low"),
    PromptRegister("descriptive_of_intervention", "minimal","low"),
    PromptRegister("descriptive_concomitant_medications", "minimal","low"),
    PromptRegister("visit_window_deviation", "minimal","low"), # end of second section - outcomes and descriptive analysis
    PromptRegister("primary_estimand", "minimal","low"),
    PromptRegister("estimand_population","minimal","low"),
    PromptRegister("estimand_endpoint","minimal","low"),
    PromptRegister("estimand_tcond","minimal","low"),  
    PromptRegister("estimand_popsum","minimal","low"),
    PromptRegister("estimand_intercurrent","medium","low"),             
    #PromptRegister("confidence_interval_p_value", "minimal","low"),
    PromptRegister("primary_analysis_model", "minimal","low"),
    PromptRegister("intercurrent_events_and_analysis", "minimal","low"), 
    #PromptRegister("secondary_estimands", "minimal","low"),
    PromptRegister("secondary_analysis", "minimal","low"),
    #PromptRegister("time_points", "minimal","low"),  # end of third section - main analysis
    #PromptRegister("stratification_and_clustering", "minimal","low"),
    PromptRegister("missing_items_in_scales", "minimal","low"),
    #PromptRegister("missing_baseline_data", "minimal","low"),
    PromptRegister("missing_data_sensitivity_analysis", "minimal","low"),
    PromptRegister("multiple_comparisons", "minimal","low"),
    PromptRegister("analysis_for_noncompliance","minimal","low"),
    PromptRegister("model_assumption_checks", "minimal","low"),
    PromptRegister("other_sensitivity_analysis", "minimal","low"),
    PromptRegister("subgroup_analysis", "minimal","low"),
    #PromptRegister("any_additional_exploratory_analysis", "minimal","low"),
    PromptRegister("any_exploratory_mediator_and_moderator_analysis", "minimal","low"),
    PromptRegister("interim_analysis", "minimal","low"), # end of final section - other bits
    PromptRegister("table_outcomes", "medium","low"),
]


# Set up template with template file and prompts   
kcl_template_v02 = Template(
    template_path = files("auto_sap").joinpath("templates/sapai_kcl_template_v0.2_clean.docx"), 
    system_message_function=prompts_file.system_message, 
    prompt_register=prompt_tasks,
    prompts_dictionary = prompts_file.PROMPTS_DICTIONARY,
    template_name = "sapai_kcl_template_v0.2_clean.docx", # this is identifying information that is recorded in the SAP
    prompts_name = "v6, 04/12/2025"
)


