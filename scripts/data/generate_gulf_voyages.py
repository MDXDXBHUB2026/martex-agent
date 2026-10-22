#!/usr/bin/env python3
"""Generate synthetic operator data for the MARTEX demo: 3 container vessels inbound to Jebel Ali (AEJEA).

All vessel data is SYNTHETIC (no real vessel, operator or voyage). It stands in for an operator's
internal fleet database, which is never public. Field names follow packages/core-domain
(MainEngineState: rpm, loadPercent, exhaustTempAvgC, exhaustTempDeviationC).

Scenarios (deterministic, seeded):
  MV Meridian Voyager  - turbocharger fouling over the last 24 h: speed falls at constant RPM,
                          exhaust temperatures rise, alarm raised. Weather is NOT the cause.
                          ETA drifts past the end of the berth window.
  MV Silver Current    - fuel use up ~9% over 48 h, explained by a deeper draft after loading,
                          not by a fault. Draft is close to the Jebel Ali channel depth (UKC check).
  MV Northern Aurora   - nominal control vessel.

Output (CSV, UTC timestamps): data/clean/{vessels,voyages,telemetry_hourly,alarms}.csv
Usage: python3 scripts/data/generate_gulf_voyages.py [--now 2026-10-22T05:00:00Z] [--out data/clean]
"""
import argparse
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOURS = 48  # history length
JEBEL_ALI = (25.016667, 55.05)
# Approach route (synthetic): northern Arabian Sea -> Gulf of Oman -> Strait of Hormuz -> Jebel Ali
ROUTE = [(10.5, 70.5), (13.5, 67.5), (18.0, 64.5), (21.0, 62.0), (24.2, 58.8), (26.4, 56.5), (25.9, 55.6), JEBEL_ALI]

VESSELS = [
    # vessel_id, name, teu, design_speed_kn, loa_m, beam_m, base_draft_m, mcr_kw
    ("V-MV", "MV Meridian Voyager", 8500, 18.5, 300.0, 48.2, 11.8, 41000),
    ("V-SC", "MV Silver Current", 9200, 18.0, 305.0, 48.4, 11.6, 43000),
    ("V-NA", "MV Northern Aurora", 6800, 19.0, 275.0, 40.0, 11.2, 36000),
]


