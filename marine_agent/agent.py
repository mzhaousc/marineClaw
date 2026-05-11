from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from .executor import detect_language, execute_code
from .galaxy_route import is_galaxy_query, run_galaxy_route
from .skill_registry import SkillRegistry
from .skill_retriever import retrieve_skills

if TYPE_CHECKING:
    from .config import MarineAgentConfig


_SYSTEM_CORE = """\
You are a marine genomics AI assistant for sequence-based analysis.

## CRITICAL BEHAVIOR RULES
1. Act immediately. Do not ask clarification questions.
2. Make reasonable assumptions and validate by inspecting files.
3. Prefer Bash for BLAST+/MAFFT/HMMER/IQ-TREE/antiSMASH commands.
4. Each reply must contain either <execute>...</execute> or <solution>...</solution>.

## MARINE BLAST DECISION RULES
- phylogenetic: evalue=1e-5, max_hits~500, prioritize taxonomic diversity
- functional annotation: evalue=1e-5, prefer curated DB (SwissProt), identity >40%
- structure template: evalue=1e-10, prefer PDB, coverage >70%
- hgt scan: evalue=1e-10, max_hits>=50, avoid strict taxonomy filters
- ortholog detection: use reciprocal BLAST strategy

## KEY DATABASE FAMILIES
- NCBI: nr, nt, swissprot, pdb
- marine-focused: SILVA, MarRef, MMETSP
- domain models: Pfam-A.hmm
- natural products: MIBiG
- If `BLASTDB` is set in the environment, local `makeblastdb` builds and `blast*` `-db` names resolve there without absolute paths.

{skill_section}
"""

_SKILL_SECTION = """\
## Loaded Skills
{entries}
"""

_SKILL_ENTRY = """\
### {display_name} [{category}]
Skill dir: `{skill_dir}`
{scripts_line}
{body}
---
"""


class AgentState(TypedDict):
    messages: list[BaseMessage]
    next_step: str
    iterations: int


