# ComfyUI CSV Batch Image Generator (Flux1 Dev FP8, Local Only)

Generate **AI images with ComfyUI** from a **CSV of prompts**—fully local, no uploads.  
**Browse & download free AI stock images:** **[STOXX.io](https://stoxx.io)**

[![Website: STOXX.io](https://img.shields.io/badge/Website-STOXX.io-blue)](https://stoxx.io)
[![ComfyUI](https://img.shields.io/badge/Works%20with-ComfyUI-success)](#requirements)
[![License](https://img.shields.io/badge/License-CC0%201.0-informational)](#license)

> **What this is:** A small, reliable script that takes prompts from `prompts.csv`, injects them into your **ComfyUI** workflow (e.g., **Flux1 Dev FP8**), and saves images to ComfyUI’s default `output/` directory.  
> **What this isn’t:** No website uploads, no API keys, no model redistribution.

---

## Table of Contents
- [Features](#features)
- [Live Website](#live-website)
- [Requirements](#requirements)
- [What’s in this repo](#whats-in-this-repo)
- [Install](#install)
- [Quick Start](#quick-start)
- [How it works](#how-it-works)
- [CSV format](#csv-format)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [License](#license)
- [Attribution](#attribution)

---

## Features
- 🔁 **Batch generation from CSV**: run many prompts hands-free.
- 🧩 **Workflow-agnostic**: uses your exported `stoxx_api.json` ComfyUI workflow.
- 🎛️ **Automatic node discovery**: finds Prompt, KSampler, and SaveImage nodes.
- 🧪 **Deterministic or random seeds**: defaults to randomized seeds per row.
- 💾 **Local output**: images saved to ComfyUI’s **`output/`** folder.
- 🔒 **Privacy-first**: no uploads, no credentials, no external calls (other than the local ComfyUI API).

---

## Live Website
- **Free AI stock images & docs:** **[STOXX.io](https://stoxx.io)**

---

## Requirements
- **Python** 3.9+
- **ComfyUI** running locally (default API: `http://127.0.0.1:8188`)
- **Models:** Flux1 Dev FP8 in `ComfyUI/models/` (install per its license)
- **Custom nodes:** ComfyUI-Manager and **WAS (was-ns)** installed/enabled in ComfyUI

> Do **not** commit or redistribute model weights.

---

## What’s in this repo
- `gen_local.py` – CSV → ComfyUI → images saved in `output/`
- `prompts.csv` – sample CSV (replace with your prompts)
- `stoxx_api.json` – your ComfyUI workflow (replace with your export)
- `requirements.txt` – Python dependency list (`requests`)

---

## Install
```bash
pip install -r requirements.txt
```

---

## Quick Start
1) Place **all files** (`gen_local.py`, `stoxx_api.json`, `prompts.csv`) in your **main ComfyUI folder** (same directory as `main.py`).  
2) Start **ComfyUI** normally.  
3) In a second terminal (same folder), run:
```bash
python gen_local.py
```
4) Check images in: `./output/` (inside your ComfyUI folder).

---

## How it works
- Loads your `stoxx_api.json` **ComfyUI workflow**.
- Auto-finds common nodes:
  - **Prompt** → a `Text` / `CLIPTextEncode` node with a `text` input
  - **Sampler** → a `KSampler` node (`steps`, `cfg`, `seed`)
  - **Save** → a `SaveImage` node (script forces `output_path = ""` → ComfyUI default `output/`)
- For each CSV row:
  1. Injects the prompt text  
  2. Sets a random seed (or fix it if you prefer)  
  3. Queues the job via the ComfyUI REST API  
  4. Waits until completed

---

## CSV format
Minimum columns:
- `prompt` (required)
- `filename` (optional; used as filename prefix)
- `processed` (optional; the script marks it so rows aren’t re-run)

**Example:**
```csv
prompt,filename,processed
"a cozy sci-fi reading nook, soft light",nook_0001,
"golden retriever astronaut, photorealistic",doge_space_0001,
```

---

## Customization
- **Fixed seed**: in `gen_local.py`, replace the random seed line with your seed (e.g., `123456789`).
- **Adjust steps/CFG/size**: set them in your ComfyUI graph and re-export `stoxx_api.json`.  
  *(Advanced: extend the script to read `width`, `height`, `steps`, `cfg`, etc., from CSV and map them into the workflow.)*
- **Different CSV name**: change `CSV_PATH` in `gen_local.py`.

---

## Troubleshooting
- **Connection refused**  
  ComfyUI may not be running or uses a different host/port. Update `SERVER_HOST` / `SERVER_PORT` in `gen_local.py`.
- **Save node not found**  
  Ensure your workflow includes a standard **`SaveImage`** node.
- **Images not in `output/`**  
  Leave the Save node’s `output_path` empty. The script also forces this at runtime.

---

## FAQ
**Q: Can I use this without Flux1 Dev FP8?**  
A: Yes—any ComfyUI workflow with compatible prompt/sampler/save nodes should work. Just export to `stoxx_api.json`.

**Q: Will this upload to my website?**  
A: No. This open-source version is strictly local. No web uploads, no keys.

**Q: Can I process thousands of rows?**  
A: Yes, but consider chunking and monitoring disk space in `output/`.

**Q: How do I make the URL more visible?**  
A: Put it near the top (as shown), add a badge, and also set your repo’s **About → Website** link.

---

## License
This project is released under **CC0 1.0 Universal (Public Domain Dedication)**. See `LICENSE` for full text.

---

## Attribution
- Built for **ComfyUI** workflows  
- Uses **WAS (was-ns)** and **ComfyUI-Manager** nodes where applicable  
- Free AI stock images: **[STOXX.io](https://stoxx.io)**

<!--
Optional non-rendered notes for maintainers (safe to keep here):
- Target keywords: ComfyUI, Flux1 Dev FP8, CSV image generator, batch AI image generation, Stable Diffusion, WAS nodes, ComfyUI Manager, local inference, FP8
- Primary CTA (above the fold): https://stoxx.io
- Keep headings descriptive; badges help link previews
-->
