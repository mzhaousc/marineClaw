import argparse
import json
import os
import time
from pathlib import Path

import requests


def read_fasta(path: str) -> str:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    seq = "".join([x.strip() for x in lines if x and not x.startswith(">")])
    if not seq:
        raise ValueError("Empty FASTA sequence.")
    return seq


def submit_job(base_url: str, api_key: str, sequence: str, model: str | None = None) -> str:
    payload = {"sequence": sequence}
    if model:
        payload["model"] = model
    resp = requests.post(
        f"{base_url.rstrip('/')}/predict",
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    job_id = data.get("job_id") or data.get("id")
    if not job_id:
        raise RuntimeError(f"Cannot find job id in response: {data}")
    return str(job_id)


def wait_job(base_url: str, api_key: str, job_id: str, poll_seconds: int = 10, timeout_seconds: int = 7200) -> dict:
    start = time.time()
    while True:
        if time.time() - start > timeout_seconds:
            raise TimeoutError(f"Job {job_id} timeout after {timeout_seconds}s")
        resp = requests.get(
            f"{base_url.rstrip('/')}/jobs/{job_id}",
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        status = str(data.get("status", "")).lower()
        print(f"[{job_id}] status: {status}")
        if status in {"completed", "succeeded", "done"}:
            return data
        if status in {"failed", "error"}:
            raise RuntimeError(f"Job failed: {data}")
        time.sleep(poll_seconds)


def fetch_result(base_url: str, api_key: str, job_id: str) -> dict:
    resp = requests.get(
        f"{base_url.rstrip('/')}/jobs/{job_id}/result",
        headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def maybe_download_files(result: dict, out_dir: Path) -> None:
    # Flexible parsing for common API schemas
    urls = []
    if isinstance(result.get("files"), list):
        for f in result["files"]:
            if isinstance(f, dict) and f.get("url"):
                urls.append((f.get("name") or "result_file", f["url"]))
    for key in ["pdb_url", "cif_url", "pae_url"]:
        if result.get(key):
            urls.append((key.replace("_url", ""), result[key]))

    for name, url in urls:
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            suffix = Path(url).suffix or ".dat"
            out_path = out_dir / f"{name}{suffix}"
            out_path.write_bytes(r.content)
            print(f"Downloaded: {out_path}")
        except Exception as exc:
            print(f"Warning: failed to download {url}: {exc}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run AlphaFold-compatible API prediction from FASTA.")
    ap.add_argument("--fasta", required=True, help="Input FASTA file path")
    ap.add_argument("--output-dir", default="af_out", help="Output directory")
    ap.add_argument("--model", default=None, help="Optional model/version name")
    ap.add_argument("--poll-seconds", type=int, default=10)
    ap.add_argument("--timeout-seconds", type=int, default=7200)
    args = ap.parse_args()

    base_url = os.getenv("ALPHAFOLD_API_URL", "").strip()
    api_key = os.getenv("ALPHAFOLD_API_KEY", "").strip()
    if not base_url:
        raise SystemExit("Please set ALPHAFOLD_API_URL in environment.")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sequence = read_fasta(args.fasta)
    print(f"Sequence length: {len(sequence)} aa")

    job_id = submit_job(base_url, api_key, sequence, model=args.model)
    print(f"Submitted job: {job_id}")

    wait_meta = wait_job(
        base_url,
        api_key,
        job_id,
        poll_seconds=args.poll_seconds,
        timeout_seconds=args.timeout_seconds,
    )
    (out_dir / "job_status.json").write_text(json.dumps(wait_meta, indent=2), encoding="utf-8")

    result = fetch_result(base_url, api_key, job_id)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    maybe_download_files(result, out_dir)
    print(f"Saved outputs to: {out_dir}")


if __name__ == "__main__":
    main()
