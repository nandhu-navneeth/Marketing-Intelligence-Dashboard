from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import io
import zipfile

import pandas as pd

from .config import EXPECTED_FILES


def _read_csv_bytes(name: str, data: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(data))
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def load_sources(path_or_zip: Any) -> Dict[str, pd.DataFrame]:
    """Load platform and business CSVs from a folder or a .zip archive.

    Accepts:
      - Directory containing Facebook.csv, Google.csv, TikTok.csv, Business.csv
      - Zip file containing the same (case-insensitive matching)
      - File-like object or bytes (e.g., Streamlit UploadedFile) containing a zip

    Returns dict with keys: 'facebook', 'google', 'tiktok', 'business'.
    Missing files are omitted from the dict.
    """
    # If file-like or bytes passed (e.g., Streamlit upload)
    if hasattr(path_or_zip, "read") or isinstance(path_or_zip, (bytes, bytearray)):
        data = path_or_zip.read() if hasattr(path_or_zip, "read") else path_or_zip
        out: Dict[str, pd.DataFrame] = {}
        with zipfile.ZipFile(io.BytesIO(data), "r") as z:
            names = {name.lower(): name for name in z.namelist()}
            for key, fname in EXPECTED_FILES.items():
                candidate = None
                for nlower, n in names.items():
                    if nlower.endswith("/" + fname) or nlower.endswith(fname):
                        candidate = n
                        break
                if candidate:
                    with z.open(candidate) as f:
                        out[key] = _read_csv_bytes(fname, f.read())
        return out

    p = Path(path_or_zip)
    out: Dict[str, pd.DataFrame] = {}
    if p.is_dir():
        files_lower = {f.name.lower(): f for f in p.iterdir() if f.is_file()}
        for key, fname in EXPECTED_FILES.items():
            match = files_lower.get(fname)
            if match is None:
                # also try exact-case names
                alt = p / fname
                if alt.exists():
                    match = alt
            if match is not None:
                df = pd.read_csv(match)
                df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                out[key] = df
        return out

    # Else if zip
    if p.suffix.lower() == ".zip" and p.exists():
        with zipfile.ZipFile(p, "r") as z:
            names = {name.lower(): name for name in z.namelist()}
            for key, fname in EXPECTED_FILES.items():
                # locate a member by case-insensitive file name match on basename
                candidate = None
                for nlower, n in names.items():
                    if nlower.endswith("/" + fname) or nlower.endswith(fname):
                        candidate = n
                        break
                if candidate:
                    with z.open(candidate) as f:
                        out[key] = _read_csv_bytes(fname, f.read())
        return out

    raise FileNotFoundError(f"Path not found or unsupported: {p}")
