import io
import os
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from contextlib import redirect_stderr, redirect_stdout
from typing import Optional

_R_PAT = re.compile(r"^#!R\b", re.IGNORECASE)
_BASH_PAT = re.compile(r"^#!BASH\b", re.IGNORECASE)
_BLAST_CMD_PAT = re.compile(
    r"(^|\n)\s*(blastn|blastp|blastx|tblastn|makeblastdb|blastdbcmd|hmmscan|mafft|iqtree|fasttree|antismash)\b",
    re.IGNORECASE,
)


def detect_language(code: str) -> str:
    first = code.lstrip()
    if _R_PAT.match(first):
        return "R"
    if _BASH_PAT.match(first):
        return "Bash"
    return "Python"


def run_python(code: str, namespace: Optional[dict], working_dir: Optional[str], timeout: int) -> str:
    namespace = namespace or {}
    orig = os.getcwd()

    def _exec() -> str:
        if working_dir:
            os.makedirs(working_dir, exist_ok=True)
            os.chdir(working_dir)
        out = io.StringIO()
        err = io.StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                exec(compile(code, "<marine_agent>", "exec"), namespace)  # noqa: S102
            merged = out.getvalue()
            if err.getvalue():
                merged = (merged + f"\n[stderr]\n{err.getvalue()}").strip()
            return merged or "(executed successfully — no output)"
        except Exception as exc:
            return f"[{type(exc).__name__}] {exc}"
        finally:
            os.chdir(orig)

    with ThreadPoolExecutor(max_workers=1) as p:
        f = p.submit(_exec)
        try:
            return f.result(timeout=timeout)
        except FuturesTimeout:
            return f"[Timeout] Python execution exceeded {timeout}s"


def _run_script(code: str, suffix: str, cmd: list[str], working_dir: Optional[str], timeout: int) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as fh:
        fh.write(code)
        path = fh.name
    try:
        if suffix == ".sh":
            os.chmod(path, 0o755)
        r = subprocess.run(
            cmd + [path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir or os.getcwd(),
        )
        merged = (r.stdout or "")
        if r.stderr:
            merged = (merged + f"\n[stderr]\n{r.stderr}").strip()
        return merged or "(executed successfully — no output)"
    except subprocess.TimeoutExpired:
        return f"[Timeout] Command execution exceeded {timeout}s"
    except FileNotFoundError as exc:
        return f"[Error] Missing executable: {exc}"
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def execute_code(code: str, namespace: Optional[dict] = None, working_dir: Optional[str] = None, timeout: int = 300) -> str:
    raw = code.strip()
    lang = detect_language(raw)
    if lang == "Python" and _BLAST_CMD_PAT.search(raw):
        lang = "Bash"
        raw = f"#!BASH\n{raw}"
    if lang == "R":
        payload = _R_PAT.sub("", raw, count=1).lstrip("\n")
        return _run_script(payload, ".R", ["Rscript"], working_dir, timeout)
    if lang == "Bash":
        payload = _BASH_PAT.sub("", raw, count=1).lstrip("\n")
        if not payload.startswith("#!"):
            payload = "#!/bin/bash\nset -e\n" + payload
        return _run_script(payload, ".sh", ["bash"], working_dir, timeout)
    return run_python(raw, namespace=namespace, working_dir=working_dir, timeout=timeout)
