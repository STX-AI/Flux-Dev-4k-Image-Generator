# ComfyUI CSV → Image (local only)

Batch-generate images with **ComfyUI** from a CSV of prompts using an existing workflow.
- Place these files in the **main ComfyUI folder** (same directory as `main.py`)
- Images are saved in ComfyUI’s default `output/` folder
- **No website uploads** (clean script for open source)

## Requirements
- Python 3.9+
- ComfyUI running locally (default API: `http://127.0.0.1:8188`)
- Models: **Flux1 dev FP8** in `ComfyUI/models/` (install per its license)
- Custom nodes: **ComfyUI-Manager** and **WAS (was-ns)** installed in ComfyUI

## What’s in this repo
- `gen_local.py` – CSV → ComfyUI → images in `output/`
- `prompts.csv` – sample CSV
- `stoxx_api.json` – your ComfyUI workflow (template; replace with your export)
- `requirements.txt` – Python deps (`requests`)

## How it works
- Loads your `stoxx_api.json` workflow.
- Auto-finds common nodes:
  - Positive prompt → a Text/CLIPTextEncode node with a `text` input
  - Sampler → a KSampler node (it randomizes `seed` each run)
  - Save → a SaveImage node (forces `output_path` = `""` so ComfyUI uses `output/`)
- Queues a job per CSV row via ComfyUI’s REST API and waits for completion.

## CSV format
Minimum columns:
- `prompt` (required)
- `filename` (optional; used as filename prefix)
- `processed` (optional; the script marks this to avoid reruns)

Example:
```csv
prompt,filename,processed
"a cozy sci-fi reading nook, soft light",nook_0001,
"golden retriever astronaut, photorealistic",doge_space_0001,
