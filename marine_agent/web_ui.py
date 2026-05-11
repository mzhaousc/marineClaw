from __future__ import annotations

import os
import re
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from langchain_core.messages import HumanMessage

from .executor import detect_language
from .galaxy_route import is_galaxy_query, run_galaxy_route

_EXT = {"Python": ".py", "R": ".R", "Bash": ".sh"}
_FENCE = {"Python": "python", "R": "r", "Bash": "bash"}


def _format(content: str) -> str:
    em = re.search(r"<execute>(.*?)</execute>", content, re.DOTALL)
    if em:
        code = em.group(1).strip()
        lang = detect_language(code)
        code = re.sub(r"^#!(R|BASH)\s*\n?", "", code, flags=re.IGNORECASE)
        return f"```{_FENCE.get(lang, 'python')}\n{code}\n```"
    sm = re.search(r"<solution>(.*?)</solution>", content, re.DOTALL)
    if sm:
        return sm.group(1).strip()
    return content


def _observation(content: str) -> str:
    m = re.search(r"<observation>(.*?)</observation>", content, re.DOTALL)
    text = (m.group(1) if m else content).strip()
    if len(text) > 1800:
        text = text[:1800] + "\n\n... (truncated) ..."
    return f"**Observation**\n```\n{text}\n```"


def _skills_html(skills: list[dict], selected: list[str] | None = None) -> str:
    selected = selected or []
    out = ['<div style="max-height:520px;overflow:auto;font-family:sans-serif;">']
    by_cat: dict[str, list] = {}
    for s in skills:
        by_cat.setdefault(s["category"], []).append(s)
    for cat in sorted(by_cat):
        out.append(f'<div style="margin-top:8px;font-weight:bold;">{cat}</div>')
        for s in by_cat[cat]:
            sel = s["name"] in selected
            bg = "#e8f5e9" if sel else "transparent"
            out.append(
                f'<div style="padding:4px;border-radius:4px;background:{bg};" title="{s["short_description"]}">'
                f'{s["display_name"]}{" *" if sel else ""}</div>'
            )
    out.append("</div>")
    return "".join(out)


def _save_zip(scripts: list[dict], tmp_dir: str) -> str:
    path = os.path.join(tmp_dir, f"marineclaw_scripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for s in scripts:
            zf.writestr(s["filename"], s["code"])
    return path


def create_app(agent):
    import gradio as gr

    summaries = agent.registry.get_all_summaries()
    tmp_dir = tempfile.mkdtemp(prefix="marineclaw_")
    scripts_state_default: list[dict] = []

    with gr.Blocks(title="marineClaw") as demo:
        gr.Markdown("# marineClaw - Marine Genomics AI Agent")
        with gr.Row():
            skills_panel = gr.HTML(value=_skills_html(summaries))
            chat = gr.Chatbot(height=520, render_markdown=True, show_copy_button=True)
        msg = gr.Textbox(lines=2, placeholder="e.g. BLAST this FASTA against nr and build a phylogenetic tree")
        with gr.Row():
            run_btn = gr.Button("Run", variant="primary")
            clear_btn = gr.Button("Clear")
        script_selector = gr.Dropdown(choices=[], label="Generated scripts")
        script_preview = gr.Code(label="Script preview", language="python")
        dl_one = gr.DownloadButton("Download selected", visible=False)
        dl_all = gr.DownloadButton("Download all zip", visible=False)
        scripts_state = gr.State(scripts_state_default)

        def respond(message, history, scripts):
            scripts = scripts or []
            if is_galaxy_query(message):
                result = run_galaxy_route(message, agent.config.working_dir)
                history = history + [[message, result]]
                yield history, _skills_html(summaries), gr.update(choices=[s["filename"] for s in scripts]), gr.update(visible=bool(scripts)), gr.update(visible=bool(scripts)), "", scripts
                return
            selected = agent._select_skills(message)
            selected_names = [s["name"] for s in selected]
            status = f"Selected skills: {', '.join([s['display_name'] for s in selected])}"
            history = history + [[message, status]]
            yield history, _skills_html(summaries, selected_names), gr.update(choices=[s["filename"] for s in scripts]), gr.update(visible=bool(scripts)), gr.update(visible=bool(scripts)), "", scripts

            app = agent._build_graph(agent._build_system_prompt(selected), {})
            first = True
            for update in app.stream(
                {"messages": [HumanMessage(content=message)], "next_step": "generate", "iterations": 0},
                stream_mode="updates",
            ):
                for node_name, state in update.items():
                    msgs = state.get("messages", [])
                    if not msgs:
                        continue
                    c = msgs[-1].content if hasattr(msgs[-1], "content") else str(msgs[-1])
                    if node_name == "generate":
                        disp = _format(c)
                        if first:
                            history[-1][1] = status + "\n\n" + disp
                            first = False
                        else:
                            history.append([None, disp])
                        em = re.search(r"<execute>(.*?)</execute>", c, re.DOTALL)
                        if em:
                            raw = em.group(1).strip()
                            lang = detect_language(raw)
                            code = re.sub(r"^#!(R|BASH)\s*\n?", "", raw, flags=re.IGNORECASE)
                            scripts.append(
                                {
                                    "filename": f"script_{len(scripts)+1:02d}{_EXT.get(lang, '.txt')}",
                                    "language": lang,
                                    "code": code,
                                }
                            )
                    elif node_name == "execute":
                        history.append([None, _observation(c)])
                    names = [s["filename"] for s in scripts]
                    yield history, _skills_html(summaries, selected_names), gr.update(choices=names), gr.update(visible=bool(names)), gr.update(visible=bool(names)), "", scripts

        def preview_script(name, scripts):
            if not name or not scripts:
                return gr.update(value="", language="python"), gr.update(visible=False)
            for s in scripts:
                if s["filename"] == name:
                    lang_map = {"Python": "python", "R": "r", "Bash": "shell"}
                    p = Path(tmp_dir) / name
                    p.write_text(s["code"], encoding="utf-8")
                    return gr.update(value=s["code"], language=lang_map.get(s["language"], "python")), gr.update(value=str(p), visible=True)
            return gr.update(value="", language="python"), gr.update(visible=False)

        def download_all(scripts):
            if not scripts:
                return gr.update(visible=False)
            return gr.update(value=_save_zip(scripts, tmp_dir), visible=True)

        def clear_all():
            return [], _skills_html(summaries), gr.update(choices=[], value=None), gr.update(value="", language="python"), gr.update(visible=False), gr.update(visible=False), "", []

        outputs = [chat, skills_panel, script_selector, dl_one, dl_all, msg, scripts_state]
        run_btn.click(respond, [msg, chat, scripts_state], outputs)
        msg.submit(respond, [msg, chat, scripts_state], outputs)
        script_selector.change(preview_script, [script_selector, scripts_state], [script_preview, dl_one])
        dl_all.click(download_all, [scripts_state], [dl_all])
        clear_btn.click(clear_all, outputs=[chat, skills_panel, script_selector, script_preview, dl_one, dl_all, msg, scripts_state])

    return demo


def launch(agent, host: str = "127.0.0.1", port: int = 7860, share: bool = False, open_browser: bool = True) -> None:
    app = create_app(agent)
    app.queue()
    app.launch(server_name=host, server_port=port, share=share, inbrowser=open_browser, show_error=True)
