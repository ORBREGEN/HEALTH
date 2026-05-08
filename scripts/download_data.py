"""
Download HEALTH datasets from their source URLs.

Usage:
  python scripts/download_data.py --list
  python scripts/download_data.py --dataset hlca_full
  python scripts/download_data.py --dataset hlca_core hlca_embeddings
  python scripts/download_data.py --all

Files are saved to the DATA_DIR configured in app/core/config.py (default: data/).
Downloads resume automatically — if a file is already present and the right size, it is skipped.
"""

import argparse
import sys
import time
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import httpx
    from tqdm import tqdm
except ImportError:
    print("Missing dependencies. Run: pip install httpx tqdm")
    sys.exit(1)

from app.core.config import DATASET_CATALOG, settings

DATA_DIR = settings.DATA_DIR
CHUNK_SIZE = 1024 * 1024  # 1 MB
CONNECT_TIMEOUT = 30.0
READ_TIMEOUT = 300.0


# ── Formatting helpers ─────────────────────────────────────────────────────────

def _fmt_size(gb: float) -> str:
    if gb < 0.001:
        return f"{gb * 1024:.0f} KB"
    if gb < 1.0:
        return f"{gb * 1024:.0f} MB"
    return f"{gb:.2f} GB"


def _status(entry: dict) -> str:
    path = DATA_DIR / entry["filename"]
    if not path.exists():
        return "missing"
    expected_bytes = int(entry["size_gb"] * 1024**3)
    actual_bytes = path.stat().st_size
    # Allow 5% tolerance — compressed sizes vary slightly
    if actual_bytes < expected_bytes * 0.95:
        return "incomplete"
    return "present"


# ── List command ───────────────────────────────────────────────────────────────

def cmd_list(show_present: bool = True, show_missing: bool = True) -> None:
    total_gb = 0.0
    missing_gb = 0.0

    print(f"\n{'ID':<22} {'SIZE':>8}  {'STATUS':<12} NAME")
    print("-" * 80)
    for entry in DATASET_CATALOG:
        st = _status(entry)
        if st == "present" and not show_present:
            continue
        if st != "present" and not show_missing:
            continue

        marker = "✓" if st == "present" else ("⚠" if st == "incomplete" else " ")
        size_str = _fmt_size(entry["size_gb"])
        print(f"  {entry['id']:<20} {size_str:>8}  [{marker}] {st:<9} {entry['name']}")
        total_gb += entry["size_gb"]
        if st != "present":
            missing_gb += entry["size_gb"]

    print("-" * 80)
    print(f"  Total: {_fmt_size(total_gb)}")
    if missing_gb > 0:
        print(f"  Not downloaded: {_fmt_size(missing_gb)}")
    print(f"  Data directory: {DATA_DIR}\n")


# ── Download a single file ─────────────────────────────────────────────────────

