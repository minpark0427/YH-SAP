"""
Multi-step generation for high-complexity SAP sections.

Step 1 (extraction): Extract key facts from protocol context (low reasoning)
Step 2 (generation): Generate SAP section using extracted facts + original prompt (high reasoning)
"""

HIGH_COMPLEXITY_TAGS = ["primary_efficacy", "secondary_efficacy", "sample_size"]

# Step 1 extraction prompts — designed to pull structured facts from protocol
_EXTRACTION_PROMPTS: dict[str, str] = {
    "primary_efficacy": """
From the protocol sections provided, extract the following information as bullet points.
If any item is not found, state "Not specified in protocol."

- Primary endpoint(s): exact definition and measurement timepoint(s)
- Primary analysis set (e.g., FAS, PPS, Safety Set)
- Statistical model or test planned for primary analysis (e.g., ANCOVA, MMRM, t-test, descriptive)
- Covariates or stratification factors in the model
- Significance level (alpha) and whether one-sided or two-sided
- Multiplicity adjustment method (if applicable)
- Sensitivity analyses planned for primary endpoint
- Estimand framework details (if specified)
- How results will be presented (e.g., LS means, CI, p-values, descriptive statistics)

Extract ONLY what is stated in the protocol. Do not infer or add information.
""",

    "secondary_efficacy": """
From the protocol sections provided, extract the following information as bullet points.
If any item is not found, state "Not specified in protocol."

- All secondary endpoint(s): exact definitions and measurement timepoints
- Analysis method for each secondary endpoint
- Whether secondary endpoints use the same model as primary
- Analysis set for secondary analyses
- Multiplicity adjustment for secondary endpoints (if applicable)
- Any hierarchical testing strategy

Extract ONLY what is stated in the protocol. Do not infer or add information.
""",

    "sample_size": """
From the protocol sections provided, extract the following information as bullet points.
If any item is not found, state "Not specified in protocol."

- Primary endpoint on which sample size is based
- Statistical test or model used for the calculation
- Assumed effect size or treatment difference
- Assumed standard deviation or variability parameter
- Assumed event rate(s) (if applicable)
- Significance level (one-sided or two-sided)
- Target power
- Dropout/attrition rate adjustment
- Any multiplicity or interim analysis adjustments
- Final planned sample size per group and total
- Any additional assumptions or justifications

Extract ONLY what is stated in the protocol. Do not infer or add information.
""",
}


class MultiStepGenerator:
    """Two-step generation for high-complexity SAP sections."""

    def __init__(self) -> None:
        self.extraction_prompts = dict(_EXTRACTION_PROMPTS)

    async def generate(
        self,
        tag: str,
        context: str,
        sap_prompt: str,
        system_message_fn,
        chat_class,
        model: str,
        reasoning_effort: str = "high",
        verbosity: str = "low",
    ) -> str:
        """Run 2-step generation: extract → generate.

        Args:
            tag: SAP section tag (e.g., "primary_efficacy")
            context: assembled protocol context for this tag
            sap_prompt: original SAP generation prompt
            system_message_fn: function(context) → system message string
            chat_class: async chat class to instantiate (e.g., ClaudeCodeChatAsync)
            model: model name
            reasoning_effort: for step 2 (step 1 always uses "low")
            verbosity: verbosity setting
        """
        extraction_prompt = self.extraction_prompts.get(tag)
        if not extraction_prompt:
            raise ValueError(f"No extraction prompt for tag: {tag}")

        # Step 1: Extract key facts (low reasoning, fast)
        sys_msg_extract = system_message_fn(context)
        bot_extract = chat_class(model_name=model, system_message=sys_msg_extract)
        response_1 = await bot_extract.get_response(
            prompt=extraction_prompt,
            reasoning_effort="low",
            verbosity="low",
        )
        extracted_facts = (response_1.get("content", "") or "").strip()

        if not extracted_facts or extracted_facts == "ERROR":
            # Fallback: skip extraction, use original context directly
            print(f"WARNING: Extraction failed for {tag}, falling back to single-step")
            sys_msg_gen = system_message_fn(context)
            bot_gen = chat_class(model_name=model, system_message=sys_msg_gen)
            response = await bot_gen.get_response(
                prompt=sap_prompt,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity,
            )
            return (response.get("content", "") or "").strip() or "ERROR"

        # Step 2: Generate SAP section using extracted facts
        enhanced_context = (
            f"=== EXTRACTED KEY FACTS ===\n{extracted_facts}\n\n"
            f"=== PROTOCOL CONTEXT ===\n{context}"
        )
        sys_msg_gen = system_message_fn(enhanced_context)
        bot_gen = chat_class(model_name=model, system_message=sys_msg_gen)
        response_2 = await bot_gen.get_response(
            prompt=sap_prompt,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        )
        result = (response_2.get("content", "") or "").strip()
        return result or "ERROR"
