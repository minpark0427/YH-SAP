from typing import Any, Dict, List, Optional, Tuple
import json
import time


# ============================================================
# BASE PIPELINE
# ============================================================

class AutoCodePipeline:
    """Complete pipeline using SAP-derived content for each extraction step"""

    def __init__(self, chat_bot, validate: bool = False):
        self.timepoint_bot = TimepointExtractor(chat_bot)
        self.variable_bot = VariableExtractor(chat_bot)
        self.analysis_bot = AnalysisExtractor(chat_bot)
        self.validation_bot = ValidationBot(chat_bot)
        self.evaluator = ExtractionEvaluator()
        self.errors: List[Tuple[str, str]] = []
        self.validate = validate

    def extract_all(self, content_dictionary: Dict[str, str]) -> Dict[str, Any]:
        """Extract all data with validation - uses specific content for each step"""

        print("=" * 60)
        print("EXTRACTION PHASE")
        print("=" * 60)

        timepoint_content = content_dictionary.get("timepoint_content", "") or ""
        variables_content = content_dictionary.get("variables_content", "") or ""
        analysis_content = content_dictionary.get("analysis_content", "") or ""

        # This is used only for validation / metrics
        input_content = (
            (timepoint_content or "")
            + "\n\n"
            + (variables_content or "")
            + "\n\n"
            + (analysis_content or "")
        )

        # Step 1: Extract timepoints
        print("[1/3] Extracting timepoints...")
        timepoints, timepoint_error = self.timepoint_bot.extract_timepoints(timepoint_content)
        if timepoint_error:
            self.errors.append(("timepoints", timepoint_error))
            print(f"\n    💬 {timepoint_error}\n")

        # Step 2: Extract variables
        print("\n[2/3] Extracting variables...")
        variables, variable_error = self.variable_bot.extract_variables(variables_content, timepoints)
        if variable_error:
            self.errors.append(("variables", variable_error))
            print(f"\n    💬 {variable_error}\n")

        # Step 3: Extract analyses
        print("\n[3/3] Extracting analyses...")
        analyses, analysis_error = self.analysis_bot.extract_analyses(analysis_content, variables)
        if analysis_error:
            self.errors.append(("analyses", analysis_error))
            print(f"\n    💬 {analysis_error}\n")

        result: Dict[str, Any] = {
            "timepoints": timepoints,
            "variables": variables,
            "analyses": analyses,
        }

        # Check if everything failed
        if not timepoints and not variables and not analyses:
            print("\n" + "=" * 60)
            print("⚠️  EXTRACTION INCOMPLETE")
            print("=" * 60)
            print("\nI tried my best, but couldn't extract anything useful. This might happen if:")
            print("  - The document is not a Statistical Analysis Plan")
            print("  - The format is very unusual or non-standard")
            print("  - Key sections are missing or poorly labeled")
            return result

        # Step 4: Validation (optional)
        validation_result: Optional[Dict[str, Any]] = None
        if self.validate and (timepoints or variables or analyses):
            print("\n" + "=" * 60)
            print("VALIDATION PHASE")
            print("=" * 60)
            print("\nValidating extraction...")
            validation_result = self.validation_bot.validate_extraction(input_content, result)

            print(f"\n  Completeness: {validation_result.get('completeness_score', 0)}/10")
            print(f"  Accuracy: {validation_result.get('accuracy_score', 0)}/10")

            if validation_result.get('issues'):
                print(f"\n  Issues found:")
                for issue in validation_result['issues'][:5]:
                    print(f"    - {issue}")

            if validation_result.get('missing_elements'):
                print(f"\n  Missing elements:")
                for missing in validation_result['missing_elements'][:5]:
                    print(f"    - {missing}")

        # Step 5: Evaluate
        print("\n" + "=" * 60)
        print("EVALUATION")
        print("=" * 60)
        metrics = self.evaluator.evaluate(input_content, result, validation_result)

        print(f"\n  Items extracted:")
        print(f"    - Timepoints: {metrics['items_extracted']['timepoints']}")
        print(f"    - Variables: {metrics['items_extracted']['variables']}")
        print(f"    - Analyses: {metrics['items_extracted']['analyses']}")
        print(f"\n  Format valid: {metrics['format_valid']}")

        if metrics['issues']:
            print(f"\n  Format issues:")
            for issue in metrics['issues']:
                print(f"    - {issue}")

        # Metadata (minimal for now)
        result["metadata"] = {
            "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "validation_enabled": self.validate,
            "metrics": metrics,
            "errors": [{"type": t, "message": m} for t, m in self.errors],
        }

        if validation_result:
            result["metadata"]["validation"] = validation_result

        if self.errors:
            print("\n" + "=" * 60)
            print("⚠️  PARTIAL SUCCESS")
            print("=" * 60)
            print(
                f"\nI managed to extract some information, "
                f"but had trouble with {len(self.errors)} section(s)."
            )

        return result

    def save_to_json(self, data: Dict[str, Any], output_path: str):
        """Save extracted data to JSON file"""
        with open(output_path, "w") as f:
            json.dump(data, indent=2, fp=f)
        print(f"\n✓ Saved to {output_path}")


