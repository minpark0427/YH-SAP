import asyncio
import subprocess
import time
import json
from openai import OpenAI, AsyncOpenAI
from anthropic import Anthropic, AsyncAnthropic
from dotenv import load_dotenv, find_dotenv

# Load .env once when the module is imported
load_dotenv(find_dotenv())

# Map reasoning_effort to max_tokens for Anthropic models
_ANTHROPIC_MAX_TOKENS = {
    "high": 8192,
    "medium": 4096,
    "low": 2048,
    "minimal": 1024,
}

# Map reasoning_effort to thinking budget_tokens for Anthropic extended thinking
_ANTHROPIC_THINKING_BUDGET = {
    "high": 10000,
    "medium": 4000,
    "low": None,
    "minimal": None,
}


class OpenAIChat:
    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        system_message: str = "You are a helpful chatbot.",
    ):
        self.model_name = model_name
        self.system_message = system_message
        # If OPENAI_API_KEY is in env, this works without passing api_key explicitly
        self.client = OpenAI()

    def get_response(
        self,
        prompt: str,
        reasoning_effort: str = "minimal",
        verbosity: str = "low",
        system_message: str | None = None,
    ):
        if system_message is None:
            system_message = self.system_message
        response = self.client.responses.create(
            model=self.model_name,
            instructions=system_message,
            input=prompt,
            reasoning={"effort": reasoning_effort},
            text={"verbosity": verbosity},
        )
        content = response.output_text.strip()
        return {"content": content}

    def run_prompts_register(self, prompt_register, system_message):
        results = {}
        for item in prompt_register:
            prompt = item.prompt_function()
            var_name = item.variable

            print(f"Running {var_name}")
            try:
                # NOTE: we're currently ignoring the `system_message` arg here;
                # if you want, you can pass it down to get_response.
                response = self.get_response(
                    prompt=prompt,
                    reasoning_effort=item.reasoning_effort,
                    verbosity=item.verbosity,
                    system_message=system_message,
                )
                response_content = (response.get("content", "") or "").strip()
                if not response_content:
                    response_content = "ERROR"
            except Exception as e:
                print(f"An error occurred: {e}")
                response_content = "ERROR"
            results[var_name] = response_content

        return results

    # >>> NEW METHOD FOR AUTOCODE CONVERSATIONAL EDITING <<<
    def edit_json_items(
        self,
        *,
        item_type: str,
        sap_context: str,
        current_json: str,
        user_instruction: str,
        reasoning_effort: str = "minimal",
        verbosity: str = "low",
        system_message: str | None = None,
    ) -> str:
        """
        Use the model to revise a JSON list (timepoints/variables/analyses)
        according to a natural-language user instruction.

        Parameters
        ----------
        item_type : str
            "timepoints", "variables", or "analyses" (only used in instructions).
        sap_context : str
            Relevant chunk of the SAP text (can be empty, or truncated).
        current_json : str
            JSON string representing the current list (e.g. result['timepoints']).
        user_instruction : str
            Free-text feedback from the user, e.g.:
            "No, you've added an extra timepoint at 6 months, can you take it out."

        Returns
        -------
        str
            JSON string with the UPDATED list (no markdown, no extra text).
        """

        if system_message is None:
            system_message = (
                "You are helping to revise a JSON list of "
                f"{item_type} extracted from a Statistical Analysis Plan (SAP).\n"
                "You will be given:\n"
                "1) Optional SAP context\n"
                "2) The current JSON list\n"
                "3) A natural-language instruction from the user\n\n"
                "Apply ONLY the requested edits while keeping everything else unchanged.\n"
                "Do NOT add explanations or comments.\n"
                "Always return VALID JSON ONLY (a JSON array) with no markdown fences."
            )

        prompt = f"""
SAP context (may be empty):
{sap_context}

Current JSON list for {item_type}:
{current_json}

User instruction:
\"\"\"{user_instruction}\"\"\"

Now return ONLY the updated JSON array for {item_type}.
"""

        response = self.get_response(
            prompt=prompt,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
            system_message=system_message,
        )
        return (response.get("content", "") or "").strip()


