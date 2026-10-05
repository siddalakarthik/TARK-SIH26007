/** Presentation-only flagship contracts. Synthetic course is never a surveyed mine map. */
export type FlagshipParticipant = {
  id: string;
  name: string;
  role: 'INSTRUMENTED_VEHICLE' | 'LOCATION_ONLY';
  source_mode: string;
  state: string;
  position: {longitude_deg: number; latitude_deg: number} | null;
  speed_mps: number | null;
  course_deg: number | null;
  heading_deg: number | null;
  accuracy_m: number | null;
  age_ms: number | null;
  timestamp_ns: number | null;
  quality: string;
  capabilities: string[];
};

export type FlagshipScene = {
  id: string;
  label: string;
  source: string;
  coordinate_system: 'WGS84_DISPLAY_ANCHOR_ONLY';
  center: [number, number];
  bounds: [number, number, number, number];
  review_status: string;
  roads: GeoJSON.FeatureCollection;
  route: GeoJSON.FeatureCollection;
  zones: GeoJSON.FeatureCollection;
  waypoints: GeoJSON.FeatureCollection;
  hazards: GeoJSON.FeatureCollection;
  history: GeoJSON.FeatureCollection;
};

export type FlagshipHardware = {
  id: string;
  name: string;
  interface: string;
  status: string;
  software_readiness: string;
  reason: string;
};

export type FlagshipSnapshot = {
  schema_version: 'tark.flagship.v1';
  mode: string;
  source_mode: string;
  timestamp_ns: number;
  sequence: number;
  traction: 'DISABLED_PHASE_1';
  monitoring_only: true;
  hardware_verified: false;
  scene: FlagshipScene;
  participants: FlagshipParticipant[];
  hardware: FlagshipHardware[];
  limitations: string[];
};
