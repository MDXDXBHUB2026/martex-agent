CREATE TABLE port_index (
  wpi_number numeric, port_name text, alt_port_name text, unlocode text, country text,
  water_body text, latitude numeric, longitude numeric, tidal_range_m numeric,
  entrance_width_m numeric, channel_depth_m numeric, anchorage_depth_m numeric,
  cargo_pier_depth_m numeric, max_vessel_length_m numeric, max_vessel_beam_m numeric,
  max_vessel_draft_m numeric, harbor_size text, harbor_type text, shelter text,
  restriction_tide text, restriction_heavy_swell text, restriction_other text,
  overhead_limits text, ukc_management text, eta_message_required text,
  pilotage_compulsory text, tugs_assistance text, vessel_traffic_service text,
  facility_container text, cranes_container text, supply_fuel_oil text, repairs text
);
COPY port_index FROM '/seed/ports_region.csv' WITH (FORMAT csv, HEADER true);
