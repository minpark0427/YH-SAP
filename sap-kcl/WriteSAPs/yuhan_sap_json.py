"""
Runner script for generating a Yuhan SAP using JSON-structured output (B안).

Uses python-docx direct rendering instead of docxtpl for proper formatting.

Usage:
    python -m WriteSAPs.yuhan_sap_json <protocol_pdf_path> [--test] [--model MODEL]
"""

import argparse
import asyncio
import time
from pathlib import Path
from datetime import date
from importlib.resources import files

from auto_sap.classes.protocol_classes import Protocol
from auto_sap.classes.protocol_segmenter import ProtocolSegmenter
from auto_sap.classes.context_assembler import ContextAssembler
from auto_sap.classes.multi_step_generator import MultiStepGenerator, HIGH_COMPLEXITY_TAGS
from auto_sap.classes.chat_classes import ClaudeCodeChatAsync
from auto_sap.classes.json_renderer import JsonSapRenderer
from auto_sap.section_mapping import SAP_TO_PROTOCOL_MAP, GLOBAL_CONTEXT_SECTIONS
from auto_sap.generate_templates.generate_yuhan_template import prompt_tasks
from auto_sap.prompts.prompts_yuhan_v1 import PROMPTS_DICTIONARY


def json_system_message(context: str) -> str:
    """System message that requests JSON-structured output."""
    return (
        "You are an expert biostatistician specialising in pharmaceutical clinical trials. "
        "You are given a clinical trial protocol and will be asked to write sections for "
        "a Statistical Analysis Plan (SAP) following Yuhan Corporation's standard template.\n\n"
        "Rules:\n"
        "- Only include content appropriate for the specific SAP section requested.\n"
        "- Do not invent information not present in the protocol.\n"
        "- Follow ICH E9(R1) estimand framework where applicable.\n"
        "- Write in English unless instructed otherwise.\n"
        "- Use terminology consistent with CDISC standards (SDTM/ADaM) where appropriate.\n\n"
        "OUTPUT FORMAT — You MUST respond with valid JSON only:\n"
        '{\n'
        '  "paragraphs": [\n'
        '    {"text": "First paragraph of content...", "style": "body"},\n'
        '    {"text": "Second paragraph...", "style": "body"},\n'
        '    {"text": "A bullet point item", "style": "bullet"},\n'
        '    {"text": "A bold label or sub-heading", "style": "bold"}\n'
        '  ]\n'
        '}\n\n'
        "Style options: body (normal paragraph), bullet (list item), bold (emphasized paragraph).\n"
        "Do NOT use markdown. Do NOT include section titles/numbers. Content only.\n"
        "Do NOT wrap in ```json``` code fences. Return raw JSON.\n\n"
        f"The protocol is:\n\n{context}"
    )


async def generate_sap_json(protocol_text: str, model: str) -> dict[str, str]:
    """Generate all SAP sections with JSON-structured output."""
    segmenter = ProtocolSegmenter(protocol_text)
    assembler = ContextAssembler(
        segmenter, SAP_TO_PROTOCOL_MAP, GLOBAL_CONTEXT_SECTIONS, protocol_text
    )
    context_map = assembler.assemble_all()
    multi_step = MultiStepGenerator()

    results = {}

    async def run_one(item):
        var_name = item.variable
        prompt = PROMPTS_DICTIONARY.get(var_name, "")
        if not prompt:
            return var_name, '{"paragraphs": [{"text": "ERROR: no prompt", "style": "body"}]}'

        tag_context = context_map.get(var_name, protocol_text)
        tag_sys_msg = json_system_message(tag_context)

        try:
            if var_name in HIGH_COMPLEXITY_TAGS:
                # For high-complexity, use multi-step but with JSON system message
                response_content = await multi_step.generate(
                    tag=var_name,
                    context=tag_context,
                    sap_prompt=prompt + "\n\nRemember: respond with JSON format as specified in the system message.",
                    system_message_fn=json_system_message,
                    chat_class=ClaudeCodeChatAsync,
                    model=model,
                    reasoning_effort=item.reasoning_effort,
                    verbosity=item.verbosity,
                )
            else:
                bot = ClaudeCodeChatAsync(model_name=model, system_message=tag_sys_msg)
                json_prompt = prompt + "\n\nRemember: respond with JSON format as specified in the system message."
                response = await bot.get_response(
                    prompt=json_prompt,
                    reasoning_effort=item.reasoning_effort,
                    verbosity=item.verbosity,
                )
                response_content = (response.get("content", "") or "").strip() or "ERROR"
        except Exception as e:
            print(f"Error for {var_name}: {e}")
            response_content = "ERROR"

        print(f"  {var_name}: {len(response_content)} chars")
        return var_name, response_content

    print(f"Running {len(prompt_tasks)} prompts (JSON mode)...")
    tasks = [run_one(item) for item in prompt_tasks]
    for var_name, value in await asyncio.gather(*tasks):
        results[var_name] = value

    return results


def main():
    parser = argparse.ArgumentParser(description="Generate Yuhan SAP with JSON output (B안)")
    parser.add_argument("protocol", type=str, help="Path to protocol file")
    parser.add_argument("--output-dir", type=str, default="SAPs_v4_json", help="Output directory")
    parser.add_argument("--test", action="store_true", help="Use haiku for testing")
    parser.add_argument("--model", type=str, default=None, help="Override model name")
    args = parser.parse_args()

    protocol_path = Path(args.protocol)
    if not protocol_path.exists():
        raise FileNotFoundError(f"Protocol not found: {protocol_path}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.model:
        model = args.model
    elif args.test:
        model = "claude-haiku-4-5-20251001"
        print(f"Test mode: using {model}")
    else:
        model = "claude-opus-4-6"
        print(f"Production mode: using {model}")

    t0 = time.time()

    protocol = Protocol(str(protocol_path))
    sap_content = asyncio.run(generate_sap_json(protocol.protocol_txt, model))

    # Save raw content
    sap_name = f"YH_SAP_{protocol_path.stem}"
    content_path = output_dir / f"{sap_name}_content.txt"
    with open(content_path, "w") as f:
        for key, value in sap_content.items():
            f.write(f"{key}: {value}\n")
    print(f"Raw content saved to {content_path}")

    # Render docx with JsonSapRenderer
    template_path = files("auto_sap").joinpath("templates/yuhan_sap_template_v1.0.docx")
    renderer = JsonSapRenderer(template_path)
    docx_path = output_dir / f"{sap_name}.docx"
    renderer.render(sap_content, docx_path)

    t1 = time.time()
    print(f"SAP written in {round(t1 - t0)} seconds")
    print(f"Done. Output in {output_dir}/")


if __name__ == "__main__":
    main()
