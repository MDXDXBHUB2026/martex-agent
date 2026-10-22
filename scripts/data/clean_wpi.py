#!/usr/bin/env python3
"""Clean NGA World Port Index (Pub. 150) into a Zetaris-friendly CSV for the MARTEX region.

Source: NGA Maritime Safety Information, UpdatedPub150.csv (US Government, public domain).
Output: data/clean/ports_region.csv with snake_case headers.
"""
import csv
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw/UpdatedPub150.csv")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "data/clean/ports_region.csv")

REGION_KEYS = ["Persian Gulf", "Gulf of Oman", "Arabian Sea", "Red Sea",
               "Gulf of Aden", "Gulf of Suez", "Gulf of Aqaba", "Suez Canal"]

COLUMNS = {
    "World Port Index Number": "wpi_number",
    "Main Port Name": "port_name",
    "Alternate Port Name": "alt_port_name",
    "UN/LOCODE": "unlocode",
    "Country Code": "country",
    "World Water Body": "water_body",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Tidal Range (m)": "tidal_range_m",
    "Entrance Width (m)": "entrance_width_m",
    "Channel Depth (m)": "channel_depth_m",
    "Anchorage Depth (m)": "anchorage_depth_m",
    "Cargo Pier Depth (m)": "cargo_pier_depth_m",
    "Maximum Vessel Length (m)": "max_vessel_length_m",
    "Maximum Vessel Beam (m)": "max_vessel_beam_m",
    "Maximum Vessel Draft (m)": "max_vessel_draft_m",
    "Harbor Size": "harbor_size",
    "Harbor Type": "harbor_type",
    "Shelter Afforded": "shelter",
    "Entrance Restriction - Tide": "restriction_tide",
    "Entrance Restriction - Heavy Swell": "restriction_heavy_swell",
    "Entrance Restriction - Other": "restriction_other",
    "Overhead Limits": "overhead_limits",
    "Underkeel Clearance Management System": "ukc_management",
    "Estimated Time of Arrival Message": "eta_message_required",
    "Pilotage - Compulsory": "pilotage_compulsory",
    "Tugs - Assistance": "tugs_assistance",
    "Vessel Traffic Service": "vessel_traffic_service",
    "Facilities - Container": "facility_container",
    "Cranes Container": "cranes_container",
    "Supplies - Fuel Oil": "supply_fuel_oil",
    "Repairs": "repairs",
}


def main() -> None:
    with SRC.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in reader.fieldnames]
        if missing:
            sys.exit(f"Missing expected columns: {missing}")
        rows = []
        for r in reader:
            if not any(k in r["World Water Body"] for k in REGION_KEYS):
                continue
            out = {new: (r[old] or "").strip() for old, new in COLUMNS.items()}
            out["unlocode"] = out["unlocode"].replace(" ", "")
            rows.append(out)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(COLUMNS.values()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} ports to {OUT}")


if __name__ == "__main__":
    main()
