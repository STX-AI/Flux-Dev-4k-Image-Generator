
---

## `gen_local.py`
```python
#!/usr/bin/env python3
"""
gen_local.py  —  CSV → ComfyUI → images in ./output/

Place this file in the MAIN ComfyUI folder (same directory as main.py).
Also place stoxx_api.json and prompts.csv in the same folder.

- Reads 'prompts.csv' (prompt,filename,processed)
- For each row: injects prompt into your workflow, randomizes seed, forces Save node to default ./output/
- Queues the job via ComfyUI REST and waits for completion
- No website upload code
"""

import os
import csv
import json
import time
import uuid
import copy
import random
from typing import Dict, Optional

import requests

# ── ComfyUI server ────────────────────────────────────────────────────────────
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8188
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# ── File paths (script lives in ComfyUI root) ─────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
WORKFLOW_JSON = os.path.join(BASE_DIR, "stoxx_api.json")
CSV_PATH = os.path.join(BASE_DIR, "prompts.csv")

# ── Polling ───────────────────────────────────────────────────────────────────
POLL_INTERVAL = 1.0
TIMEOUT = 60 * 20  # 20 minutes per job safety timeout


def load_workflow(path: str) -> Dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Workflow JSON not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_node_id(wf: Dict, want_class: str = "", has_keys: tuple = ()) -> Optional[str]:
    """
    Find a node by class_type (preferred) or by checking if input keys exist.
    Returns the first matching node-id (as a string).
    """
    for node_id, node in wf.items():
        if not isinstance(node, dict):
            continue
        ctype = node.get("class_type", "")
        inputs = node.get("inputs", {}) or {}
        if want_class and ctype == want_class:
            return str(node_id)
        if has_keys and all(k in inputs for k in has_keys):
            return str(node_id)
    return None


def prepare_workflow(
    workflow: Dict,
    prompt_text: str,
    filename_prefix: str = "generated",
) -> Dict:
    wf = copy.deepcopy(workflow)

    # 1) Try to find common nodes automatically
    prompt_node = (
        find_node_id(wf, want_class="CLIPTextEncode")
        or find_node_id(wf, want_class="CLIPTextEncodeSDXL")
        or find_node_id(wf, want_class="Text")
        or find_node_id(wf, has_keys=("text",))
    )
    sampler_node = (
        find_node_id(wf, want_class="KSampler")
        or find_node_id(wf, has_keys=("steps", "cfg", "seed"))
    )
    save_node = (
        find_node_id(wf, want_class="SaveImage")
        or find_node_id(wf, has_keys=("filename_prefix",))
    )

    if not prompt_node:
        raise RuntimeError("Couldn't auto-find a prompt text node (e.g., CLIPTextEncode).")
    if not sampler_node:
        raise RuntimeError("Couldn't auto-find a KSampler node (steps/cfg/seed).")
    if not save_node:
        raise RuntimeError("Couldn't auto-find a SaveImage node.")

    # 2) Set prompt text
    wf[prompt_node]["inputs"]["text"] = prompt_text

    # 3) Randomize seed (replace with a fixed seed if desired)
    wf[sampler_node]["inputs"]["seed"] = random.randint(1, 10**9)

    # 4) Force Save node to default ComfyUI output/ by clearing `output_path`
    wf[save_node]["inputs"]["output_path"] = ""  # default ./output/
    wf[save_node]["inputs"]["filename_prefix"] = filename_prefix

    # (Optional) add CSV-driven params here (width/height/steps/cfg/etc.)

    return wf


def queue_prompt(wf: Dict, client_id: str) -> str:
    r = requests.post(
        f"{BASE_URL}/prompt",
        json={"prompt": wf, "client_id": client_id},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    prompt_id = data.get("prompt_id")
    if not prompt_id:
        raise RuntimeError("ComfyUI did not return a prompt_id.")
    return prompt_id


def wait_for_done(prompt_id: str, timeout_s: int = TIMEOUT) -> Dict:
    start = time.time()
    while True:
        r = requests.get(f"{BASE_URL}/history/{prompt_id}", params={"full": True}, timeout=30)
        r.raise_for_status()
        payload = r.json() or {}
        entry = payload.get(prompt_id, {})
        # ComfyUI marks completion in a few shapes; check broadly
        if entry.get("completed") or entry.get("status", {}).get("completed"):
            return entry
        if (time.time() - start) > timeout_s:
            raise TimeoutError(f"Timed out waiting for prompt {prompt_id}")
        time.sleep(POLL_INTERVAL)


def main():
    wf = load_workflow(WORKFLOW_JSON)

    # Create CSV if missing
    if not os.path.isfile(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as out:
            out.write("prompt,filename,processed\n")
        print(f"Created sample CSV at {CSV_PATH}. Add prompts and commit.")
        return

    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("CSV is empty. Add at least one row with a 'prompt' value.")
        return

    # Ensure 'processed' column exists
    fieldnames = list(rows[0].keys())
    if "processed" not in fieldnames:
        fieldnames.append("processed")
        for r in rows:
            r["processed"] = ""

    client_id = str(uuid.uuid4())

    for idx, row in enumerate(rows):
        # Skip processed rows
        if str(row.get("processed", "")).strip().lower() in ("1", "true", "yes", "done", "y"):
            continue

        prompt_text = (row.get("prompt") or "").strip()
        if not prompt_text:
            rows[idx]["processed"] = "1"
            continue

        filename_prefix = (row.get("filename") or f"image_{idx:04d}").strip()

        wf_row = prepare_workflow(
            workflow=wf,
            prompt_text=prompt_text,
            filename_prefix=filename_prefix,
        )

        pid = queue_prompt(wf_row, client_id)
        print(f"[{idx+1}] queued prompt_id={pid} — {prompt_text[:80]!r}")
        _ = wait_for_done(pid)
        print("    ✓ finished (saved by ComfyUI SaveImage node)")

        rows[idx]["processed"] = "1"

        # Persist CSV after each row
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    print("Done. Images should be in the ./output/ folder of your ComfyUI directory.")


if __name__ == "__main__":
    main()
