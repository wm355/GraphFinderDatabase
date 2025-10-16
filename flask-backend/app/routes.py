# app/routes.py
from flask import Blueprint, jsonify, request, current_app, abort
from pathlib import Path
import traceback
import re
from datetime import datetime
from .models import db, Upload


from .files import (
    list_types, list_elements_for_type, list_files_for, read_timeseries,
    map_element_to_types, search_elements, group_heating_cooling_pairs
)

main = Blueprint("main", __name__)

@main.route("/upload_csv", methods=["POST"])
def upload_csv():
    """
    Receives multipart/form-data:
      - file: the CSV file
      - dopant: e.g. "W", "Cr" (case-insensitive)
      - role: "heating" | "cooling" | ""
      - groupKey: pairing key from the frontend
    Saves into <UPLOAD_ROOT>/<DOPANT>/timestamp__original.csv
    """
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file"}), 400

    dopant = (request.form.get("dopant") or "").strip()
    role = (request.form.get("role") or "").strip()
    group_key = (request.form.get("groupKey") or "").strip()

    data_type = (request.form.get("data_type") or "resistance_temp").strip().lower()
    if data_type not in {"resistance_temp", "transmittance_temp"}:
        return jsonify({"error": "Invalid data_type"}), 400

    if not dopant:
        m = re.match(r"^([A-Za-z]+)_(\d+(?:\.\d+)?)(?:_|\.)", (f.filename or ""))
        dopant = m.group(1).upper() if m else "UNKNOWN"

    # Normalize dopant folder like your tree: "B", "Cr", "Fe", ...
    dopant_folder = dopant[:1].upper() + dopant[1:].lower() if dopant else "Unknown"

    # Build save path: input/<data_type>/<DOPANT>/
    root = current_app.config["UPLOAD_ROOT"]  # points to input/
    save_dir = os.path.join(root, data_type, dopant_folder)
    os.makedirs(save_dir, exist_ok=True)


    # Safe filename + timestamp
    original = re.sub(r"[^\w.\- ]+", "_", f.filename or "upload.csv")
    stamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    final_name = f"{stamp}__{original}"
    final_path = os.path.join(save_dir, final_name)

    # Save file
    f.save(final_path)

    # Insert DB row
    rec = Upload(
        dopant=dopant,
        role=role,
        group_key=group_key,
        data_type=data_type,
        filename=final_name,
        filepath=final_path,
    )
    db.session.add(rec)
    db.session.commit()

    return jsonify({
        "ok": True,
        "dopant": dopant,
        "role": role,
        "groupKey": group_key,
        "data_type": data_type,
        "savedAs": final_name,
        "folder": save_dir,
    })

@main.route("/")
def index():
    return "Welcome to the Flask API"

@main.route("/api/hello")
def hello():
    return jsonify({"message": "Hello from Flask!"})

# Optional: legacy items route (can remove if unused)
# @main.route("/api/items")
# def get_items():
#     return jsonify({"items": [], "page": 1, "per_page": 10, "total": 0})

@main.route("/api/datatypes")
def get_datatypes():
    root = Path(current_app.config["DATA_ROOT"]).resolve()
    if not root.exists():
        return jsonify({"types": []})
    return jsonify({"types": list_types(root)})

@main.route("/api/elements")
def get_elements():
    dtype = request.args.get("type")
    if not dtype:
        abort(400, "Missing ?type=")
    root = Path(current_app.config["DATA_ROOT"]).resolve()
    return jsonify({"type": dtype, "elements": list_elements_for_type(root, dtype)})

@main.route("/api/series")
def get_series():
    dtype = request.args.get("type")
    element = request.args.get("element")
    if not dtype or not element:
        abort(400, "Missing ?type= and/or ?element=")

    root = Path(current_app.config["DATA_ROOT"]).resolve()
    pairs = group_heating_cooling_pairs(root, dtype, element)

    out = []
    for concentration, file_pair in pairs.items():
        pair_info = {
            "concentration": concentration,
            "heating_file": file_pair["heating"].name if "heating" in file_pair else None,
            "cooling_file": file_pair["cooling"].name if "cooling" in file_pair else None,
            "has_both": "heating" in file_pair and "cooling" in file_pair
        }

        # Preview data from one of the files to get y_label
        if "heating" in file_pair:
            try:
                ylabel, sample_rows = read_timeseries(file_pair["heating"])
                pair_info["y_label"] = ylabel
                pair_info["sample_points"] = len(sample_rows)
            except Exception as e:
                pair_info["error"] = str(e)
        elif "cooling" in file_pair:
            try:
                ylabel, sample_rows = read_timeseries(file_pair["cooling"])
                pair_info["y_label"] = ylabel
                pair_info["sample_points"] = len(sample_rows)
            except Exception as e:
                pair_info["error"] = str(e)

        out.append(pair_info)

    return jsonify({"type": dtype, "element": element, "series": out})

@main.route("/api/search_dopants")
def search_dopants():
    q = (request.args.get("q") or "").strip()
    root = Path(current_app.config["DATA_ROOT"]).resolve()
    try:
        if not root.exists():
            return jsonify({"error": f"DATA_ROOT does not exist: {root}"}), 500

        match_map = search_elements(root, q)  # element -> { dtype -> [paths] }

        results = []
        for element, typed in sorted(match_map.items(), key=lambda kv: kv[0].lower()):
            types_list = [
                {"type": dtype, "file_count": len(files)}
                for dtype, files in sorted(typed.items(), key=lambda kv: kv[0].lower())
            ]
            results.append({"element": element, "types": types_list})

        return jsonify(results)

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to scan data folders."}), 500

@main.route("/api/chart_data")
def get_chart_data():
    dtype = request.args.get("type")
    element = request.args.get("element")
    concentration = request.args.get("concentration")

    if not dtype or not element or not concentration:
        abort(400, "Missing ?type=, ?element=, and/or ?concentration=")

    root = Path(current_app.config["DATA_ROOT"]).resolve()
    try:
        pairs = group_heating_cooling_pairs(root, dtype, element)

        if concentration not in pairs:
            return jsonify({"error": f"No data found for {element} at {concentration}% concentration"}), 404

        pair_data = pairs[concentration]
        chart_data = {"concentration": concentration, "element": element, "type": dtype, "curves": []}

        # Get the appropriate y-axis label
        y_label = "Resistance" if "resistance" in dtype else "Transmittance"
        chart_data["y_label"] = y_label

        # Read heating data
        if "heating" in pair_data:
            try:
                _, heating_points = read_timeseries(pair_data["heating"])
                chart_data["curves"].append({
                    "label": "Heating",
                    "type": "heating",
                    "color": "#ef4444",  # red
                    "data": heating_points
                })
            except Exception as e:
                chart_data["curves"].append({
                    "label": "Heating",
                    "type": "heating",
                    "error": str(e)
                })

        # Read cooling data
        if "cooling" in pair_data:
            try:
                _, cooling_points = read_timeseries(pair_data["cooling"])
                chart_data["curves"].append({
                    "label": "Cooling",
                    "type": "cooling",
                    "color": "#3b82f6",  # blue
                    "data": cooling_points
                })
            except Exception as e:
                chart_data["curves"].append({
                    "label": "Cooling",
                    "type": "cooling",
                    "error": str(e)
                })

        return jsonify(chart_data)

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to load chart data."}), 500
