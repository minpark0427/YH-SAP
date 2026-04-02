from auto_sap.classes.template_class import Template
from auto_sap.classes.prompt_register_class import PromptRegister
from auto_sap.classes.chat_classes import OpenAIChat
from auto_sap.classes.auto_code_classes import run_autocode_with_conversation

from auto_sap.prompts import prompts_06 as prompts_file
from importlib.resources import files
import time

# ----------------------------------------------------------------------
# Prompt setup
# ----------------------------------------------------------------------
# reasoning_effort = "high", "medium", "low", or "minimal"
# verbosity       = "high", "medium", or "low"
# PromptRegister(variable, reasoning_effort, verbosity)

prompt_tasks = [
    PromptRegister("title", "minimal", "low"),
    PromptRegister("trial_acronym", "minimal", "low"),
    PromptRegister("primary_outcome_measures", "minimal", "low"),
    PromptRegister("secondary_outcome_measures", "minimal", "low"),
    PromptRegister("timing_of_analysis", "minimal", "low"),
    PromptRegister("primary_analysis_model", "minimal", "low"),
    PromptRegister("secondary_analysis", "minimal", "low"),
]

# ----------------------------------------------------------------------
# Template instance used across helpers
# ----------------------------------------------------------------------

simple_template = Template(
    template_path=files("auto_sap").joinpath("templates/sapai_kcl_template_v0.2_clean.docx"),
    system_message_function=prompts_file.system_message,
    prompt_register=prompt_tasks,
    prompts_dictionary=prompts_file.PROMPTS_DICTIONARY,
    template_name="simple test template",  # identifying information recorded in the SAP
    prompts_name="v6, 04/12/2025",
)

# ----------------------------------------------------------------------
# Helper: run SAP generation from a protocol text
# ----------------------------------------------------------------------


def get_sap_content_for_protocol(protocol_txt: str, model: str = "gpt-5-nano"):
    """
    Convenience wrapper to populate the template using a protocol text.

    This will:
      - call simple_template.get_sap_content(...)
      - populate simple_template.sap_content (usually a dict of sections)
    """
    simple_template.get_sap_content(protocol_txt, model=model)
    return simple_template


# ----------------------------------------------------------------------
# Helper: build content_dictionary for the autocode pipeline
# ----------------------------------------------------------------------


def build_autocode_content_dictionary_from_sap() -> dict[str, str]:
    """
    Build the content_dictionary expected by AutoCodePipeline / run_autocode_with_conversation.

    Preferred behaviour:
      - If simple_template.sap_content is a dict (the usual case), we use specific
        sections to feed each extractor.
      - If it's a plain string, we fall back to giving the full SAP text to all three.

    Heuristic mapping when sap_content is a dict:
      - timepoint_content:
          primary_outcome_measures
          + secondary_outcome_measures
          + timing_of_analysis
          + primary_analysis_model
          + secondary_analysis

      - variables_content:
          primary_outcome_measures
          + secondary_outcome_measures
          + primary_analysis_model
          + secondary_analysis

      - analysis_content:
          primary_analysis_model
          + secondary_analysis
          + timing_of_analysis
    """

    sap_data = getattr(simple_template, "sap_content", "")

    # Case 1: sap_content is already a dict of sections (most likely in your setup)
    if isinstance(sap_data, dict):

        def get_section(key: str) -> str:
            val = sap_data.get(key, "")
            return val if isinstance(val, str) else ""

        # Build each "view" as a concatenation of relevant sections
        timepoint_content = "\n\n".join(
            [
                get_section("primary_outcome_measures"),
                get_section("secondary_outcome_measures"),
                get_section("timing_of_analysis"),
                get_section("primary_analysis_model"),
                get_section("secondary_analysis"),
            ]
        )

        variables_content = "\n\n".join(
            [
                get_section("primary_outcome_measures"),
                get_section("secondary_outcome_measures"),
                get_section("primary_analysis_model"),
                get_section("secondary_analysis"),
            ]
        )

        analysis_content = "\n\n".join(
            [
                get_section("primary_analysis_model"),
                get_section("secondary_analysis"),
                get_section("timing_of_analysis"),
            ]
        )

        content_dictionary = {
            "timepoint_content": timepoint_content or "",
            "variables_content": variables_content or "",
            "analysis_content": analysis_content or "",
        }
        return content_dictionary

    # Case 2: sap_content is a single string – fall back to "full-doc everywhere"
    sap_text = sap_data or ""
    if not isinstance(sap_text, str):
        # Just in case someone changed Template internals
        sap_text = str(sap_text)

    content_dictionary = {
        "timepoint_content": sap_text,
        "variables_content": sap_text,
        "analysis_content": sap_text,
    }
    return content_dictionary


# ----------------------------------------------------------------------
# End-to-end helper returning an AutoCodeConversation
# ----------------------------------------------------------------------


def get_autocode_conversation_for_protocol(
    protocol_txt: str,
    model: str = "gpt-5-nano",
    validate: bool = False,
):
    """
    End-to-end helper that:
      1) runs the SAP generation for a given protocol text
      2) builds the autocode content_dictionary from the SAP content
      3) runs the AutoCodePipeline wrapped in an AutoCodeConversation
      4) returns an AutoCodeConversation object for interactive editing

    Usage:

        convo = get_autocode_conversation_for_protocol(protocol_txt)
        # initial JSON:
        convo.result["timepoints"]

        # user says: "no, you've added an extra timepoint at 6 months..."
        convo.apply_user_edit("timepoints", user_message)

        # final JSON:
        final_json = convo.result
    """

    # Step 1: populate the template from the protocol text
    get_sap_content_for_protocol(protocol_txt, model=model)

    # Step 2: build content dictionary from the SAP (section-aware if possible)
    content_dictionary = build_autocode_content_dictionary_from_sap()

    # Step 3: set up chat bot and run autocode pipeline with conversational wrapper
    chat_bot = OpenAIChat(model_name=model)
    convo = run_autocode_with_conversation(
        chat_bot=chat_bot,
        content_dictionary=content_dictionary,
        validate=validate,
    )

    return convo
