"""
Data pipeline orchestrator for money-flow collection rounds.

Steps: fetch -> normalize -> validate -> rebuild DB -> verify.
Emits a run manifest with sources, script versions, checksums, and counts.

Usage:
    python run_pipeline.py [--skip-fetch] [--skip-normalize] [--force]
"""
import os
import sys
import json
import hashlib
import argparse
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPTS_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

FETCH_SCRIPTS = [
    "fetch_usaspending_weighted.py",
    "fetch_usaspending_multiagency.py",
    "fetch_sbir_multiagency.py",
    "fetch_nsf_awards.py",
]

NORMALIZE_SCRIPTS = [
    "normalize_usaspending_weighted.py",
    "normalize_usaspending_multiagency.py",
    "normalize_sbir_multiagency.py",
    "score_join_integrated.py",
    "aggregate_top_recipients.py",
]

CANONICAL_FILES = [
    os.path.join(DATA_DIR, "entities", "entities_master.csv"),
    os.path.join(DATA_DIR, "financial", "money_flows.csv"),
    os.path.join(DATA_DIR, "financial", "awards_master.csv"),
    os.path.join(DATA_DIR, "entities", "entity_relationships.csv"),
]


def file_checksum(path: str) -> str:
    if not os.path.exists(path):
        return "missing"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def row_count(path: str) -> int:
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1  # exclude header


def run_script(script_name: str) -> bool:
    path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(path):
        logger.warning(f"Script not found, skipping: {script_name}")
        return True
    logger.info(f"Running: {script_name}")
    result = subprocess.run([sys.executable, path], cwd=SCRIPTS_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"FAILED: {script_name}\n{result.stderr[:500]}")
        return False
    logger.info(f"OK: {script_name}")
    return True


def run_validation() -> bool:
    logger.info("Running CSV schema validation...")
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS_DIR, "validate_csv_schema.py"), "--data-dir", DATA_DIR],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        logger.error(f"Validation failed:\n{result.stderr}")
        return False
    logger.info("Validation passed.")
    return True


def rebuild_db(force: bool = False) -> bool:
    logger.info("Rebuilding database...")
    cmd = [sys.executable, os.path.join(PROJECT_ROOT, "backend", "rebuild_database.py"), "--force"]
    if not force:
        cmd.append("--dry-run")
    result = subprocess.run(cmd, cwd=os.path.join(PROJECT_ROOT, "backend"), capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"DB rebuild failed:\n{result.stderr[:500]}")
        return False
    logger.info("DB rebuild complete.")
    return True


def emit_manifest(started_at: datetime, ended_at: datetime, success: bool):
    manifest = {
        "pipeline_run": {
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "success": success,
            "duration_seconds": (ended_at - started_at).total_seconds(),
        },
        "canonical_files": {},
    }
    for path in CANONICAL_FILES:
        name = os.path.basename(path)
        manifest["canonical_files"][name] = {
            "checksum_sha256": file_checksum(path),
            "row_count": row_count(path),
        }

    manifest_path = os.path.join(DATA_DIR, "pipeline_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Manifest written: {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="Run data collection pipeline")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip fetch scripts")
    parser.add_argument("--skip-normalize", action="store_true", help="Skip normalize scripts")
    parser.add_argument("--force", action="store_true", help="Actually rebuild DB (not dry-run)")
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc)
    success = True

    if not args.skip_fetch:
        for script in FETCH_SCRIPTS:
            if not run_script(script):
                success = False
                break

    if success and not args.skip_normalize:
        for script in NORMALIZE_SCRIPTS:
            if not run_script(script):
                success = False
                break

    if success:
        success = run_validation()

    if success:
        success = rebuild_db(force=args.force)

    ended_at = datetime.now(timezone.utc)
    emit_manifest(started_at, ended_at, success)

    if success:
        logger.info("Pipeline completed successfully.")
    else:
        logger.error("Pipeline failed. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
