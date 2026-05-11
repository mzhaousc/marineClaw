from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="marine_agent",
        description="marineClaw marine genomics AI agent",
    )
    p.add_argument("query", nargs="?", help="Marine genomics task")
    p.add_argument("-w", "--web", action="store_true", help="Launch web UI")
    p.add_argument("-i", "--interactive", action="store_true", help="Interactive terminal")
    p.add_argument("--list-skills", action="store_true", help="List all skills and exit")
    p.add_argument("--source", help="LLM source: OpenAI|Anthropic|Groq|Gemini|Ollama|Custom")
    p.add_argument("--model", help="Model name")
    p.add_argument("--skills-dir", help="Override skills directory")
    p.add_argument("--workdir", help="Working directory")
    p.add_argument("--host", default="127.0.0.1", help="Web UI bind address (use 0.0.0.0 on HPC + SSH tunnel)")
    p.add_argument("--port", type=int, default=7860, help="Web port")
    p.add_argument("--share", action="store_true", help="Enable Gradio share link")
    p.add_argument("-q", "--quiet", action="store_true", help="Less logging")
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    from .agent import MarineAgent
    from .config import MarineAgentConfig

    cfg = MarineAgentConfig(
        llm_source=args.source or None,
        llm_model=args.model or None,
        skills_dir=args.skills_dir or None,
        working_dir=args.workdir or None,
    )
    agent = MarineAgent(config=cfg, verbose=not args.quiet)

    if args.list_skills:
        for s in agent.list_skills():
            print(f"[{s['category']}] {s['display_name']}: {s['short_description']}")
        return
    if args.web:
        print(f"Launching marineClaw at http://{args.host}:{args.port}")
        agent.launch_web_ui(host=args.host, port=args.port, share=args.share)
        return
    if args.interactive:
        print("marineClaw interactive mode. type exit to quit.")
        while True:
            try:
                q = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if not q:
                continue
            if q.lower() in {"exit", "quit", "q"}:
                print("Goodbye!")
                break
            print("\nAgent:\n" + agent.go(q) + "\n")
        return
    if args.query:
        print(agent.go(args.query))
        return

    _build_parser().print_help()
    sys.exit(1)