class OpenAIChatAsync:
    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        system_message: str = "You are a helpful chatbot.",
    ):
        self.model_name = model_name
        self.system_message = system_message
        # If OPENAI_API_KEY is in env, this works without passing api_key explicitly
        self.client = AsyncOpenAI()

    async def get_response(self, prompt: str, reasoning_effort="minimal", verbosity="low"):
        response = await self.client.responses.create(
            model=self.model_name,
            instructions=self.system_message,
            input=prompt,
            reasoning={"effort": reasoning_effort},
            text={"verbosity": verbosity},
        )
        content = response.output_text.strip()
        return {"content": content}

    async def run_prompts_register(self, prompt_register, prompt_dictionary):
        print("running prompts async for ⚡ speed")
        results = {}

        async def run_one(item):
            var_name = item.variable
            prompt = prompt_dictionary.get(var_name, "")

            print(f"Running {var_name}")
            if prompt == "":
                print(f"No prompt in prompt dictionary for {var_name}")
                response_content = "ERROR: tag not in prompt dictionary"
            else:
                try:
                    response = await self.get_response(
                        prompt=prompt,
                        reasoning_effort=item.reasoning_effort,
                        verbosity=item.verbosity,
                    )
                    response_content = (response.get("content", "") or "").strip()
                    if not response_content:
                        response_content = "ERROR"
                except Exception as e:
                    print(f"An error occurred for {var_name}: {e}")
                    response_content = "ERROR"

            return var_name, response_content

        tasks = [run_one(item) for item in prompt_register]

        for var_name, value in await asyncio.gather(*tasks):
            results[var_name] = value

        return results


class AnthropicChat:
    """Synchronous Anthropic Claude chat client — mirrors OpenAIChat."""

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-5-20250929",
        system_message: str = "You are a helpful chatbot.",
    ):
        self.model_name = model_name
        self.system_message = system_message
        self.client = Anthropic()

    def get_response(
        self,
        prompt: str,
        reasoning_effort: str = "minimal",
        verbosity: str = "low",
        system_message: str | None = None,
    ):
        if system_message is None:
            system_message = self.system_message

        max_tokens = _ANTHROPIC_MAX_TOKENS.get(reasoning_effort, 4096)
        thinking_budget = _ANTHROPIC_THINKING_BUDGET.get(reasoning_effort)

        kwargs = dict(
            model=self.model_name,
            max_tokens=max_tokens,
            system=system_message,
            messages=[{"role": "user", "content": prompt}],
        )
        if thinking_budget:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}

        response = self.client.messages.create(**kwargs)

        # Extract text from response (skip thinking blocks)
        content = ""
        for block in response.content:
            if block.type == "text":
                content = block.text.strip()
                break

        return {"content": content}

    def run_prompts_register(self, prompt_register, system_message):
        results = {}
        for item in prompt_register:
            prompt = item.prompt_function()
            var_name = item.variable

            print(f"Running {var_name}")
            try:
                response = self.get_response(
                    prompt=prompt,
                    reasoning_effort=item.reasoning_effort,
                    verbosity=item.verbosity,
                    system_message=system_message,
                )
                response_content = (response.get("content", "") or "").strip()
                if not response_content:
                    response_content = "ERROR"
            except Exception as e:
                print(f"An error occurred: {e}")
                response_content = "ERROR"
            results[var_name] = response_content

        return results


class AnthropicChatAsync:
    """Asynchronous Anthropic Claude chat client — mirrors OpenAIChatAsync."""

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-5-20250929",
        system_message: str = "You are a helpful chatbot.",
    ):
        self.model_name = model_name
        self.system_message = system_message
        self.client = AsyncAnthropic()

    async def get_response(self, prompt: str, reasoning_effort="minimal", verbosity="low"):
        max_tokens = _ANTHROPIC_MAX_TOKENS.get(reasoning_effort, 4096)
        thinking_budget = _ANTHROPIC_THINKING_BUDGET.get(reasoning_effort)

        kwargs = dict(
            model=self.model_name,
            max_tokens=max_tokens,
            system=self.system_message,
            messages=[{"role": "user", "content": prompt}],
        )
        if thinking_budget:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}

        response = await self.client.messages.create(**kwargs)

        content = ""
        for block in response.content:
            if block.type == "text":
                content = block.text.strip()
                break

        return {"content": content}

    async def run_prompts_register(self, prompt_register, prompt_dictionary):
        print("running prompts async for ⚡ speed")
        results = {}

        async def run_one(item):
            var_name = item.variable
            prompt = prompt_dictionary.get(var_name, "")

            print(f"Running {var_name}")
            if prompt == "":
                print(f"No prompt in prompt dictionary for {var_name}")
                response_content = "ERROR: tag not in prompt dictionary"
            else:
                try:
                    response = await self.get_response(
                        prompt=prompt,
                        reasoning_effort=item.reasoning_effort,
                        verbosity=item.verbosity,
                    )
                    response_content = (response.get("content", "") or "").strip()
                    if not response_content:
                        response_content = "ERROR"
                except Exception as e:
                    print(f"An error occurred for {var_name}: {e}")
                    response_content = "ERROR"

            return var_name, response_content

        tasks = [run_one(item) for item in prompt_register]

        for var_name, value in await asyncio.gather(*tasks):
            results[var_name] = value

        return results


