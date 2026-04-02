# Classes/interactive_autocode_conversation.py

import copy
import json
import textwrap
from typing import Any, Callable, Dict, Optional

class AdvancedAutoCodeConversation:
    """
    Dual-mode wrapper around an AutoCodeConversation-like object.

    Modes:
      - chat: advice/explanations, no JSON changes
      - edit: applies edits via base_convo.chat(...), then explains changes

    Requirements for base_convo:
      - has .result (dict-like) and .chat(user_msg: str) -> Any
      - .result should be assignable for undo (base_convo.result = state)
    """

    def __init__(
        self,
        base_convo: Any,
        llm_chat_fn: Callable[[list, str], str],
        protocol_txt: Optional[str] = None,
        verbose: bool = True,
    ):
        self.base_convo = base_convo
        self.llm_chat_fn = llm_chat_fn
        self.protocol_txt = protocol_txt
        self.verbose = verbose

        if self.verbose:
            print("🧩 Initialising AdvancedAutoCodeConversation wrapper...")

        self._history = [copy.deepcopy(self.base_convo.result)]
        self._history_idx = 0

        if self.verbose:
            print("✅ Wrapper ready. JSON snapshot stored.")

    @property
    def result(self) -> Dict[str, Any]:
        return self.base_convo.result

    # ---------- History ----------
    def _snapshot(self):
        if self._history_idx < len(self._history) - 1:
            self._history = self._history[: self._history_idx + 1]
        self._history.append(copy.deepcopy(self.base_convo.result))
        self._history_idx += 1
        if self.verbose:
            print("💾 Snapshot saved (for undo/redo).")

    def undo(self) -> bool:
        if self._history_idx == 0:
            return False
        self._history_idx -= 1
        state = copy.deepcopy(self._history[self._history_idx])
        self.base_convo.result = state
        if self.verbose:
            print("↩️  Undo applied. Reverted to previous JSON state.")
        return True

    def redo(self) -> bool:
        if self._history_idx >= len(self._history) - 1:
            return False
        self._history_idx += 1
        state = copy.deepcopy(self._history[self._history_idx])
        self.base_convo.result = state
        if self.verbose:
            print("↪️  Redo applied. Moved forward to next JSON state.")
        return True

    # ---------- Intent classification ----------
    def _classify_intent(self, message: str) -> str:
        msg = message.lower()

        edit_keywords = [
            "add ", "remove ", "delete ", "drop ",
            "rename ", "change ", "update ", "fix ",
            "split ", "merge ", "modify ", "correct ",
            "take out", "leave out", "exclude", "include",
        ]
        if any(kw in msg for kw in edit_keywords):
            return "edit"

        chat_keywords = [
            "what do you think",
            "what would you suggest",
            "does this make sense",
            "is this ok",
            "is this correct",
            "how would you",
            "could we",
        ]
        if any(kw in msg for kw in chat_keywords):
            return "chat"

        return "chat"

    def _truncate_json(self, result: Dict[str, Any], max_chars: int = 3000) -> str:
        try:
            j = json.dumps(result, indent=2)
        except TypeError:
            return str(result)
        if len(j) > max_chars:
            return j[:max_chars] + "\n\n... [truncated]"
        return j

    # ---------- Main chat interface ----------
    def chat(self, user_message: str, model: str = "gpt-4.1-mini") -> Dict[str, Any]:
        intent = self._classify_intent(user_message)

        if intent == "edit":
            if self.verbose:
                print("\n🛠  Interpreting your message as an EDIT instruction.")
                print("   ⏳ Applying edit to JSON via AutoCodeConversation...")

            self.base_convo.chat(user_message)
            self._snapshot()

            json_str = self._truncate_json(self.result)

            system = (
                "You are an assistant helping to edit a structured JSON spec "
                "for a clinical trial SAP. The user just gave an edit instruction. "
                "You have already applied this edit to the JSON. "
                "Explain briefly what you changed and why, then show the updated "
                "JSON snippet if helpful, but do NOT invent new changes."
            )

            prompt = textwrap.dedent(f"""
            USER EDIT INSTRUCTION:
            {user_message}

            UPDATED JSON (after applying the edit):
            {json_str}
            """)

            if self.verbose:
                print("   🤖 Asking LLM to summarise the changes...")

            reply = self.llm_chat_fn(
                [{"role": "system", "content": system},
                 {"role": "user", "content": prompt}],
                model,
            )

            if self.verbose:
                print("   ✅ Edit explanation received.\n")

            return {"mode": "edit", "message": reply, "json": self.result}

        # chat mode
        if self.verbose:
            print("\n💬 Interpreting your message as a DISCUSSION / QUESTION (no JSON change).")

        json_str = self._truncate_json(self.result)
        prot_snip = self.protocol_txt[:2000] if self.protocol_txt else ""

        system = (
            "You are a senior clinical trial statistician and methods expert. "
            "You are helping the user reason about a trial SAP and a structured "
            "JSON representation of timepoints, variables, and analyses. "
            "Answer conceptually and practically. DO NOT modify the JSON; "
            "just discuss, critique, or suggest changes in words."
        )

        parts = [
            "User question:",
            user_message,
            "\n\nCurrent JSON representation:",
            json_str,
        ]
        if prot_snip:
            parts.append("\n\nOriginal protocol excerpt:")
            parts.append(prot_snip)

        if self.verbose:
            print("   ⏳ Asking LLM for advice / explanation...")

        reply = self.llm_chat_fn(
            [{"role": "system", "content": system},
             {"role": "user", "content": "\n".join(parts)}],
            model,
        )

        if self.verbose:
            print("   ✅ Response received.\n")

        return {"mode": "chat", "message": reply, "json": self.result}
