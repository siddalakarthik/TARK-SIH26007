import {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type {FlagshipParticipant, FlagshipScene} from './types';
import './flagship-map.css';

type Props = {
  scene: FlagshipScene;
  participants: FlagshipParticipant[];
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  compact?: boolean;
  telemetryStale?: boolean;
};
const EMPTY: GeoJSON.FeatureCollection = {type: 'FeatureCollection', features: []};
const COLLECTIONS = ['zones', 'roads', 'route', 'history', 'hazards'] as const;
const MAX_MARKERS = 64;
const STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{id: 'background', type: 'background', paint: {'background-color': '#101e29'}}],
};

export function validPosition(value: unknown): value is [number, number] {
  return Array.isArray(value) && value.length >= 2 && typeof value[0] === 'number' && typeof value[1] === 'number' && Number.isFinite(value[0]) && Number.isFinite(value[1]) && Math.abs(value[0]) <= 180 && Math.abs(value[1]) <= 90;
}

function validGeometry(geometry: GeoJSON.Geometry, budget: {points: number}): boolean {
  if (geometry.type === 'GeometryCollection' || !Array.isArray(geometry.coordinates)) return false;
  const point = (value: unknown) => --budget.points >= 0 && validPosition(value);
  const line = (value: unknown): boolean => Array.isArray(value) && value.length >= 2 && value.length <= 4096 && value.every(point);
  const ring = (value: unknown): boolean => Array.isArray(value) && value.length >= 4 && line(value) && value[0][0] === value[value.length - 1][0] && value[0][1] === value[value.length - 1][1];
  const polygon = (value: unknown): boolean => Array.isArray(value) && value.length > 0 && value.length <= 64 && value.every(ring);
  if (geometry.type === 'Point') return point(geometry.coordinates);
  if (geometry.type === 'LineString') return line(geometry.coordinates);
  if (geometry.type === 'Polygon') return polygon(geometry.coordinates);
  if (geometry.type === 'MultiLineString') return geometry.coordinates.length > 0 && geometry.coordinates.length <= 64 && geometry.coordinates.every(line);
  if (geometry.type === 'MultiPolygon') return geometry.coordinates.length > 0 && geometry.coordinates.length <= 64 && geometry.coordinates.every(polygon);
  return false;
}

/** Keep malformed or unbounded display geometry away from the map renderer. */
export function safeCollection(collection: GeoJSON.FeatureCollection | undefined): GeoJSON.FeatureCollection {
  if (!collection || !Array.isArray(collection.features)) return EMPTY;
  const budget = {points: 10000};
  return {type: 'FeatureCollection', features: collection.features.slice(0, 200).filter(feature => {
    const geometry = feature?.geometry;
    return feature?.type === 'Feature' && geometry && validGeometry(geometry, budget);
  })};
}

export function participantFresh(participant: FlagshipParticipant, telemetryStale = false): boolean {
  return !telemetryStale && ['SIMULATED', 'ONLINE'].includes(participant.state) && typeof participant.age_ms === 'number' && Number.isFinite(participant.age_ms) && participant.age_ms >= 0 && participant.age_ms <= 3000;
}

export function participantDirection(participant: FlagshipParticipant, telemetryStale = false): number | null {
  if (!participantFresh(participant, telemetryStale)) return null;
  const heading = participant.heading_deg;
  if (participant.role !== 'LOCATION_ONLY' && typeof heading === 'number' && Number.isFinite(heading) && heading >= 0 && heading < 360) return heading;
  const course = participant.course_deg;
  return typeof participant.speed_mps === 'number' && participant.speed_mps > 0.05 && typeof course === 'number' && Number.isFinite(course) && course >= 0 && course < 360 ? course : null;
}

function participantPosition(participant: FlagshipParticipant): [number, number] | null {
  if (!participant.position) return null;
  const coordinate = [participant.position.longitude_deg, participant.position.latitude_deg];
  return validPosition(coordinate) ? coordinate : null;
}

function ageLabel(age: number | null): string {
  return typeof age === 'number' && Number.isFinite(age) && age >= 0 ? age < 1000 ? `${Math.round(age)} ms` : `${(age / 1000).toFixed(1)} s` : 'age unknown';
}

function courseBounds(scene: FlagshipScene): [number, number, number, number] | null {
  const b = scene.bounds;
  return Array.isArray(b) && b.length === 4 && validPosition([b[0], b[1]]) && validPosition([b[2], b[3]]) && b[0] < b[2] && b[1] < b[3] ? b : null;
}