def _claude_cli_env():
    """Return a copy of os.environ without API keys that would override subscription auth."""
    import os
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("OPENAI_API_KEY", None)
    return env


class ClaudeCodeChat:
    """Synchronous chat client using the `claude` CLI (subscription auth, no API key)."""

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-5",
        system_message: str = "You are a helpful chatbot.",
    ):
        self.model_name = model_name
        self.system_message = system_message

    def get_response(
        self,
        prompt: str,
        reasoning_effort: str = "minimal",
        verbosity: str = "low",
        system_message: str | None = None,
    ):
        sys_msg = system_message or self.system_message
        full_prompt = f"{sys_msg}\n\n{prompt}"
        # Pass prompt via stdin to avoid OS argument length limits on large protocols
        result = subprocess.run(
            ["claude", "--print", "-p", "-", "--model", self.model_name],
            capture_output=True,
            text=True,
            input=full_prompt,
            env=_claude_cli_env(),
            timeout=600,
        )
        if result.returncode != 0:
            raise RuntimeError(f"claude CLI error: {result.stderr}")
        return {"content": result.stdout.strip()}

    def run_prompts_register(self, prompt_register, system_message):
        results = {}
        for item in prompt_register:
            prompt = item.prompt_function()
            var_name = item.variable

            print(f"Running {var_name}")
            try:
                response = self.get_response(
                    prompt=prompt,
                    reasoning_effort=item.reasoning_effort,
                    verbosity=item.verbosity,
                    system_message=system_message,
                )
                response_content = (response.get("content", "") or "").strip()
                if not response_content:
                    response_content = "ERROR"
            except Exception as e:
                print(f"An error occurred: {e}")
                response_content = "ERROR"
            results[var_name] = response_content

        return results


class ClaudeCodeChatAsync:
    """Async chat client using the `claude` CLI via subprocess (no API key needed).

    max_concurrent limits parallel subprocess spawns to avoid overwhelming the system.
    """

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-5",
        system_message: str = "You are a helpful chatbot.",
        max_concurrent: int = 4,
    ):
        self.model_name = model_name
        self.system_message = system_message
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def get_response(self, prompt: str, reasoning_effort="minimal", verbosity="low",
                           max_retries: int = 2):
        full_prompt = f"{self.system_message}\n\n{prompt}"
        loop = asyncio.get_event_loop()

        def _run():
            return subprocess.run(
                ["claude", "--print", "-p", "-", "--model", self.model_name],
                capture_output=True,
                text=True,
                input=full_prompt,
                env=_claude_cli_env(),
                timeout=600,
            )

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                async with self.semaphore:
                    result = await loop.run_in_executor(None, _run)
                if result.returncode != 0:
                    last_error = f"claude CLI error: {result.stderr[:200]}"
                    if attempt < max_retries:
                        print(f"  Retry {attempt+1}/{max_retries}: {last_error[:80]}")
                        await asyncio.sleep(2)
                        continue
                    raise RuntimeError(last_error)
                content = result.stdout.strip()
                if not content and attempt < max_retries:
                    print(f"  Retry {attempt+1}/{max_retries}: empty response")
                    await asyncio.sleep(2)
                    continue
                return {"content": content}
            except subprocess.TimeoutExpired:
                last_error = "timeout"
                if attempt < max_retries:
                    print(f"  Retry {attempt+1}/{max_retries}: timeout")
                    await asyncio.sleep(2)
                    continue
                raise

        return {"content": ""}

    async def run_prompts_register(self, prompt_register, prompt_dictionary):
        print("running prompts async via claude CLI ⚡")
        results = {}

        async def run_one(item):
            var_name = item.variable
            prompt = prompt_dictionary.get(var_name, "")

            print(f"Running {var_name}")
            if prompt == "":
                print(f"No prompt in prompt dictionary for {var_name}")
                response_content = "ERROR: tag not in prompt dictionary"
            else:
                try:
                    response = await self.get_response(
                        prompt=prompt,
                        reasoning_effort=item.reasoning_effort,
                        verbosity=item.verbosity,
                    )
                    response_content = (response.get("content", "") or "").strip()
                    if not response_content:
                        response_content = "ERROR"
                except Exception as e:
                    print(f"An error occurred for {var_name}: {e}")
                    response_content = "ERROR"

            return var_name, response_content

        tasks = [run_one(item) for item in prompt_register]

        for var_name, value in await asyncio.gather(*tasks):
            results[var_name] = value

        return results
