import json
import re
from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage, SystemMessage

if TYPE_CHECKING:
    from .skill_registry import SkillRegistry


_SELECTION_SYSTEM = """You are a marine genomics skill router.
Given a user query, select the most relevant skills from the provided list.
Return ONLY a JSON array of exact skill names.
Select between 1 and 3 skills."""


def retrieve_skills(query: str, registry: "SkillRegistry", llm, k: int = 3) -> list[dict]:
    summaries = registry.get_all_summaries()
    if not summaries:
        return []
    candidates = "\n".join(
        [f'- "{s["name"]}" ({s["category"]}): {s["short_description"]}' for s in summaries]
    )
    prompt = (
        f"User query:\n{query}\n\nAvailable skills:\n{candidates}\n\n"
        "Return ONLY a JSON array of selected skill names."
    )
    try:
        resp = llm.invoke([SystemMessage(content=_SELECTION_SYSTEM), HumanMessage(content=prompt)])
        text = resp.content if hasattr(resp, "content") else str(resp)
        m = re.search(r"\[.*?\]", text, re.DOTALL)
        arr = json.loads(m.group()) if m else []
        valid = [str(x) for x in arr if registry.get_skill(str(x))]
        if valid:
            return registry.get_skills_by_names(valid[:k])
    except Exception:
        pass

    q_tokens = set(re.findall(r"\w+", query.lower()))
    scored: list[tuple[int, str]] = []
    for s in summaries:
        t = f'{s["name"]} {s["category"]} {s["short_description"]}'.lower()
        score = len(q_tokens & set(re.findall(r"\w+", t)))
        scored.append((score, s["name"]))
    scored.sort(key=lambda x: x[0], reverse=True)
    names = [n for _, n in scored[:k] if scored and scored[0][0] > 0]
    if not names and scored:
        names = [scored[0][1]]
    return registry.get_skills_by_names(names)