def haversine_nm(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 3440.065 * math.asin(math.sqrt(d))


LEGS = [haversine_nm(ROUTE[i], ROUTE[i + 1]) for i in range(len(ROUTE) - 1)]
ROUTE_NM = sum(LEGS)


def position_at(dist_to_go_nm):
    """Position along ROUTE given remaining distance to Jebel Ali."""
    along = max(0.0, ROUTE_NM - dist_to_go_nm)
    for i, leg in enumerate(LEGS):
        if along <= leg:
            f = along / leg if leg else 0
            a, b = ROUTE[i], ROUTE[i + 1]
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        along -= leg
    return JEBEL_ALI


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", help="anchor time (UTC, ISO). Default: current hour")
    ap.add_argument("--out", default="data/clean")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    now = (datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now
           else datetime.now(timezone.utc)).replace(minute=0, second=0, microsecond=0)
    rng = random.Random(args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    vessels, voyages, telem, alarms = [], [], [], []

    # remaining distance to Jebel Ali at "now", and berth windows relative to now
    plan = {
        "V-MV": dict(dtg_now=310.0, planned_kn=16.0, win_start_h=18, win_end_h=22),
        "V-SC": dict(dtg_now=420.0, planned_kn=15.5, win_start_h=26, win_end_h=32),
        "V-NA": dict(dtg_now=150.0, planned_kn=15.0, win_start_h=9, win_end_h=13),
    }

    for vid, name, teu, design_kn, loa, beam, base_draft, mcr in VESSELS:
        vessels.append(dict(vessel_id=vid, name=name, vessel_type="Container Vessel", teu_capacity=teu,
                            design_speed_kn=design_kn, loa_m=loa, beam_m=beam, mcr_kw=mcr, data_origin="synthetic"))
        p = plan[vid]
        voyages.append(dict(voyage_id=f"{vid}-2610", vessel_id=vid, destination_unlocode="AEJEA",
                            destination_name="Mina Jabal Ali",
                            berth_window_start_utc=iso(now + timedelta(hours=p["win_start_h"])),
                            berth_window_end_utc=iso(now + timedelta(hours=p["win_end_h"])),
                            planned_speed_kn=p["planned_kn"], status="inbound", data_origin="synthetic"))

        # build the hourly series backwards from "now"
        rows = []
        dtg = p["dtg_now"]
        for h in range(0, HOURS + 1):
            t = now - timedelta(hours=h)
            age = h  # hours before now
            rpm = 72.0 + rng.uniform(-0.6, 0.6)
            draft = base_draft
            stw = p["planned_kn"]
            exh_avg = 335.0
            exh_dev = 3.0
            scav = 42.0
            load = 68.0
            fuel_tph = 2.05

            if vid == "V-MV" and age <= 24:
                s = (24 - age) / 24  # 0 -> 1 as fouling develops
                stw = p["planned_kn"] - 2.8 * s
                exh_avg = 335.0 + 38.0 * s
                exh_dev = 3.0 + 14.0 * s
                scav = 42.0 + 9.0 * s
                load = 68.0 + 6.0 * s
                fuel_tph = 2.05 + 0.12 * s
            if vid == "V-SC":
                draft = base_draft + (0.7 if age <= 40 else 0.0)  # loaded deeper after last port call
                s = 1.0 if age <= 40 else 0.0
                fuel_tph = 2.15 * (1 + 0.09 * s)
                load = 70.0 + 5.0 * s
                stw = p["planned_kn"] - 0.2 * s
            if vid == "V-NA":
                stw = p["planned_kn"]

            stw += rng.uniform(-0.15, 0.15)
            sog = stw + rng.uniform(-0.2, 0.2)  # calm conditions: current/weather effect small
            lat, lon = position_at(dtg)
            rows.append(dict(vessel_id=vid, ts_utc=iso(t), latitude=round(lat, 4), longitude=round(lon, 4),
                             sog_kn=round(sog, 2), stw_kn=round(stw, 2), me_rpm=round(rpm, 1),
                             me_load_pct=round(load + rng.uniform(-0.8, 0.8), 1),
                             fuel_tph=round(fuel_tph + rng.uniform(-0.02, 0.02), 3),
                             exhaust_temp_avg_c=round(exh_avg + rng.uniform(-1.5, 1.5), 1),
                             exhaust_temp_deviation_c=round(exh_dev + rng.uniform(-0.5, 0.5), 1),
                             scavenge_air_temp_c=round(scav + rng.uniform(-0.4, 0.4), 1),
                             draft_m=round(draft, 2), distance_to_go_nm=round(dtg, 1),
                             data_origin="synthetic"))
            dtg += sog  # going back one hour, the vessel was one hour's run further away
        telem.extend(reversed(rows))

    alarms += [
        dict(vessel_id="V-MV", ts_utc=iso(now - timedelta(hours=11)), system="Main Engine",
             code="ME-TC-EFF-LOW", severity="warning",
             message="Turbocharger efficiency below threshold; scavenge air temperature rising", data_origin="synthetic"),
        dict(vessel_id="V-MV", ts_utc=iso(now - timedelta(hours=4)), system="Main Engine",
             code="ME-EXH-DEV-HIGH", severity="warning",
             message="Exhaust temperature deviation across cylinders above 15 C", data_origin="synthetic"),
        dict(vessel_id="V-SC", ts_utc=iso(now - timedelta(hours=40)), system="Cargo",
             code="CARGO-DRAFT-CHANGE", severity="info",
             message="Departure draft increased after loading; trim and draft updated", data_origin="synthetic"),
    ]

    for fname, data in [("vessels.csv", vessels), ("voyages.csv", voyages),
                        ("telemetry_hourly.csv", telem), ("alarms.csv", alarms)]:
        with (out / fname).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
        print(f"Wrote {len(data):>4} rows to {out / fname}")
    print(f"Anchor time (now): {iso(now)}")


if __name__ == "__main__":
    main()