class MarineAgent:
    def __init__(
        self,
        config: "MarineAgentConfig | None" = None,
        skills_dir: str | None = None,
        llm=None,
        verbose: bool = True,
    ):
        from .config import default_config

        self.config = config or default_config
        if skills_dir:
            self.config.skills_dir = skills_dir
        self.verbose = verbose
        self.llm = llm or self.config.build_llm()
        self.registry = SkillRegistry(self.config.skills_dir)
        os.makedirs(self.config.working_dir, exist_ok=True)

    def _build_system_prompt(self, selected_skills: list[dict]) -> str:
        if not selected_skills:
            section = "No specific marine skills selected."
        else:
            entries = []
            for s in selected_skills:
                scripts_line = ""
                if s.get("scripts_list"):
                    scripts_line = f"Scripts: {', '.join([f'`{x}`' for x in s['scripts_list']])} (in `{s['scripts_dir']}`)"
                entries.append(
                    _SKILL_ENTRY.format(
                        display_name=s["display_name"],
                        category=s["category"],
                        skill_dir=s["skill_dir"],
                        scripts_line=scripts_line,
                        body=s["body"],
                    )
                )
            section = _SKILL_SECTION.format(entries="\n\n".join(entries))
        base = _SYSTEM_CORE.format(skill_section=section)
        return base + self._hpc_execution_hints()

    def _hpc_execution_hints(self) -> str:
        """Inject BLAST/HPC hints from env so generated Bash matches the cluster (skipped on plain laptops)."""
        cfg = self.config
        hpc_mode = os.getenv("MARINE_AGENT_HPC_MODE", "").lower() in ("1", "true", "yes")
        if not hpc_mode and not cfg.blast_db and cfg.blast_num_threads is None:
            return ""
        parts: list[str] = []
        if cfg.blast_db:
            parts.append(
                f"- **BLASTDB** is `{cfg.blast_db}`. Use `blastp -db nr ...` (short name) when DB volumes live there."
            )
        if cfg.blast_num_threads is not None:
            parts.append(
                f"- Prefer **`-num_threads {cfg.blast_num_threads}`** on BLAST+ unless the user overrides."
            )
        else:
            parts.append(
                "- On **Slurm/PBS**, use `-num_threads ${SLURM_CPUS_PER_TASK:-4}` (or `${NCPUS:-4}`) in Bash."
            )
        parts.append(
            f"- **Agent working directory**: `{cfg.working_dir}` — point `MARINE_AGENT_WORKDIR` at scratch for large I/O."
        )
        return "\n## HPC EXECUTION (from configuration)\n" + "\n".join(parts) + "\n"

    def _build_graph(self, system_prompt: str, namespace: dict):
        llm = self.llm
        cfg = self.config

        def generate(state: AgentState) -> AgentState:
            if state["iterations"] >= cfg.max_iterations:
                return {
                    "messages": state["messages"] + [AIMessage(content="<solution>Stopped after reaching max iterations.</solution>")],
                    "next_step": "end",
                    "iterations": state["iterations"] + 1,
                }
            resp = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
            content = resp.content if hasattr(resp, "content") else str(resp)
            if "<solution>" in content:
                nxt = "end"
            elif "<execute>" in content:
                nxt = "execute"
            else:
                content = f"<solution>{content}</solution>"
                nxt = "end"
            return {
                "messages": state["messages"] + [AIMessage(content=content)],
                "next_step": nxt,
                "iterations": state["iterations"] + 1,
            }

        def execute(state: AgentState) -> AgentState:
            content = state["messages"][-1].content if state["messages"] else ""
            m = re.search(r"<execute>(.*?)</execute>", content, re.DOTALL)
            if not m:
                observation = "[Error] Missing <execute> block."
            else:
                code = m.group(1).strip()
                if self.verbose:
                    print(f"[Executing {detect_language(code)}]")
                observation = execute_code(code, namespace=namespace, working_dir=cfg.working_dir, timeout=cfg.timeout_seconds)
            return {
                "messages": state["messages"] + [HumanMessage(content=f"<observation>\n{observation}\n</observation>")],
                "next_step": "generate",
                "iterations": state["iterations"],
            }

        def route(state: AgentState) -> Literal["execute", "generate", "end"]:
            if state["next_step"] == "execute":
                return "execute"
            if state["next_step"] == "generate":
                return "generate"
            return "end"

        g = StateGraph(AgentState)
        g.add_node("generate", generate)
        g.add_node("execute", execute)
        g.add_conditional_edges("generate", route, {"execute": "execute", "generate": "generate", "end": END})
        g.add_edge("execute", "generate")
        g.add_edge(START, "generate")
        return g.compile()

    def _select_skills(self, query: str) -> list[dict]:
        skills = retrieve_skills(query, self.registry, self.llm, k=3)
        if self.verbose and skills:
            print("[Skills]", ", ".join([s["display_name"] for s in skills]))
        return skills

    def go(self, query: str) -> str:
        if is_galaxy_query(query):
            return run_galaxy_route(query=query, working_dir=self.config.working_dir)
        selected = self._select_skills(query)
        app = self._build_graph(self._build_system_prompt(selected), {})
        final_state = app.invoke(
            {"messages": [HumanMessage(content=query)], "next_step": "generate", "iterations": 0}
        )
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage):
                m = re.search(r"<solution>(.*?)</solution>", msg.content, re.DOTALL)
                return m.group(1).strip() if m else msg.content.strip()
        return ""

    def go_stream(self, query: str):
        if is_galaxy_query(query):
            yield {
                "generate": {
                    "messages": [
                        AIMessage(
                            content=(
                                "<solution>"
                                + run_galaxy_route(query=query, working_dir=self.config.working_dir)
                                + "</solution>"
                            )
                        )
                    ]
                }
            }
            return
        selected = self._select_skills(query)
        app = self._build_graph(self._build_system_prompt(selected), {})
        yield from app.stream(
            {"messages": [HumanMessage(content=query)], "next_step": "generate", "iterations": 0},
            stream_mode="updates",
        )

    def list_skills(self) -> list[dict]:
        return self.registry.get_all_summaries()

    def launch_web_ui(self, host: str = "127.0.0.1", port: int = 7860, share: bool = False, open_browser: bool = True) -> None:
        from .web_ui import launch

        launch(self, host=host, port=port, share=share, open_browser=open_browser)
