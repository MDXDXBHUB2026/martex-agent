-- Live marine weather from Open-Meteo Marine API (free non-commercial use; data CC BY 4.0, attribution required).
-- Run each statement separately in Zetaris SQL Workspace. No credentials needed.
-- Note: container name "martex" was rejected (Bad Request); "martex_views" works.

CREATE LIGHTNING DATABASE MARTEX_REST DESCRIBE BY "MARTEX_live_REST_sources";

CREATE SCHEMASTORE CONTAINER martex_views;

CREATE LIGHTNING REST TABLE marine_hormuz FROM MARTEX_REST REQUEST(endpoint "https://marine-api.open-meteo.com/v1/marine?latitude=26.3&longitude=56.4&hourly=wave_height,wave_direction,wave_period,swell_wave_height&forecast_days=3", method "get", response_type "json", http_encoding "URLENCODED") HEADER () BODY ();

-- Turn the parallel hourly arrays into one row per hour.
CREATE SCHEMASTORE VIEW marine_hormuz_hourly WITH CONTAINER martex_views AS SELECT 'HORMUZ' AS waypoint_id, latitude, longitude, ts AS time_utc, hourly.wave_height[pos] AS wave_height_m, hourly.swell_wave_height[pos] AS swell_height_m, hourly.wave_period[pos] AS wave_period_s, hourly.wave_direction[pos] AS wave_direction_deg FROM martex_rest.marine_hormuz LATERAL VIEW posexplode(hourly.time) t AS pos, ts;

-- Verify
SELECT time_utc, wave_height_m, swell_height_m, wave_period_s FROM martex_views.marine_hormuz_hourly ORDER BY wave_height_m DESC LIMIT 5;
