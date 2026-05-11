from __future__ import annotations

import os
import re
import shlex
import subprocess
from pathlib import Path


def is_galaxy_query(query: str) -> bool:
    q = query.lower()
    keys = [
        "galaxy",
        "usegalaxy",
        "planemo",
        "workflow.ga",
        "job.yml",
        "tool discovery",
        "tool recommendation",
    ]
    return any(k in q for k in keys)


def run_galaxy_route(query: str, working_dir: str) -> str:
    """
    Dedicated route for Galaxy bridge:
      1) run tool discovery
      2) recommend workflow command
      3) optionally run planemo if workflow.ga/job.yml are present in query
    """
    base = Path(__file__).resolve().parent.parent
    discovery_script = base / "skills" / "galaxy-bridge-au" / "scripts" / "galaxy_tool_discovery.py"
    planemo_script = base / "skills" / "galaxy-bridge-au" / "scripts" / "planemo_run_workflow.sh"

    galaxy_url = os.getenv("GALAXY_URL", "https://usegalaxy.org.au")
    api_key = os.getenv("GALAXY_API_KEY", "")

    os.makedirs(working_dir, exist_ok=True)
    out_file = Path(working_dir) / "galaxy_tool_candidates.tsv"

    parts: list[str] = []
    parts.append("### Galaxy Bridge Auto Route")
    parts.append(f"- Galaxy URL: `{galaxy_url}`")
    parts.append(f"- Working dir: `{working_dir}`")

    if not api_key:
        parts.append("- API key not found (`GALAXY_API_KEY`).")
        parts.append("- Set `.env` and rerun to enable remote discovery and execution.")
        return "\n".join(parts)

    # Step 1: Discovery + ranking
    discover_cmd = [
        "python",
        str(discovery_script),
        "--galaxy-url",
        galaxy_url,
        "--api-key",
        api_key,
        "--query",
        query,
        "--topk",
        "30",
        "--output",
        str(out_file),
    ]
    try:
        proc = subprocess.run(discover_cmd, capture_output=True, text=True, cwd=working_dir, timeout=180)
        if proc.returncode == 0:
            parts.append(f"- Tool discovery completed: `{out_file}`")
        else:
            parts.append("- Tool discovery failed.")
            parts.append(f"```text\n{(proc.stderr or proc.stdout)[:1200]}\n```")
            return "\n".join(parts)
    except Exception as exc:
        parts.append(f"- Tool discovery error: `{exc}`")
        return "\n".join(parts)

    # Step 2: workflow recommendation command
    parts.append("- Recommended execution command template:")
    parts.append(
        "```bash\n"
        f"bash {shlex.quote(str(planemo_script))} {shlex.quote(galaxy_url)} \"$GALAXY_API_KEY\" workflow.ga job.yml\n"
        "```"
    )

    # Step 3: optional auto-run planemo if workflow and job files are explicitly provided
    wf_match = re.search(r"([\\w./-]+\\.ga)\\b", query)
    job_match = re.search(r"([\\w./-]+\\.ya?ml)\\b", query)
    if wf_match and job_match:
        wf = wf_match.group(1)
        job = job_match.group(1)
        run_cmd = ["bash", str(planemo_script), galaxy_url, api_key, wf, job]
        parts.append(f"- Detected workflow inputs in query: `{wf}`, `{job}`")
        try:
            proc = subprocess.run(run_cmd, capture_output=True, text=True, cwd=working_dir, timeout=3600)
            if proc.returncode == 0:
                parts.append("- Planemo run completed successfully.")
            else:
                parts.append("- Planemo run failed.")
                parts.append(f"```text\n{(proc.stderr or proc.stdout)[:1200]}\n```")
        except Exception as exc:
            parts.append(f"- Planemo execution error: `{exc}`")
    else:
        parts.append("- No explicit `workflow.ga` + `job.yml` found in query, so only discovery/recommendation was auto-run.")

    parts.append("- Next: open `galaxy_tool_candidates.tsv` and select top tools/workflow for your marine task.")
    return "\n".join(parts)
