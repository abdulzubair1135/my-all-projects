"""
ZUBAIR LLM — Phase 1: Colab Diagnostic, Inventory & Metadata Audit Script
Run this script or notebook cell directly in Google Colab with GPU runtime enabled.
Google Drive Root: /content/drive/MyDrive/ZUBAIR_LLM
"""

import os
import sys
import json
import hashlib
from pathlib import Path

def get_file_hash(filepath: Path, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return f"Error reading hash: {e}"

def run_colab_audit(project_root_str: str = "/content/drive/MyDrive/ZUBAIR_LLM"):
    report = {
        "environment": {},
        "project_root_exists": False,
        "manifest": [],
        "checkpoints": {},
        "tokenizer": {},
        "datasets": {},
        "active_code_or_notebooks": [],
        "warnings": []
    }

    # 1. Environment & Hardware Checks
    print("=" * 70)
    print("ZUBAIR LLM — PHASE 1 AUDIT & INVENTORY")
    print("=" * 70)

    try:
        import torch
        report["environment"]["python_version"] = sys.version
        report["environment"]["pytorch_version"] = torch.__version__
        cuda_avail = torch.cuda.is_available()
        report["environment"]["cuda_available"] = cuda_avail
        if cuda_avail:
            report["environment"]["gpu_name"] = torch.cuda.get_device_name(0)
            report["environment"]["gpu_vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
            print(f"[OK] CUDA GPU Detected: {report['environment']['gpu_name']} ({report['environment']['gpu_vram_gb']} GB VRAM)")
        else:
            report["warnings"].append("CUDA is NOT available in this Colab session.")
            print("[WARNING] CUDA is NOT available. Switch runtime to T4 or A100 GPU before model execution.")
    except Exception as e:
        report["warnings"].append(f"PyTorch check failed: {e}")
        print(f"[ERROR] PyTorch check failed: {e}")

    # 2. Project Root & Drive Checks
    project_root = Path(project_root_str)
    if not project_root.exists():
        msg = f"Project root {project_root_str} does not exist. Please mount Google Drive with drive.mount('/content/drive')."
        report["warnings"].append(msg)
        print(f"[ERROR] {msg}")
        return report

    report["project_root_exists"] = True
    print(f"[OK] Project Root Verified: {project_root}")

    # 3. File Inventory & Hash Manifest
    print("\nScanning project directory tree...")
    all_files = list(project_root.rglob("*"))
    file_records = []
    for p in all_files:
        if p.is_file():
            rel_path = str(p.relative_to(project_root)).replace("\\", "/")
            size_mb = round(p.stat().st_size / (1024 * 1024), 3)
            file_records.append({
                "path": rel_path,
                "size_mb": size_mb,
                "size_bytes": p.stat().st_size
            })
            if p.suffix in [".ipynb", ".py"]:
                report["active_code_or_notebooks"].append(rel_path)

    report["manifest"] = file_records
    print(f"[OK] Inventoried {len(file_records)} files across project.")

    # 4. Checkpoints Audit
    print("\nAuditing Checkpoints...")
    target_checkpoints = [
        "checkpoints/stage3_scratch_v1/best.pt",
        "checkpoints/stage3_scratch_resume_v1/best.pt",
        "checkpoints/stage3_quality_finetune_v2/best.pt"
    ]
    
    # Also find any other .pt files
    found_pt_files = [r["path"] for r in file_records if r["path"].endswith(".pt")]
    all_ckpt_paths = sorted(list(set(target_checkpoints + found_pt_files)))

    import torch
    for ckpt_rel in all_ckpt_paths:
        ckpt_path = project_root / ckpt_rel
        if not ckpt_path.exists():
            report["checkpoints"][ckpt_rel] = {"status": "MISSING"}
            print(f"  [-] {ckpt_rel}: NOT FOUND")
            continue

        print(f"  [+] Inspecting: {ckpt_rel} ...")
        ckpt_info = {
            "status": "EXISTS",
            "size_mb": round(ckpt_path.stat().st_size / (1024 * 1024), 2),
            "sha256": get_file_hash(ckpt_path),
            "metadata_keys": [],
            "state_dict_keys_count": 0,
            "total_params": 0,
            "epoch": None,
            "step": None,
            "config": None
        }

        try:
            # Inspect metadata safely on CPU without moving model to GPU
            data = torch.load(str(ckpt_path), map_location="cpu")
            if isinstance(data, dict):
                ckpt_info["metadata_keys"] = list(data.keys())
                for ep_key in ["epoch", "current_epoch", "epochs"]:
                    if ep_key in data:
                        ckpt_info["epoch"] = data[ep_key]
                for st_key in ["step", "global_step"]:
                    if st_key in data:
                        ckpt_info["step"] = data[st_key]
                if "config" in data:
                    ckpt_info["config"] = str(data["config"])

                # Determine state dict
                sd = data.get("model_state_dict", data.get("state_dict", data.get("model", data)))
                if isinstance(sd, dict):
                    ckpt_info["state_dict_keys_count"] = len(sd)
                    total_p = 0
                    sample_shapes = {}
                    for k, v in sd.items():
                        if hasattr(v, "numel"):
                            total_p += v.numel()
                            if len(sample_shapes) < 8:
                                sample_shapes[k] = list(v.shape)
                    ckpt_info["total_params"] = total_p
                    ckpt_info["sample_param_shapes"] = sample_shapes
            print(f"      -> Size: {ckpt_info['size_mb']} MB, Params: {ckpt_info['total_params']:,}, Epoch: {ckpt_info['epoch']}, Keys: {ckpt_info['metadata_keys']}")
        except Exception as e:
            ckpt_info["load_error"] = str(e)
            print(f"      -> ERROR loading checkpoint: {e}")

        report["checkpoints"][ckpt_rel] = ckpt_info

    # 5. Tokenizer Audit
    print("\nAuditing Tokenizer...")
    tok_rel = "tokenizer/zubair_bpe_v3.json"
    tok_path = project_root / tok_rel
    if tok_path.exists():
        tok_info = {
            "status": "EXISTS",
            "size_kb": round(tok_path.stat().st_size / 1024, 2),
            "sha256": get_file_hash(tok_path)
        }
        try:
            with open(tok_path, "r", encoding="utf-8") as f:
                tok_data = json.load(f)
            tok_info["model_type"] = tok_data.get("model", {}).get("type", "unknown")
            vocab = tok_data.get("model", {}).get("vocab", {})
            tok_info["vocab_size"] = len(vocab)
            tok_info["added_tokens"] = tok_data.get("added_tokens", [])
            print(f"  [+] Tokenizer found: Vocab Size = {tok_info['vocab_size']}, Added Tokens Count = {len(tok_info['added_tokens'])}")
        except Exception as e:
            tok_info["load_error"] = str(e)
            print(f"  [-] Tokenizer parse error: {e}")
        report["tokenizer"] = tok_info
    else:
        print(f"  [-] Tokenizer NOT found at {tok_rel}")
        report["tokenizer"] = {"status": "MISSING"}

    # 6. Datasets Audit
    print("\nAuditing Datasets...")
    dataset_targets = [
        "dataset/cleaned/expanded_v1.jsonl",
        "dataset/splits_expanded_v1/train.jsonl",
        "dataset/splits_expanded_v1/validation.jsonl",
        "dataset/splits_expanded_v1/test.jsonl",
        "dataset/cleaned/targeted_quality_v2.jsonl",
        "dataset/targeted_v2_splits/train.jsonl",
        "dataset/targeted_v2_splits/validation.jsonl"
    ]

    for ds_rel in dataset_targets:
        ds_path = project_root / ds_rel
        if not ds_path.exists():
            report["datasets"][ds_rel] = {"status": "MISSING"}
            print(f"  [-] {ds_rel}: NOT FOUND")
            continue

        print(f"  [+] Checking {ds_rel} ...")
        valid_lines = 0
        invalid_lines = 0
        sample_keys = None
        empty_responses = 0

        try:
            with open(ds_path, "r", encoding="utf-8") as f:
                for line in f:
                    line_s = line.strip()
                    if not line_s:
                        continue
                    try:
                        record = json.loads(line_s)
                        valid_lines += 1
                        if sample_keys is None:
                            sample_keys = list(record.keys())
                        resp = record.get("response", record.get("output", record.get("answer", "")))
                        if not resp or str(resp).strip() == "":
                            empty_responses += 1
                    except Exception:
                        invalid_lines += 1

            ds_info = {
                "status": "EXISTS",
                "valid_records": valid_lines,
                "invalid_json_lines": invalid_lines,
                "empty_responses": empty_responses,
                "sample_keys": sample_keys,
                "size_mb": round(ds_path.stat().st_size / (1024 * 1024), 2),
                "sha256": get_file_hash(ds_path)
            }
            print(f"      -> Records: {valid_lines}, Invalid lines: {invalid_lines}, Empty: {empty_responses}, Keys: {sample_keys}")
        except Exception as e:
            ds_info = {"status": "ERROR", "error": str(e)}
            print(f"      -> ERROR reading dataset: {e}")

        report["datasets"][ds_rel] = ds_info

    # 7. Save and Return Report
    out_path = project_root / "experiments" / "audit_phase1_inventory_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 70)
    print(f"AUDIT COMPLETE. Report saved to:\n{out_path}")
    print("=" * 70)
    print("\nPlease copy the summary printed above or copy the contents of audit_phase1_inventory_report.json")
    print("and share it in our chat so we can proceed with Phase 2!")
    return report

if __name__ == "__main__":
    run_colab_audit()
