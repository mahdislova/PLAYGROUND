from __future__ import annotations

import re

import anthropic


class LLM:
    def __init__(self, model: str = "claude-opus-5-5", effort: str = "high"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.effort = effort

    def complete(self, system: str, user: str) -> str:
        with self.client.beta.messages.stream(
            model=self.model,
            max_tokens=64000,
            system=system,
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            # On a policy decline, the API reroutes to a suitable model in the same call.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": user}],
        ) as stream:
            msg = stream.get_final_message()
        if msg.stop_reason == "refusal":
            raise RuntimeError(f"model declined this passage: {msg.stop_details}")
        if msg.stop_reason == "max_tokens":
            raise RuntimeError("output hit max_tokens; use a smaller --chunk-words")
        return "".join(b.text for b in msg.content if b.type == "text")


def extract_prose(reply: str) -> str:
    m = re.search(r"<prose>\s*(.*?)\s*</prose>", reply, re.S)
    return (m.group(1) if m else reply).strip()
