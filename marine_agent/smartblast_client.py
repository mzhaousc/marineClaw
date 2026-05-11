"""Optional client for SmartBLAST follow-up API."""

import requests


def launch_followup(execution_plan: dict, host: str = "http://localhost:8000", timeout: int = 60) -> str:
    resp = requests.post(
        f"{host}/api/followup/start",
        json={"execution_plan": execution_plan},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return str(data.get("session_id", ""))