def _download_one(entry: dict) -> bool:
    """
    Download one dataset. Returns True on success, False on failure.
    Resumes partial downloads using Range header.
    """
    url = entry["url"]
    dest = DATA_DIR / entry["filename"]
    expected_gb = entry["size_gb"]
    expected_bytes = int(expected_gb * 1024**3)

    if not url:
        print(f"  ⚠  {entry['id']}: no URL defined — skipping")
        return False

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check if already complete
    st = _status(entry)
    if st == "present":
        print(f"  ✓  {entry['id']}: already downloaded ({_fmt_size(expected_gb)}) — skipping")
        return True

    # Resume from existing partial file
    resume_bytes = dest.stat().st_size if dest.exists() else 0
    if resume_bytes > 0:
        print(f"  ↩  {entry['id']}: resuming from {_fmt_size(resume_bytes / 1024**3)}")

    headers = {"Range": f"bytes={resume_bytes}-"} if resume_bytes > 0 else {}

    print(f"  ↓  {entry['id']}: {entry['name']}")
    print(f"     URL: {url}")
    print(f"     Destination: {dest}")

    try:
        with httpx.stream(
            "GET",
            url,
            headers=headers,
            follow_redirects=True,
            timeout=httpx.Timeout(connect=CONNECT_TIMEOUT, read=READ_TIMEOUT, write=10.0, pool=10.0),
        ) as response:
            response.raise_for_status()

            # Total for the progress bar
            content_length = int(response.headers.get("content-length", 0))
            total_for_bar = resume_bytes + content_length if content_length else expected_bytes

            mode = "ab" if resume_bytes > 0 else "wb"
            with open(dest, mode) as f, tqdm(
                total=total_for_bar,
                initial=resume_bytes,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=entry["id"],
                ncols=80,
            ) as bar:
                for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
                    bar.update(len(chunk))

        # Verify final size
        final_size = dest.stat().st_size
        if expected_bytes > 0 and final_size < expected_bytes * 0.95:
            print(f"  ✗  {entry['id']}: file is smaller than expected "
                  f"({_fmt_size(final_size / 1024**3)} vs {_fmt_size(expected_gb)}) — may be corrupt")
            return False

        print(f"  ✓  {entry['id']}: complete ({_fmt_size(final_size / 1024**3)})\n")
        return True

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 416:
            # Range not satisfiable — file is already complete
            print(f"  ✓  {entry['id']}: server says file is already complete\n")
            return True
        print(f"  ✗  {entry['id']}: HTTP {e.response.status_code} — {e}\n")
        return False
    except httpx.RequestError as e:
        print(f"  ✗  {entry['id']}: network error — {e}\n")
        return False
    except KeyboardInterrupt:
        print(f"\n  ⚠  {entry['id']}: interrupted — partial file kept at {dest}")
        print("     Re-run the same command to resume.\n")
        raise


# ── Download command ───────────────────────────────────────────────────────────

def cmd_download(ids: list[str]) -> None:
    catalog = {entry["id"]: entry for entry in DATASET_CATALOG}

    # Validate all IDs first
    unknown = [i for i in ids if i not in catalog]
    if unknown:
        print(f"Unknown dataset ID(s): {', '.join(unknown)}")
        print(f"Valid IDs: {', '.join(catalog.keys())}")
        sys.exit(1)

    entries = [catalog[i] for i in ids]
    total_needed_gb = sum(
        e["size_gb"] for e in entries if _status(e) != "present"
    )

    if total_needed_gb == 0:
        print("\nAll requested datasets are already present.\n")
        return

    print(f"\nDownloading {len(entries)} dataset(s) — {_fmt_size(total_needed_gb)} needed\n")
    start = time.time()
    success = 0
    failed = []

    for entry in entries:
        try:
            ok = _download_one(entry)
        except KeyboardInterrupt:
            sys.exit(130)
        if ok:
            success += 1
        else:
            failed.append(entry["id"])

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.0f}s — {success}/{len(entries)} succeeded")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download HEALTH datasets from their source URLs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/download_data.py --list
  python scripts/download_data.py --dataset hlca_full
  python scripts/download_data.py --dataset hlca_core hlca_embeddings hlca_gene_order
  python scripts/download_data.py --all

Recommended first download (fast, enables all endpoints):
  python scripts/download_data.py --dataset hlca_gene_order hlca_embeddings

Full reference atlas (20 GB — needed for live scVI cell matching):
  python scripts/download_data.py --dataset hlca_full
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--list",
        action="store_true",
        help="List all datasets and their download status",
    )
    group.add_argument(
        "--dataset",
        metavar="ID",
        nargs="+",
        help="Download one or more specific datasets by ID",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help=f"Download all {len(DATASET_CATALOG)} datasets (~{_fmt_size(sum(e['size_gb'] for e in DATASET_CATALOG))} total)",
    )
    group.add_argument(
        "--missing",
        action="store_true",
        help="Download only datasets not yet on disk",
    )

    args = parser.parse_args()

    if args.list:
        cmd_list()
    elif args.dataset:
        cmd_download(args.dataset)
    elif args.all:
        cmd_download([e["id"] for e in DATASET_CATALOG])
    elif args.missing:
        missing_ids = [e["id"] for e in DATASET_CATALOG if _status(e) != "present"]
        if not missing_ids:
            print("\nAll datasets are already present.\n")
        else:
            cmd_download(missing_ids)


if __name__ == "__main__":
    main()
