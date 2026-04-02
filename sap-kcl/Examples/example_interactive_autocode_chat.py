# example_interactive_autocode_chat.py

import argparse
import json
import os

from openai import OpenAI
from docx import Document
from pypdf import PdfReader

from auto_sap.generate_templates.generate_simple_template import (
    get_autocode_conversation_for_protocol,
)
from auto_sap.classes.interactive_autocode_conversation import (
    AdvancedAutoCodeConversation,
)

# ---------------------------------------------------------
# OpenAI client
# ---------------------------------------------------------
client = OpenAI()


def llm_chat_fn(messages, model="gpt-5"):
    """
    Thin wrapper around OpenAI Chat Completions.

    Parameters
    ----------
    messages : list[dict]
        OpenAI-style messages: [{"role": "...", "content": "..."}]
    model : str
        Defaults to GPT-5.

    Returns
    -------
    str
        Assistant message content.
    """
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return resp.choices[0].message.content


# ---------------------------------------------------------
# Protocol loading utilities
# ---------------------------------------------------------
def load_protocol_text(path: str) -> str:
    """
    Load protocol text from .txt, .docx, or .pdf.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if ext == ".docx":
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    if ext == ".pdf":
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    raise ValueError(
        f"Unsupported file type: {ext}. "
        "Supported types are .txt, .docx, .pdf"
    )


def pretty_print_result(result, max_chars=2000):
    try:
        j = json.dumps(result, indent=2)
    except TypeError:
        print(result)
        return
    if len(j) <= max_chars:
        print(j)
    else:
        print(j[:max_chars])
        print("\n... [truncated]")


# ---------------------------------------------------------
# Main CLI entrypoint
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Interactive AutoCode JSON chat (GPT-5 powered)"
    )
    parser.add_argument(
        "--protocol",
        required=True,
        help="Path to protocol file (.txt, .docx, .pdf)",
    )
    parser.add_argument(
        "--out",
        default="autocode_result.json",
        help="Output JSON filename",
    )
    parser.add_argument(
        "--model",
        default="gpt-5",
        help="OpenAI model for chat/explanations (default: gpt-5)",
    )
    args = parser.parse_args()

    # ---- Load protocol ----
    print(f"📄 Loading protocol: {args.protocol}")
    protocol_txt = load_protocol_text(args.protocol)
    print("✅ Protocol loaded.")

    print("\nPreview (first 600 characters):\n")
    print(protocol_txt[:600])
    print("\n--- END PREVIEW ---\n")

    # ---- Run existing AutoCode extraction pipeline ----
    print("⚙️ Running auto-code extraction pipeline...")
    base_convo = get_autocode_conversation_for_protocol(protocol_txt)
    print("✅ Extraction complete.\n")

    # ---- Wrap with interactive dual-mode conversation ----
    print("🧠 Initialising interactive AutoCode conversation (GPT-5)...")
    adv = AdvancedAutoCodeConversation(
        base_convo=base_convo,
        llm_chat_fn=llm_chat_fn,
        protocol_txt=protocol_txt,
        verbose=True,
    )

    print("\n📊 Initial JSON (truncated):")
    pretty_print_result(adv.result)

    print(
        "\n💬 Interactive SAP / AutoCode chat\n"
        "Commands:\n"
        "  - Natural questions → chat mode\n"
        "  - Edit instructions → JSON edit mode\n"
        "  - undo / redo\n"
        "  - done (save & exit)\n"
    )

    # ---- Interactive loop ----
    while True:
        user_msg = input("You: ").strip()

        if user_msg.lower() == "undo":
            ok = adv.undo()
            print("✅ Undone." if ok else "⚠️ Nothing to undo.")
            continue

        if user_msg.lower() == "redo":
            ok = adv.redo()
            print("✅ Redone." if ok else "⚠️ Nothing to redo.")
            continue

        if user_msg.lower() in {"done", "exit", "quit"}:
            print("\n🛑 Ending session. Saving final JSON...")
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(adv.result, f, indent=2)
            print(f"💾 Saved to: {args.out}")
            break

        print("🧮 Processing with GPT-5...")
        resp = adv.chat(user_msg, model=args.model)

        print(f"\n[mode: {resp['mode']}] Assistant:\n")
        print(resp["message"])
        print("\n📊 Current JSON (truncated):")
        pretty_print_result(resp["json"])
        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()
