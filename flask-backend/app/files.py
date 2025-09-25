# app/files.py
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import csv, json

# Common column name guesses (you can tailor these to your real files)
COMMON_TEMP_KEYS = ["temperature", "temp", "T", "Temp", "Temperature"]
COMMON_VALUE_KEYS = ["value", "resistance", "transmittance", "R", "rho", "Transmittance", "Value"]

def _pick_key(row: dict, candidates: List[str]) -> str:
    """Pick a column name from candidates (case-insensitive fallback)."""
    for k in candidates:
        if k in row:
            return k
    lower = {k.lower(): k for k in row.keys()}
    for k in candidates:
        if k.lower() in lower:
            return lower[k.lower()]
    raise KeyError("No matching column")

def list_types(data_root: Path) -> List[str]:
    """Top-level folders under DATA_ROOT are the dataset types."""
    if not data_root.exists():
        return []
    return [p.name for p in data_root.iterdir() if p.is_dir()]

def list_elements_for_type(data_root: Path, dtype: str) -> List[str]:
    """Second-level folders (elements/dopants) under a given type."""
    tdir = data_root / dtype
    if not tdir.exists():
        return []
    return [p.name for p in tdir.iterdir() if p.is_dir()]

def list_files_for(data_root: Path, dtype: str, element: str) -> List[Path]:
    """Files (.csv/.json) under DATA_ROOT/dtype/element."""
    base = data_root / dtype / element
    if not base.exists():
        return []
    return [p for p in base.iterdir() if p.is_file() and p.suffix.lower() in (".csv", ".json")]

def read_timeseries(path: Path) -> Tuple[str, List[dict]]:
    """
    Read a single CSV/JSON file and normalize to:
      y_label: str
      rows: [{'temperature': float, 'value': float}, ...]
    """
    rows: List[dict] = []
    value_label = "value"

    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            first = None
            tkey = vkey = None
            for i, r in enumerate(reader):
                if i == 0:
                    first = r
                    tkey = _pick_key(first, COMMON_TEMP_KEYS)
                    vkey = _pick_key(first, COMMON_VALUE_KEYS)
                    value_label = vkey
                # parse using detected keys
                t = float(r[tkey])
                v = float(r[vkey])
                rows.append({"temperature": t, "value": v})
    else:  # JSON
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        seq = data.get("data", data) if isinstance(data, dict) else data
        if not isinstance(seq, list) or not seq:
            raise ValueError(f"{path.name}: JSON not a non-empty list")
        tkey = _pick_key(seq[0], COMMON_TEMP_KEYS)
        vkey = _pick_key(seq[0], COMMON_VALUE_KEYS)
        value_label = vkey
        for r in seq:
            rows.append({"temperature": float(r[tkey]), "value": float(r[vkey])})

    rows.sort(key=lambda x: x["temperature"])
    return value_label, rows

def map_element_to_types(data_root: Path) -> Dict[str, Dict[str, List[Path]]]:
    """
    Build: element -> { dtype -> [file Paths...] }
    Scans DATA_ROOT/<dtype>/<element>/*
    """
    res: Dict[str, Dict[str, List[Path]]] = defaultdict(lambda: defaultdict(list))
    if not data_root or not data_root.exists():
        return res
    for dtype_dir in data_root.iterdir():
        if not dtype_dir.is_dir():
            continue
        dtype = dtype_dir.name
        for elem_dir in dtype_dir.iterdir():
            if not elem_dir.is_dir():
                continue
            element = elem_dir.name
            files = [
                p for p in elem_dir.iterdir()
                if p.is_file() and p.suffix.lower() in (".csv", ".json")
            ]
            if files:
                res[element][dtype].extend(files)
    return res

def search_elements(data_root: Path, q: str) -> Dict[str, Dict[str, List[Path]]]:
    """
    Filter element names by substring match (case-insensitive).
    Returns same shape as map_element_to_types.
    """
    q = (q or "").strip()
    full = map_element_to_types(data_root)
    if not q:
        return full
    out: Dict[str, Dict[str, List[Path]]] = {}
    for element, typed in full.items():
        if q.lower() in element.lower():
            out[element] = typed
    return out

def group_heating_cooling_pairs(data_root: Path, dtype: str, element: str) -> Dict[str, Dict[str, Path]]:
    """
    Group files by their base concentration and identify heating/cooling pairs.
    Returns: {concentration: {"heating": path, "cooling": path}}

    Example:
    - b_0.5_heating.csv and b_0.5_cooling.csv -> {"0.5": {"heating": path1, "cooling": path2}}
    """
    files = list_files_for(data_root, dtype, element)
    pairs = defaultdict(dict)

    for file_path in files:
        name = file_path.stem  # filename without extension

        # Extract base name and cycle type
        if "_heating" in name:
            base_name = name.replace("_heating", "")
            # Strip element prefix (e.g., "b_0.5" -> "0.5")
            concentration = base_name.split("_", 1)[-1] if "_" in base_name else base_name
            pairs[concentration]["heating"] = file_path
        elif "_cooling" in name:
            base_name = name.replace("_cooling", "")
            # Strip element prefix (e.g., "b_0.5" -> "0.5")
            concentration = base_name.split("_", 1)[-1] if "_" in base_name else base_name
            pairs[concentration]["cooling"] = file_path
        else:
            # Handle files without explicit heating/cooling designation
            # Strip element prefix here too
            concentration = name.split("_", 1)[-1] if "_" in name else name
            pairs[concentration]["unknown"] = file_path

    return dict(pairs)
