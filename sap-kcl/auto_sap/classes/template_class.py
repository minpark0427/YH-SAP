import re
from pathlib import Path
from tempfile import template
from docxtpl import DocxTemplate
from auto_sap.classes.chat_classes import (
    OpenAIChat, OpenAIChatAsync,
    AnthropicChat, AnthropicChatAsync,
    ClaudeCodeChat, ClaudeCodeChatAsync,
)
from auto_sap.classes.protocol_classes import Protocol
from auto_sap.classes.protocol_segmenter import ProtocolSegmenter
from auto_sap.classes.context_assembler import ContextAssembler
from auto_sap.classes.multi_step_generator import MultiStepGenerator, HIGH_COMPLEXITY_TAGS
from auto_sap.classes.auto_code_classes import AutoCodePipeline
from auto_sap.section_mapping import SAP_TO_PROTOCOL_MAP, GLOBAL_CONTEXT_SECTIONS
import asyncio
from datetime import date
import time


def _strip_markdown(text: str) -> str:
    """Remove markdown formatting from LLM output for clean docx rendering."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'^[-*]\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


class Template:
    def __init__(
        self,
        template_path: str | Path,
        system_message_function,
        prompt_register,
        prompts_dictionary,
        template_name,
        prompts_name,
        backend: str = "claudecode",
    ) -> None:

        self.template_path = template_path
        self.system_message_function = system_message_function
        self.prompt_register = prompt_register
        self.prompts_dictionary = prompts_dictionary
        self.template_name = template_name
        self.prompts_name = prompts_name
        self.backend = backend

    def _get_async_chat_class(self, backend):
        """Return the appropriate async chat class for the given backend."""
        if backend == "claudecode":
            return ClaudeCodeChatAsync
        elif backend == "anthropic" or (backend == "auto" and backend and backend.startswith("claude-")):
            return AnthropicChatAsync
        else:
            return OpenAIChatAsync

    async def get_sap_content_async(self, protocol_text, model="claude-sonnet-4-5-20250929", backend=None):
        backend = backend or self.backend

        segmenter = ProtocolSegmenter(protocol_text)
        assembler = ContextAssembler(
            segmenter, SAP_TO_PROTOCOL_MAP, GLOBAL_CONTEXT_SECTIONS, protocol_text
        )
        context_map = assembler.assemble_all()
        multi_step = MultiStepGenerator()
        chat_class = self._get_async_chat_class(backend)

        print(f"Running {len(self.prompt_register)} prompts with targeted context...")
        results = {}

        async def run_one(item):
            var_name = item.variable
            prompt = self.prompts_dictionary.get(var_name, "")

            print(f"Running {var_name}")
            if not prompt:
                print(f"No prompt in prompt dictionary for {var_name}")
                return var_name, "ERROR: tag not in prompt dictionary"

            tag_context = context_map.get(var_name, protocol_text)
            tag_sys_msg = self.system_message_function(tag_context)

            try:
                if var_name in HIGH_COMPLEXITY_TAGS:
                    response_content = await multi_step.generate(
                        tag=var_name,
                        context=tag_context,
                        sap_prompt=prompt,
                        system_message_fn=self.system_message_function,
                        chat_class=chat_class,
                        model=model,
                        reasoning_effort=item.reasoning_effort,
                        verbosity=item.verbosity,
                    )
                else:
                    bot = chat_class(model_name=model, system_message=tag_sys_msg)
                    response = await bot.get_response(
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

        tasks = [run_one(item) for item in self.prompt_register]
        for var_name, value in await asyncio.gather(*tasks):
            results[var_name] = _strip_markdown(value) if value != "ERROR" else value

        self.sap_content = results

        today = date.today()
        str_today = today.strftime("%d/%m/%y")
        self.sap_content.update({"todays_date": str_today})
        self.sap_content.update(
            {"template_prompt_version": f"{self.template_name} with prompts {self.prompts_name}"}
        )

    def get_sap_content(self, protocol_text, model="claude-sonnet-4-5-20250929", backend=None):
        asyncio.run(self.get_sap_content_async(protocol_text, model, backend))

    def save_content_as_text(self, path):
        sap_content = self.sap_content
        with open(path, "w", encoding="utf-8") as f:
            for key, value in sap_content.items():
                f.write(f"{key}: {value}\n")
        print(f"raw SAP content saved to {path}")

    def populate(self, sap_folder, sap_name='SAP.docx'):
        if getattr(self, "sap_content", None) is not None:
            sap_content = self.sap_content
            template = DocxTemplate(self.template_path)
            template.render(sap_content)
            output_path = Path(sap_folder) / sap_name
            template.save(output_path)
            print(f"SAP saved to {output_path}")
        else:
            raise ValueError("sap_content must be set before populating template.")

    def write_sap(self, protocol_path, sap_name, sap_folder_path="SAPs", test=False):
        t0 = time.time()

        protocol = Protocol(protocol_path)
        if not test:
            self.get_sap_content(protocol.protocol_txt)
        else:
            print("Test enabled - running with claude-haiku-4-5-20251001")
            self.get_sap_content(protocol.protocol_txt, model="claude-haiku-4-5-20251001")

        self.save_content_as_text(path=f"{sap_folder_path}/{sap_name}_content.txt")
        self.populate(sap_folder=sap_folder_path, sap_name=f"{sap_name}.docx")

        t1 = time.time()
        total_time = round(t1 - t0)
        print(f"SAP written in {total_time} seconds")

    def get_autocode_json(self, output_path=None, model="claude-sonnet-4-5-20250929", backend=None):
        backend = backend or self.backend
        if getattr(self, "sap_content", None) is not None:
            if backend == "claudecode":
                chat_bot = ClaudeCodeChat(model_name=model, system_message="")
            elif backend == "anthropic" or (backend == "auto" and model.startswith("claude-")):
                chat_bot = AnthropicChat(model_name=model, system_message="")
            else:
                chat_bot = OpenAIChat(model_name=model, system_message="")
            pipeline = AutoCodePipeline(chat_bot)

            content_for_autocode = {
                "timepoint_content": self.sap_content.get("primary_outcome_measures", "") + "\n" + self.sap_content.get("secondary_outcome_measures", ""),
                "variables_content": self.sap_content.get("primary_outcome_measures", "") + "\n" + self.sap_content.get("secondary_outcome_measures", ""),
                "analysis_content": self.sap_content.get("primary_analysis_model", "") + "\n" + self.sap_content.get("secondary_analysis", "")
            }

            result = pipeline.extract_all(content_for_autocode)
            if output_path:
                pipeline.save_to_json(result, output_path)
            return result
        else:
            raise ValueError("sap_content must be set before creating autocode json.")