# ============================================================
# BASE EXTRACTOR
# ============================================================

class AutoCodeExtractor:
    """Base class for autoCode format extraction with retry logic"""

    def __init__(self, chat_bot, max_retries: int = 1):
        self.chat_bot = chat_bot
        self.max_retries = max_retries

    def get_response(self, prompt: str) -> str:
        instructions = (
            "You are a helpful assistant that extracts structured data from "
            "statistical analysis plans. Always respond with valid JSON only."
        )
        try:
            response = self.chat_bot.get_response(prompt=prompt, system_message=instructions)
        except Exception as e:
            print(f"An error occurred while getting response: {e}")
            response = {"content": ""}
        return response.get("content", "")


# ============================================================
# EXTRACTION BOTS
# ============================================================

class TimepointExtractor(AutoCodeExtractor):
    """Bot 1: Extract timepoints"""

    def extract_timepoints(self, sap_text: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract timepoints with retry logic using SAP-derived text"""

        print(f"    Using content: {len(sap_text):,} chars")

        prompt = f"""Extract all timepoints mentioned in this Statistical Analysis Plan.

SAP Text:
{sap_text}

Your task: Find all time measurements mentioned (baseline, follow-up visits, etc.)

Return a JSON array in this EXACT format:
[
  {{"value": 0, "label": "Baseline"}},
  {{"value": 1, "label": "6 months"}}
]

Rules:
- value 0 = baseline, value 1 = first follow-up, value 2 = second follow-up, etc.
- label = exact description from SAP or the prompts
- Include ALL timepoints you find
- Output ONLY the JSON array, no explanation, no markdown
"""

        last_error = None
        for attempt in range(self.max_retries):
            response = self.get_response(prompt=prompt)

            if not response or response.strip() == "":
                last_error = "The AI returned an empty response"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Empty response, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: Empty response after {self.max_retries} attempts")
                    break

            # Clean response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            try:
                timepoints = json.loads(cleaned)

                # Validate format
                if not isinstance(timepoints, list):
                    last_error = "Response was not a list format"
                    raise ValueError("Response is not a list")

                if len(timepoints) == 0:
                    last_error = "No timepoints found in the document"
                    print(f"    ⚠ Warning: AI found 0 timepoints")
                    return [], (
                        "Sorry, I couldn't find any timepoints mentioned. "
                        "The SAP or prompts might not clearly specify when measurements are taken."
                    )

                for tp in timepoints:
                    if not isinstance(tp, dict) or "value" not in tp or "label" not in tp:
                        last_error = "Timepoints were not in the correct format"
                        raise ValueError("Invalid timepoint format")

                print(f"    ✓ Extracted {len(timepoints)} timepoints")
                return timepoints, None

            except (json.JSONDecodeError, ValueError) as e:
                last_error = f"Could not parse the AI's response as valid JSON: {str(e)}"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Parse error, retry {attempt + 1}/{self.max_retries}: {e}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: {e}")
                    print(f"    Response preview: {cleaned[:300]}")
                    break

        # Fallback message
        error_msg = (
            f"Sorry friend, I tried {self.max_retries} times but couldn't extract timepoints. "
            f"{last_error if last_error else 'Unknown error'}."
        )
        return [], error_msg


class VariableExtractor(AutoCodeExtractor):
    """Bot 2: Extract variables"""

    def extract_variables(
        self, sap_text: str, timepoints: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract variables with retry logic using SAP-derived text"""

        print(f"    Using content: {len(sap_text):,} chars")

        timepoints_str = json.dumps(timepoints, indent=2) if timepoints else "[]"

        prompt = f"""Extract all outcome variables from this Statistical Analysis Plan.

SAP Text:
{sap_text}

Available timepoints:
{timepoints_str}

Return a JSON array in this EXACT format:
[
  {{
    "label": "Primary outcome: Depression score (PHQ-9)",
    "variable_name": "phq9_total",
    "timepoints": [0, 1, 2],
    "type": "continuous"
  }}
]

Rules:
- label = human readable description
- variable_name = valid Python/R name (lowercase, underscores)
- timepoints = list of timepoint values from above
- type = one of: continuous, binary, categorical, count, time_to_event
- Output ONLY the JSON array
"""

        last_error = None
        for attempt in range(self.max_retries):
            response = self.get_response(prompt=prompt)

            if not response or response.strip() == "":
                last_error = "The AI returned an empty response"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Empty response, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: Empty response")
                    break

            # Clean response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            try:
                variables = json.loads(cleaned)

                # Validate format
                if not isinstance(variables, list):
                    last_error = "Response was not a list format"
                    raise ValueError("Response is not a list")

                if len(variables) == 0:
                    last_error = "No variables found in the document"
                    print(f"    ⚠ Warning: AI found 0 variables")
                    return [], (
                        "Sorry, I couldn't find any outcome variables. "
                        "The SAP might not clearly define primary/secondary outcomes."
                    )

                valid_types = {"continuous", "binary", "categorical", "count", "time_to_event"}
                for var in variables:
                    if not isinstance(var, dict):
                        last_error = "Variables were not in the correct format"
                        raise ValueError("Invalid variable format")
                    required = ["label", "variable_name", "timepoints", "type"]
                    if not all(k in var for k in required):
                        last_error = "Variables missing required fields"
                        raise ValueError("Missing required fields")
                    if var["type"] not in valid_types:
                        last_error = f"Invalid variable type: {var['type']}"
                        raise ValueError(f"Invalid type: {var['type']}")

                print(f"    ✓ Extracted {len(variables)} variables")
                return variables, None

            except (json.JSONDecodeError, ValueError) as e:
                last_error = f"Could not parse the AI's response: {str(e)}"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Parse error, retry {attempt + 1}/{self.max_retries}: {e}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: {e}")
                    print(f"    Response preview: {cleaned[:300]}")
                    break

        error_msg = (
            f"Sorry homie, I tried {self.max_retries} times but couldn't extract variables. "
            f"{last_error if last_error else 'Unknown error'}."
        )
        return [], error_msg


class AnalysisExtractor(AutoCodeExtractor):
    """Bot 3: Extract analyses"""

    def extract_analyses(
        self, sap_text: str, variables: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract analyses with retry logic using SAP-derived text"""

        print(f"    Using content: {len(sap_text):,} chars")

        variables_str = json.dumps(variables, indent=2) if variables else "[]"

        prompt = f"""Extract all planned statistical analyses from this Statistical Analysis Plan.

SAP Text:
{sap_text}

Available variables:
{variables_str}

Return a JSON array in this EXACT format:
[
  {{
    "name": "Primary analysis: Depression at 6 weeks",
    "model": "linear_mixed_model",
    "outcome": "phq9_total",
    "covariates": ["baseline_phq9", "age"],
    "comparison": "treatment vs control"
  }}
]

Rules:
- name = descriptive name
- model = statistical model type
- outcome = must match a variable_name from variables list
- covariates = list of covariate names (can be empty)
- comparison = what is being compared
- Output ONLY the JSON array
"""

        last_error = None
        for attempt in range(self.max_retries):
            response = self.get_response(prompt=prompt)

            if not response or response.strip() == "":
                last_error = "The AI returned an empty response"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Empty response, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: Empty response")
                    break

            # Clean response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            try:
                analyses = json.loads(cleaned)

                # Validate format
                if not isinstance(analyses, list):
                    last_error = "Response was not a list format"
                    raise ValueError("Response is not a list")

                if len(analyses) == 0:
                    last_error = "No analyses found in the document"
                    print(f"    ⚠ Warning: AI found 0 analyses")
                    return [], (
                        "Sorry, I couldn't find any statistical analyses described. "
                        "The analysis plan section might be missing or unclear."
                    )

                variable_names = {v["variable_name"] for v in variables} if variables else set()
                for analysis in analyses:
                    if not isinstance(analysis, dict):
                        last_error = "Analyses were not in the correct format"
                        raise ValueError("Invalid analysis format")
                    required = ["name", "model", "outcome"]
                    if not all(k in analysis for k in required):
                        last_error = "Analyses missing required fields"
                        raise ValueError("Missing required fields")

                    if variable_names and analysis["outcome"] not in variable_names:
                        print(
                            f"      ⚠ Warning: outcome '{analysis['outcome']}' not in variables"
                        )

                print(f"    ✓ Extracted {len(analyses)} analyses")
                return analyses, None

            except (json.JSONDecodeError, ValueError) as e:
                last_error = f"Could not parse the AI's response: {str(e)}"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Parse error, retry {attempt + 1}/{self.max_retries}: {e}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: {e}")
                    print(f"    Response preview: {cleaned[:300]}")
                    break

        error_msg = (
            f"Sorry buddy, I tried {self.max_retries} times but couldn't extract analyses. "
            f"{last_error if last_error else 'Unknown error'}."
        )
        return [], error_msg


# ============================================================
# VALIDATION BOT
# ============================================================

class ValidationBot(AutoCodeExtractor):
    """Validates extracted data against the SAP"""

    def validate_extraction(self, sap_text: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the complete extraction"""

        sap_excerpt = sap_text[:1000000]
        print(f"    Using excerpt for validation: {len(sap_excerpt):,} chars")

        prompt = f"""Review this extracted data against the Statistical Analysis Plan.

SAP Text (excerpt):
{sap_excerpt}

Extracted Data:
{json.dumps(extracted_data, indent=2)}

Return ONLY a JSON object:
{{
  "completeness_score": 8,
  "accuracy_score": 9,
  "issues": ["list any problems"],
  "missing_elements": ["list missing items"],
  "suggestions": ["improvement suggestions"]
}}

Scores are 0-10 (10 = perfect). Output ONLY JSON.
"""

        response = self.get_response(prompt=prompt)

        if not response:
            return {
                "completeness_score": 0,
                "accuracy_score": 0,
                "issues": ["Validation failed: no response"],
                "missing_elements": [],
                "suggestions": [],
            }

        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            validation = json.loads(cleaned)
            return validation
        except json.JSONDecodeError as e:
            return {
                "completeness_score": 0,
                "accuracy_score": 0,
                "issues": [f"Validation parse error: {e}"],
                "missing_elements": [],
                "suggestions": [],
            }


# ============================================================
# EVALUATION
# ============================================================

class ExtractionEvaluator:
    """Evaluate extraction quality with metrics"""

    @staticmethod
    def evaluate(
        sap_text: str, extracted_data: Dict[str, Any], validation_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate metrics for the extraction"""

        metrics: Dict[str, Any] = {
            "items_extracted": {
                "timepoints": len(extracted_data.get("timepoints", [])),
                "variables": len(extracted_data.get("variables", [])),
                "analyses": len(extracted_data.get("analyses", [])),
            },
            "format_valid": True,
            "issues": [],
        }

        try:
            timepoints = extracted_data.get("timepoints", [])
            if timepoints:
                values = [tp["value"] for tp in timepoints]
                # They don't *have* to be sequential, but it's a nice check
                if sorted(values) != values:
                    metrics["issues"].append("Timepoint values not sorted ascending")

            variables = extracted_data.get("variables", [])
            valid_timepoint_values = {tp["value"] for tp in timepoints}
            for var in variables:
                for tp_val in var.get("timepoints", []):
                    if tp_val not in valid_timepoint_values:
                        metrics["issues"].append(
                            f"Variable '{var['variable_name']}' references invalid timepoint {tp_val}"
                        )

            analyses = extracted_data.get("analyses", [])
            valid_var_names = {var["variable_name"] for var in variables}
            for analysis in analyses:
                if analysis["outcome"] not in valid_var_names:
                    metrics["issues"].append(
                        f"Analysis '{analysis['name']}' references invalid variable '{analysis['outcome']}'"
                    )

        except Exception as e:
            metrics["format_valid"] = False
            metrics["issues"].append(f"Format validation error: {e}")

        if validation_result:
            metrics["validation"] = {
                "completeness_score": validation_result.get("completeness_score", 0),
                "accuracy_score": validation_result.get("accuracy_score", 0),
                "llm_issues": validation_result.get("issues", []),
                "missing_elements": validation_result.get("missing_elements", []),
            }

        return metrics


# ============================================================
# CONVERSATIONAL WRAPPER
# ============================================================

class AutoCodeConversation:
    """
    Wraps an AutoCodePipeline result and allows conversational edits
    to timepoints / variables / analyses.
    """

    def __init__(
        self,
        chat_bot,
        pipeline: AutoCodePipeline,
        content_dictionary: Dict[str, str],
        initial_result: Dict[str, Any],
    ):
        self.chat_bot = chat_bot
        self.pipeline = pipeline
        self.content_dictionary = content_dictionary
        self.result: Dict[str, Any] = initial_result
        self.history: List[Dict[str, str]] = []  # simple text history

    # ---------------------------- internal helpers ----------------------------

    def _edit_section_with_llm(self, section_name: str, user_message: str) -> Any:
        """
        Ask the model to edit the JSON for a single section (timepoints/variables/analyses)
        based on a free-text user request.
        """

        current_section = self.result.get(section_name, [])
        current_json = json.dumps(current_section, indent=2)

        system_message = (
            "You are helping a statistician edit a structured JSON representation of a "
            "Statistical Analysis Plan. You MUST:\n"
            "- Respect the JSON schema already in use for that section.\n"
            "- Keep field names identical.\n"
            "- Only modify what the user asks you to change.\n"
            "- Return ONLY valid JSON (no comments, no markdown).\n"
        )

        prompt = f"""We are editing the '{section_name}' section.

Current JSON for {section_name}:
{current_json}

User request:
\"\"\"{user_message}\"\"\"


Update ONLY the JSON for this section to satisfy the user's request.
Return ONLY the updated JSON (no explanation, no markdown)."""

        try:
            response = self.chat_bot.get_response(prompt=prompt, system_message=system_message)
            raw = (response.get("content", "") or "").strip()
        except Exception as e:
            print(f"Edit error for section '{section_name}': {e}")
            return current_section

        # Clean potential fences
        cleaned = raw
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            updated_section = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"⚠ Failed to parse edited JSON for {section_name}: {e}")
            print(f"   Raw response (first 300 chars): {cleaned[:300]}")
            return current_section

        return updated_section

    def _infer_section_from_message(self, user_message: str) -> str:
        """
        Very simple heuristic to decide which section the user is referring to.
        """

        text = user_message.lower()

        # Obvious keywords
        if any(k in text for k in ["timepoint", "time point", "month", "visit", "follow-up", "follow up"]):
            return "timepoints"
        if any(k in text for k in ["variable", "outcome", "endpoint", "measure"]):
            return "variables"
        if any(k in text for k in ["analysis", "model", "cox", "ancova", "mixed model", "regression"]):
            return "analyses"

        # Fallback: if they mention '6 months', '12 months', etc, assume timepoints
        if any(m in text for m in ["6 months", "12 months", "18 months", "24 months", "30 months", "36 months"]):
            return "timepoints"

        # Default to timepoints (safest for manual tweaking)
        return "timepoints"

    # ---------------------------- public API ----------------------------------

    def apply_user_edit(self, section_name: str, user_message: str) -> Dict[str, Any]:
        """
        Explicitly edit one section based on a free-text instruction.
        section_name ∈ {"timepoints", "variables", "analyses"}.
        Returns the full updated result dict.
        """
        if section_name not in {"timepoints", "variables", "analyses"}:
            raise ValueError(f"Unknown section_name '{section_name}'")

        updated = self._edit_section_with_llm(section_name, user_message)
        self.result[section_name] = updated

        # Log to simple history
        self.history.append(
            {
                "role": "user",
                "section": section_name,
                "message": user_message,
            }
        )
        self.history.append(
            {
                "role": "assistant",
                "section": section_name,
                "message": f"Updated {section_name} JSON.",
            }
        )

        return self.result

    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Chatty interface: infer which section the user is talking about,
        apply the edit, return updated result.
        """
        section = self._infer_section_from_message(user_message)
        print(f"(AutoCodeConversation) Interpreting this as an edit to '{section}'")
        return self.apply_user_edit(section, user_message)


# ============================================================
# CONVENIENCE ENTRY POINT
# ============================================================

def run_autocode_with_conversation(
    chat_bot,
    content_dictionary: Dict[str, str],
    validate: bool = False,
) -> AutoCodeConversation:
    """
    Convenience function that:
      1) Runs the AutoCodePipeline on content_dictionary
      2) Wraps the result in an AutoCodeConversation
      3) Returns the conversation object for interactive editing
    """
    pipeline = AutoCodePipeline(chat_bot=chat_bot, validate=validate)
    result = pipeline.extract_all(content_dictionary)
    convo = AutoCodeConversation(
        chat_bot=chat_bot,
        pipeline=pipeline,
        content_dictionary=content_dictionary,
        initial_result=result,
    )
    return convo
