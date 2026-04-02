from pathlib import Path
from tempfile import template
from docxtpl import DocxTemplate
from auto_sap.classes.chat_classes import (
    OpenAIChat, OpenAIChatAsync,
    AnthropicChat, AnthropicChatAsync,
    ClaudeCodeChat, ClaudeCodeChatAsync,
)
from auto_sap.classes.protocol_classes import Protocol
from auto_sap.classes.auto_code_classes import AutoCodePipeline
import asyncio
from datetime import date
import time 



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
        self.system_message_function = system_message_function # a function of protocol text
        self.prompt_register = prompt_register
        self.prompts_dictionary = prompts_dictionary
        self.template_name = template_name
        self.prompts_name = prompts_name
        self.backend = backend

    
    async def get_sap_content_async(self, protocol_text, model="claude-sonnet-4-5-20250929", backend=None):
        backend = backend or self.backend
        sys_msg = self.system_message_function(protocol_text)

        if backend == "claudecode":
            chat_bot = ClaudeCodeChatAsync(model_name=model, system_message=sys_msg)
        elif backend == "anthropic" or (backend == "auto" and model.startswith("claude-")):
            chat_bot = AnthropicChatAsync(model_name=model, system_message=sys_msg)
        else:
            chat_bot = OpenAIChatAsync(model_name=model, system_message=sys_msg)
        
        self.sap_content = await chat_bot.run_prompts_register(
            prompt_register=self.prompt_register, 
            prompt_dictionary=self.prompts_dictionary
        )

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
            

    def populate(self, sap_folder, sap_name = 'SAP.docx'):
        if getattr(self, "sap_content", None) is not None:
            sap_content = self.sap_content
            template = DocxTemplate(self.template_path)
            template.render(sap_content)
            output_path = Path(sap_folder) / sap_name
            template.save(output_path)
            print(f"SAP saved to {output_path}")
        else:
             raise ValueError("sap_content must be set before populating template.")
        
    def write_sap(self, protocol_path, sap_name, sap_folder_path = "SAPs", test = False):
        t0 = time.time()

        protocol = Protocol(protocol_path)
        if not test:
            self.get_sap_content(protocol.protocol_txt)
        else:
            print("Test enabled - running with claude-haiku-4-5-20251001")
            self.get_sap_content(protocol.protocol_txt, model="claude-haiku-4-5-20251001")

        self.save_content_as_text(path = f"{sap_folder_path}/{sap_name}_content.txt")
        self.populate(sap_folder = sap_folder_path, sap_name = f"{sap_name}.docx")

        t1 = time.time()
        total_time = round(t1- t0)
        print(f"SAP written in {total_time} seconds")

    def get_autocode_json(self, output_path = None, model = "claude-sonnet-4-5-20250929", backend=None):
        backend = backend or self.backend
        if getattr(self, "sap_content", None) is not None:
            if backend == "claudecode":
                chat_bot = ClaudeCodeChat(model_name=model, system_message="")
            elif backend == "anthropic" or (backend == "auto" and model.startswith("claude-")):
                chat_bot = AnthropicChat(model_name=model, system_message="")
            else:
                chat_bot = OpenAIChat(model_name=model, system_message="")
            pipeline = AutoCodePipeline(chat_bot)
            
            # TODO: This may need to be adjusted based on how sap_content is structured for a specific tempalte
            # could let a set of strings be passed to the template class init specifying which sections of sap content to use.
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
