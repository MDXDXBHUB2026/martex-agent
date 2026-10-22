-- Federated view across all three MARTEX sources:
--   MARTEX_OPS (operator Postgres: vessels, voyages, telemetry_hourly, port_index from NGA WPI)
--   martex_views.marine_hormuz_hourly (live Open-Meteo marine forecast)
-- Note: the "latest reading" filter must be in WHERE; a subquery inside JOIN ... ON returned Bad Request.
-- Typical query time on the 6 GB local setup: 8-13 s.

CREATE SCHEMASTORE VIEW voyage_risk_context WITH CONTAINER martex_views AS SELECT v.name AS vessel_name, p.port_name, p.channel_depth_m, t.draft_m, round(p.channel_depth_m - t.draft_m, 2) AS channel_ukc_m, round(t.distance_to_go_nm / t.sog_kn, 2) AS hours_to_go, from_unixtime(unix_timestamp(t.ts_utc) + cast(t.distance_to_go_nm / t.sog_kn * 3600 AS bigint)) AS eta_utc, y.berth_window_end_utc, w.max_wave_height_m FROM MARTEX_OPS.vessels v JOIN MARTEX_OPS.voyages y ON y.vessel_id = v.vessel_id JOIN MARTEX_OPS.telemetry_hourly t ON t.vessel_id = v.vessel_id LEFT JOIN MARTEX_OPS.port_index p ON p.unlocode = y.destination_unlocode CROSS JOIN (SELECT max(wave_height_m) AS max_wave_height_m FROM martex_views.marine_hormuz_hourly) w WHERE t.ts_utc = (SELECT max(ts_utc) FROM MARTEX_OPS.telemetry_hourly);

-- Verify (expect 3 rows; MV Meridian Voyager ETA after berth_window_end_utc)
SELECT vessel_name, hours_to_go, eta_utc, berth_window_end_utc, channel_ukc_m, max_wave_height_m FROM martex_views.voyage_risk_context;