function accuracyCollection(participants: FlagshipParticipant[], stale: boolean): GeoJSON.FeatureCollection {
  const features: GeoJSON.Feature[] = [];
  for (const participant of participants.slice(0, MAX_MARKERS)) {
    const point = participantPosition(participant);
    const accuracy = participant.accuracy_m;
    if (!point || !participantFresh(participant, stale) || typeof accuracy !== 'number' || !Number.isFinite(accuracy) || accuracy <= 0 || accuracy > 1000) continue;
    const ring: [number, number][] = [];
    for (let step = 0; step <= 40; step++) {
      const a = step * Math.PI / 20;
      ring.push([point[0] + accuracy * Math.cos(a) / (111320 * Math.max(0.1, Math.cos(point[1] * Math.PI / 180))), point[1] + accuracy * Math.sin(a) / 110540]);
    }
    features.push({type: 'Feature', properties: {participant: participant.id}, geometry: {type: 'Polygon', coordinates: [ring]}});
  }
  return {type: 'FeatureCollection', features};
}

function featureLabel(feature: GeoJSON.Feature): string {
  const label = feature.properties?.name ?? feature.properties?.label ?? feature.properties?.id;
  return typeof label === 'string' ? label.slice(0, 80) : '';
}

/** WebGL-free fallback: uses exactly the supplied geometry; never fetches or invents a map. */
function CourseFallback({scene, participants, selectedId, onSelect, telemetryStale}: Props) {
  const bounds = courseBounds(scene);
  if (!bounds) return <div className="flagship-map-no-geometry">No course geometry available.</div>;
  const project = (point: number[]) => [48 + (point[0] - bounds[0]) / (bounds[2] - bounds[0]) * 704, 430 - (point[1] - bounds[1]) / (bounds[3] - bounds[1]) * 360];
  const path = (coordinates: number[][]) => coordinates.map((point, index) => `${index ? 'L' : 'M'}${project(point).join(',')}`).join(' ');
  return <svg viewBox="0 0 800 500" className="flagship-map-fallback" role="img" aria-label="Offline schematic course; interactive map unavailable">
    <defs><pattern id="flagship-fallback-grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#243542" strokeWidth=".7"/></pattern></defs>
    <rect width="800" height="500" fill="url(#flagship-fallback-grid)"/>
    {safeCollection(scene.zones).features.map((feature, index) => feature.geometry.type === 'Polygon' ? <path key={`z${index}`} d={`${path(feature.geometry.coordinates[0])}Z`} fill="#253d42" stroke="#45605e"/> : null)}
    {safeCollection(scene.roads).features.map((feature, index) => feature.geometry.type === 'LineString' ? <path key={`r${index}`} d={path(feature.geometry.coordinates)} fill="none" stroke="#3e5362" strokeWidth="18" strokeLinejoin="round" strokeLinecap="round"/> : null)}
    {safeCollection(scene.history).features.map((feature, index) => feature.geometry.type === 'LineString' ? <path key={`h${index}`} d={path(feature.geometry.coordinates)} fill="none" stroke="#7ca7b2" strokeWidth="2" strokeDasharray="2 5"/> : null)}
    {safeCollection(scene.route).features.map((feature, index) => feature.geometry.type === 'LineString' ? <path key={`q${index}`} d={path(feature.geometry.coordinates)} fill="none" stroke="#bceba0" strokeWidth="4" strokeLinejoin="round" strokeLinecap="round"/> : null)}
    {safeCollection(scene.hazards).features.map((feature, index) => feature.geometry.type === 'Point' ? <g key={`o${index}`} transform={`translate(${project(feature.geometry.coordinates).join(',')})`}><circle r="7" fill="#e5b86d" stroke="#101e29" strokeWidth="3"/><title>{featureLabel(feature)}</title></g> : null)}
    {safeCollection(scene.waypoints).features.map((feature, index) => feature.geometry.type === 'Point' ? <g key={`w${index}`} transform={`translate(${project(feature.geometry.coordinates).join(',')})`}><circle r="4" fill="#c5d4d9"/><text y="-12" textAnchor="middle" fill="#ccdadd" fontSize="12">{featureLabel(feature)}</text></g> : null)}
    {participants.slice(0, MAX_MARKERS).map(participant => {const point = participantPosition(participant); if (!point) return null; const fresh = participantFresh(participant, telemetryStale); return <g key={participant.id} transform={`translate(${project(point).join(',')})`} role="button" tabIndex={0} aria-label={`Select ${participant.name}, ${fresh ? 'fresh' : 'last-known location'}`} onClick={() => onSelect?.(participant.id)} onKeyDown={event => {if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); onSelect?.(participant.id);}}}><circle r={selectedId === participant.id ? 16 : 13} fill={fresh ? participant.role === 'LOCATION_ONLY' ? '#e5b86d' : '#bceba0' : '#8895a0'} stroke="#101e29" strokeWidth="3"/><text textAnchor="middle" y="5" fill="#101e29" fontSize="13" fontWeight="700">{participant.id}</text></g>;})}
  </svg>;
}

