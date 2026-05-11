from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

for p in [Path(__file__).parent.parent / ".env", Path.cwd() / ".env"]:
    if p.exists():
        load_dotenv(p)
        break
else:
    load_dotenv()

_DEFAULTS = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20241022",
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.0-flash",
    "ollama": "llama3.1",
    "custom": "local-model",
}


class MarineAgentConfig:
    def __init__(
        self,
        llm_source: str | None = None,
        llm_model: str | None = None,
        skills_dir: str | None = None,
        timeout_seconds: int | None = None,
        max_iterations: int | None = None,
        working_dir: str | None = None,
    ):
        self.llm_source = llm_source or os.getenv("LLM_SOURCE", "OpenAI")
        self.llm_model = llm_model or os.getenv("MARINE_AGENT_MODEL", _DEFAULTS.get(self.llm_source.lower(), "gpt-4o"))

        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.custom_base_url = os.getenv("CUSTOM_MODEL_BASE_URL", "")
        self.custom_api_key = os.getenv("CUSTOM_MODEL_API_KEY", "sk-empty")

        self.skills_dir = skills_dir or os.getenv("MARINE_AGENT_SKILLS_DIR", str(Path(__file__).parent.parent / "skills"))
        self.timeout_seconds = timeout_seconds or int(os.getenv("MARINE_AGENT_TIMEOUT", "300"))
        self.max_iterations = max_iterations or int(os.getenv("MARINE_AGENT_MAX_ITER", "20"))
        self.working_dir = working_dir or os.getenv("MARINE_AGENT_WORKDIR", str(Path(__file__).parent.parent / "work"))
        # HPC: NCBI BLAST+ uses BLASTDB for -db name resolution; optional default thread count for generated commands
        self.blast_db = (os.getenv("BLASTDB", "") or "").strip()
        _t = (os.getenv("MARINE_AGENT_BLAST_NUM_THREADS", "") or "").strip()
        self.blast_num_threads: int | None = int(_t) if _t.isdigit() and int(_t) > 0 else None

    def build_llm(self, temperature: float = 0.0):
        src = self.llm_source.lower()
        if src == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=self.llm_model, temperature=temperature, api_key=self.openai_api_key or None)
        if src == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=self.llm_model, temperature=temperature, api_key=self.anthropic_api_key or None)
        if src == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(model=self.llm_model, temperature=temperature, api_key=self.groq_api_key or None)
        if src == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=self.llm_model, temperature=temperature, google_api_key=self.gemini_api_key or None)
        if src == "ollama":
            from langchain_ollama import ChatOllama
            return ChatOllama(model=self.llm_model, temperature=temperature, base_url=self.ollama_base_url)
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=self.llm_model, temperature=temperature, base_url=self.custom_base_url, api_key=self.custom_api_key)


default_config = MarineAgentConfig()