export default function FlagshipMap(props: Props) {
  const {scene, participants, selectedId, compact = false, telemetryStale = false} = props;
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const latest = useRef(props);
  latest.current = props;
  const markers = useRef(new Map<string, maplibregl.Marker>());
  const placeMarkers = useRef<maplibregl.Marker[]>([]);
  const sceneId = useRef('');
  const follow = useRef(false);
  const [following, setFollowing] = useState(false);
  const [state, setState] = useState<'LOADING' | 'READY' | 'FALLBACK'>('LOADING');

  const fitCourse = useCallback(() => {
    const bounds = courseBounds(latest.current.scene);
    if (bounds && map.current) map.current.fitBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]], {padding: {top: 78, bottom: 76, left: 44, right: 44}, maxZoom: 19, duration: 450});
    follow.current = false;
    setFollowing(false);
  }, []);

  useEffect(() => {
    if (!container.current || map.current) return;
    setState('LOADING');
    let instance: maplibregl.Map;
    let observer: ResizeObserver | undefined;
    let disposed = false;
    const stopFollow = () => {follow.current = false; setFollowing(false);};
    const onError = () => {if (!disposed) setState('FALLBACK');};
    try {
      instance = new maplibregl.Map({container: container.current, style: STYLE, center: validPosition(latest.current.scene.center) ? latest.current.scene.center : [0, 0], zoom: 16, maxZoom: 22, attributionControl: false, pitchWithRotate: false, dragRotate: false});
      map.current = instance;
      instance.addControl(new maplibregl.NavigationControl({showCompass: true, visualizePitch: false}), 'top-right');
      instance.addControl(new maplibregl.ScaleControl({maxWidth: 90, unit: 'metric'}), 'bottom-left');
      instance.on('dragstart', stopFollow);
      instance.on('error', onError);
      const initialize = () => {
        if (disposed) return;
        for (const id of [...COLLECTIONS, 'accuracy']) instance.addSource(`flagship-${id}`, {type: 'geojson', data: EMPTY});
        instance.addLayer({id: 'flagship-zone-fill', type: 'fill', source: 'flagship-zones', paint: {'fill-color': '#28443c', 'fill-opacity': 0.65}});
        instance.addLayer({id: 'flagship-zone-edge', type: 'line', source: 'flagship-zones', paint: {'line-color': '#4f6b58', 'line-width': 1, 'line-dasharray': [3, 3]}});
        instance.addLayer({id: 'flagship-road-edge', type: 'line', source: 'flagship-roads', layout: {'line-join': 'round', 'line-cap': 'round'}, paint: {'line-color': '#496070', 'line-width': ['interpolate', ['linear'], ['zoom'], 14, 8, 18, 26, 21, 58]}});
        instance.addLayer({id: 'flagship-road-fill', type: 'line', source: 'flagship-roads', layout: {'line-join': 'round', 'line-cap': 'round'}, paint: {'line-color': '#273e4e', 'line-width': ['interpolate', ['linear'], ['zoom'], 14, 5, 18, 22, 21, 52]}});
        instance.addLayer({id: 'flagship-road-centre', type: 'line', source: 'flagship-roads', paint: {'line-color': '#6d8592', 'line-width': 1, 'line-dasharray': [4, 5], 'line-opacity': 0.6}});
        instance.addLayer({id: 'flagship-history-line', type: 'line', source: 'flagship-history', paint: {'line-color': '#7ca7b2', 'line-width': 2, 'line-dasharray': [1, 3], 'line-opacity': 0.65}});
        instance.addLayer({id: 'flagship-route-shadow', type: 'line', source: 'flagship-route', layout: {'line-cap': 'round', 'line-join': 'round'}, paint: {'line-color': '#bceba0', 'line-width': 12, 'line-opacity': 0.09}});
        instance.addLayer({id: 'flagship-route-line', type: 'line', source: 'flagship-route', layout: {'line-cap': 'round', 'line-join': 'round'}, paint: {'line-color': '#bceba0', 'line-width': 3.5, 'line-opacity': 0.95}});
        instance.addLayer({id: 'flagship-accuracy-fill', type: 'fill', source: 'flagship-accuracy', paint: {'fill-color': '#bceba0', 'fill-opacity': 0.1}});
        instance.addLayer({id: 'flagship-accuracy-edge', type: 'line', source: 'flagship-accuracy', paint: {'line-color': '#bceba0', 'line-width': 1, 'line-opacity': 0.45}});
        instance.addLayer({id: 'flagship-hazard-circle', type: 'circle', source: 'flagship-hazards', paint: {'circle-color': '#e5b86d', 'circle-radius': 7, 'circle-stroke-color': '#101e29', 'circle-stroke-width': 3}});
        fitCourse();
        setState('READY');
      };
      if (instance.isStyleLoaded()) initialize(); else instance.once('load', initialize);
      if (typeof ResizeObserver !== 'undefined') {
        observer = new ResizeObserver(() => {
          if (disposed) return;
          instance.resize();
          // Keep the whole supplied course readable when a laptop becomes a phone
          // layout; a deliberate follow view retains its active vehicle instead.
          if (!follow.current) fitCourse();
        });
        observer.observe(container.current);
      }
    } catch {setState('FALLBACK');}
    return () => {
      disposed = true;
      observer?.disconnect();
      markers.current.forEach(marker => marker.remove()); markers.current.clear();
      placeMarkers.current.forEach(marker => marker.remove()); placeMarkers.current = [];
      sceneId.current = '';
      if (container.current) delete container.current.dataset.labels;
      if (map.current) {map.current.off('dragstart', stopFollow); map.current.off('error', onError); map.current.remove(); map.current = null;}
    };
  }, [fitCourse]);

  useEffect(() => {
    const instance = map.current;
    if (!instance || state !== 'READY') return;
    for (const id of COLLECTIONS) (instance.getSource(`flagship-${id}`) as maplibregl.GeoJSONSource | undefined)?.setData(safeCollection(scene[id]));
    (instance.getSource('flagship-accuracy') as maplibregl.GeoJSONSource | undefined)?.setData(accuracyCollection(participants, telemetryStale));
    if (sceneId.current !== scene.id) {
      sceneId.current = scene.id;
      fitCourse();
    }
    // Rebuild the small static place-label collection only when its serialized content changes.
    const labels = safeCollection(scene.waypoints).features.filter(feature => feature.geometry.type === 'Point').slice(0, 32);
    const labelKey = JSON.stringify(labels);
    if (container.current?.dataset.labels !== labelKey) {
      if (container.current) container.current.dataset.labels = labelKey;
      placeMarkers.current.forEach(marker => marker.remove());
      placeMarkers.current = labels.flatMap(feature => {
        if (feature.geometry.type !== 'Point') return [];
        const element = document.createElement('div'); element.className = 'flagship-place-label'; element.textContent = featureLabel(feature);
        return [new maplibregl.Marker({element, anchor: 'bottom', offset: [0, -12]}).setLngLat(feature.geometry.coordinates as [number, number]).addTo(instance)];
      });
    }
    const active = new Set<string>();
    for (const participant of participants.slice(0, MAX_MARKERS)) {
      const position = participantPosition(participant);
      if (!position || active.has(participant.id)) continue;
      active.add(participant.id);
      let marker = markers.current.get(participant.id);
      if (!marker) {
        const button = document.createElement('button'); button.type = 'button'; button.className = 'flagship-participant-marker';
        const direction = document.createElement('span'); direction.className = 'flagship-marker-direction'; direction.setAttribute('aria-hidden', 'true');
        const identity = document.createElement('span'); identity.className = 'flagship-marker-identity'; identity.textContent = participant.id;
        const label = document.createElement('span'); label.className = 'flagship-marker-label';
        button.append(direction, identity, label); button.addEventListener('click', () => latest.current.onSelect?.(participant.id));
        marker = new maplibregl.Marker({element: button, anchor: 'center'}).setLngLat(position).addTo(instance);
        markers.current.set(participant.id, marker);
      }
      const fresh = participantFresh(participant, telemetryStale), direction = participantDirection(participant, telemetryStale);
      marker.setLngLat(position);
      const button = marker.getElement();
      button.dataset.role = participant.role;
      button.dataset.fresh = String(fresh);
      button.dataset.selected = String(selectedId === participant.id);
      button.setAttribute('aria-label', `Select ${participant.name}; ${participant.role === 'LOCATION_ONLY' ? 'location-only participant' : 'instrumented vehicle'}; ${fresh ? 'fresh' : 'last-known location'}; ${ageLabel(participant.age_ms)}; ${participant.source_mode}`);
      button.setAttribute('aria-pressed', String(selectedId === participant.id));
      const arrow = button.querySelector<HTMLElement>('.flagship-marker-direction');
      if (arrow) {arrow.hidden = direction === null; arrow.style.transform = direction === null ? 'none' : `rotate(${direction}deg)`;}
      const label = button.querySelector<HTMLElement>('.flagship-marker-label');
      if (label) label.textContent = `${participant.name}${fresh ? '' : ' · LAST KNOWN'}`;
    }
    for (const [id, marker] of markers.current) if (!active.has(id)) {marker.remove(); markers.current.delete(id);}
    const vehicleA = participants.find(participant => participant.id === 'A');
    if (follow.current && vehicleA && participantFresh(vehicleA, telemetryStale)) {
      const position = participantPosition(vehicleA); if (position) instance.easeTo({center: position, duration: 300});
    } else if (follow.current) {follow.current = false; setFollowing(false);}
  }, [scene, participants, selectedId, telemetryStale, state, fitCourse]);

  const vehicleA = participants.find(participant => participant.id === 'A');
  const canFollow = !!vehicleA && !!participantPosition(vehicleA) && participantFresh(vehicleA, telemetryStale);
  const markersAvailable = useMemo(() => participants.filter(participant => participantPosition(participant)).length, [participants]);
  const startFollowing = () => {
    if (!vehicleA || !canFollow || !map.current) return;
    follow.current = !follow.current; setFollowing(follow.current);
    const position = participantPosition(vehicleA);
    if (follow.current && position) map.current.easeTo({center: position, duration: 450});
  };

  return <section className={`flagship-map${compact ? ' flagship-map--compact' : ''}`} aria-label="Fleet demonstration map">
    <div className="flagship-map-canvas" ref={container} aria-label="Interactive schematic course"/>
    {state === 'FALLBACK' && <CourseFallback {...props}/>}
    <div className="flagship-map-title"><span className="flagship-map-live-dot"/><div><strong>{scene.source === 'SIMULATION' ? 'SIMULATION · DEMO COURSE' : 'LOCATION UNAVAILABLE'}</strong><small>{scene.source === 'SIMULATION' ? 'Schematic course · not a surveyed mine' : 'No live participant position supplied'}</small></div></div>
    <div className="flagship-map-toolbar" aria-label="Map controls">
      <button type="button" aria-label="Fit entire course" onClick={fitCourse} disabled={state !== 'READY'} title="Fit entire course">⛶<span>Course</span></button>
      <button type="button" aria-label="Follow Vehicle A" aria-pressed={following} onClick={startFollowing} disabled={!canFollow || state !== 'READY'} title="Follow Vehicle A">◎<span>Follow A</span></button>
      <button type="button" aria-label="Orient map north up" onClick={() => map.current?.easeTo({bearing: 0, pitch: 0, duration: 400})} disabled={state !== 'READY'} title="North up">↑<span>North</span></button>
    </div>
    {state === 'LOADING' && <div className="flagship-map-message" role="status">Opening offline course…</div>}
    {state === 'FALLBACK' && <div className="flagship-map-render-note" role="status">Schematic fallback · interactive map unavailable</div>}
    {(telemetryStale || markersAvailable === 0) && <div className="flagship-map-message" role="status">{telemetryStale ? 'TELEMETRY STALE · markers are last-known positions' : 'No vehicle location available · no position invented'}</div>}
    <div className="flagship-map-legend" aria-label="Map legend"><span><i className="legend-a"/>Vehicle A</span><span><i className="legend-b"/>Node B · location only</span><span><i className="legend-route"/>Demo route</span><span><i className="legend-history"/>History</span></div>
    <div className="flagship-map-footnote">Synthetic coordinates · no live-site guidance · radar stays vehicle-relative</div>
  </section>;
}
