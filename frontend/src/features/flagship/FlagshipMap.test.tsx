import '@testing-library/jest-dom/vitest';
import {StrictMode} from 'react';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import {afterEach, beforeEach, expect, test, vi} from 'vitest';
import FlagshipMap, {participantDirection, participantFresh, safeCollection, validPosition} from './FlagshipMap';
import type {FlagshipParticipant, FlagshipScene} from './types';

const fixture = vi.hoisted(() => ({maps: [] as any[], markers: [] as any[], observers: [] as (() => void)[], fail: false, loaded: true, disconnected: 0}));
vi.mock('maplibre-gl', () => ({default: {
  Map: class {
    sources: Record<string, any> = {}; layers: any[] = []; options: any; handlers: Record<string, () => void> = {}; removed = false;
    fitBounds = vi.fn(); easeTo = vi.fn(); resize = vi.fn();
    constructor(options: any) {if (fixture.fail) throw new Error('WebGL unavailable'); this.options = options; fixture.maps.push(this);}
    addControl() {} on(name: string, fn: () => void) {this.handlers[name] = fn;} once(name: string, fn: () => void) {this.handlers[name] = fn;} off(name: string) {delete this.handlers[name];}
    isStyleLoaded() {return fixture.loaded;} remove() {this.removed = true;}
    getSource(id: string) {return this.sources[id];}
    addSource(id: string, source: any) {this.sources[id] = {data: source.data, setData: vi.fn(function(this: any, data: any) {this.data = data;})};}
    addLayer(layer: any) {this.layers.push(layer);}
  },
  Marker: class {
    element: HTMLElement; removed = false; position: number[] = [];
    constructor(options: any) {this.element = options.element; fixture.markers.push(this);}
    setLngLat(value: number[]) {this.position = value; return this;} addTo() {return this;} getElement() {return this.element;} remove() {this.removed = true;}
  }, NavigationControl: class {}, ScaleControl: class {},
}}));
const empty: GeoJSON.FeatureCollection = {type: 'FeatureCollection', features: []};
const collection = (geometry: GeoJSON.Geometry, label = 'Fixture'): GeoJSON.FeatureCollection => ({type: 'FeatureCollection', features: [{type: 'Feature', properties: {label}, geometry}]});
const scene: FlagshipScene = {
  id: 'demo', label: 'Synthetic course', source: 'SIMULATION', coordinate_system: 'WGS84_DISPLAY_ANCHOR_ONLY',
  center: [78, 17], bounds: [77.99, 16.99, 78.01, 17.01], review_status: 'NOT_SURVEYED',
  roads: collection({type: 'LineString', coordinates: [[78, 17], [78.001, 17.001]]}),
  route: collection({type: 'LineString', coordinates: [[78, 17], [78.001, 17.001]]}),
  zones: empty, hazards: collection({type: 'Point', coordinates: [78.002, 17]}, 'Synthetic obstacle'),
  history: collection({type: 'LineString', coordinates: [[78, 17], [78.001, 17.001]]}),
  waypoints: collection({type: 'Point', coordinates: [78, 17]}, 'Loading point'),
};
const vehicle: FlagshipParticipant = {id: 'A', name: 'Vehicle A', role: 'INSTRUMENTED_VEHICLE', source_mode: 'SIMULATION', state: 'SIMULATED', position: {longitude_deg: 78, latitude_deg: 17}, speed_mps: .8, course_deg: 90, heading_deg: null, accuracy_m: 3, age_ms: 20, timestamp_ns: 123, quality: 'SIMULATED_FIX', capabilities: ['GNSS']};
beforeEach(() => {fixture.maps.length = 0; fixture.markers.length = 0; fixture.observers.length = 0; fixture.fail = false; fixture.loaded = true; fixture.disconnected = 0; vi.stubGlobal('ResizeObserver', class {constructor(callback: () => void) {fixture.observers.push(callback);} observe() {} disconnect() {fixture.disconnected++;}});});
afterEach(() => {cleanup(); vi.unstubAllGlobals();});

test('one offline map instance updates supplied layers and markers without remount', () => {
  const onSelect = vi.fn();
  const view = render(<FlagshipMap scene={scene} participants={[vehicle]} onSelect={onSelect}/>);
  const map = fixture.maps[0];
  expect(fixture.maps).toHaveLength(1);
  expect(map.options.style.sources).toEqual({});
  expect(map.options.style.glyphs).toBeUndefined();
  expect(map.options.style.sprite).toBeUndefined();
  expect(map.layers.some((layer: any) => layer.id === 'flagship-hazard-circle')).toBe(true);
  expect(map.sources['flagship-route'].data).toEqual(scene.route);
  expect(map.sources['flagship-history'].data).toEqual(scene.history);
  expect(map.sources['flagship-accuracy'].data.features).toHaveLength(1);
  const marker = fixture.markers.find(item => item.element.className === 'flagship-participant-marker');
  fireEvent.click(marker.element); expect(onSelect).toHaveBeenCalledWith('A');
  for (let i = 0; i < 5; i++) view.rerender(<FlagshipMap scene={scene} participants={[{...vehicle, position: {longitude_deg: 78.001 + i * .001, latitude_deg: 17}}]}/>);
  expect(fixture.maps).toHaveLength(1);
  expect(fixture.markers.filter(item => item.element.className === 'flagship-participant-marker')).toHaveLength(1);
  expect(marker.position[0]).toBeCloseTo(78.005);
  expect(screen.getByText('SIMULATION · DEMO COURSE')).toBeInTheDocument();
  expect(screen.getByText('Synthetic coordinates · no live-site guidance · radar stays vehicle-relative')).toBeInTheDocument();
  view.unmount(); expect(map.removed).toBe(true); expect(fixture.markers.every(item => item.removed)).toBe(true); expect(fixture.disconnected).toBe(1);
});

test('stale telemetry keeps last-known markers, clears uncertainty circles and stops following', () => {
  const view = render(<FlagshipMap scene={scene} participants={[vehicle]}/>);
  fireEvent.click(screen.getByRole('button', {name: 'Follow Vehicle A'}));
  expect(screen.getByRole('button', {name: 'Follow Vehicle A'})).toHaveAttribute('aria-pressed', 'true');
  view.rerender(<FlagshipMap scene={scene} participants={[vehicle]} telemetryStale/>);
  const marker = fixture.markers.find(item => item.element.className === 'flagship-participant-marker');
  expect(marker.element.dataset.fresh).toBe('false');
  expect(marker.element.getAttribute('aria-label')).toContain('last-known location');
  expect(marker.element.querySelector('.flagship-marker-direction')).toHaveAttribute('hidden');
  expect(fixture.maps[0].sources['flagship-accuracy'].data.features).toEqual([]);
  expect(screen.getByRole('button', {name: 'Follow Vehicle A'})).toBeDisabled();
  expect(screen.getByRole('button', {name: 'Follow Vehicle A'})).toHaveAttribute('aria-pressed', 'false');
  view.rerender(<FlagshipMap scene={scene} participants={[]}/>);
  expect(marker.removed).toBe(true);
  expect(screen.getByText('No vehicle location available · no position invented')).toBeInTheDocument();
});

test('StrictMode releases the first map and recreates static labels for the active map', () => {
  const view = render(<StrictMode><FlagshipMap scene={scene} participants={[vehicle]}/></StrictMode>);
  expect(fixture.maps.filter(item => !item.removed)).toHaveLength(1);
  expect(fixture.markers.filter(item => !item.removed && item.element.className === 'flagship-place-label')).toHaveLength(1);
  view.unmount(); expect(fixture.maps.every(item => item.removed)).toBe(true);
});

test('container resize refits the course without creating a map or cancelling active follow', () => {
  const view = render(<FlagshipMap scene={scene} participants={[vehicle]}/>);
  const map = fixture.maps[0];
  map.fitBounds.mockClear();
  fixture.observers[0]();
  expect(map.resize).toHaveBeenCalledTimes(1);
  expect(map.fitBounds).toHaveBeenCalledTimes(1);
  expect(fixture.maps).toHaveLength(1);
  fireEvent.click(screen.getByRole('button', {name: 'Follow Vehicle A'}));
  fixture.observers[0]();
  expect(map.resize).toHaveBeenCalledTimes(2);
  expect(map.fitBounds).toHaveBeenCalledTimes(1);
  expect(screen.getByRole('button', {name: 'Follow Vehicle A'})).toHaveAttribute('aria-pressed', 'true');
  view.unmount();
  fixture.observers[0]();
  expect(map.resize).toHaveBeenCalledTimes(2);
});

test('no-WebGL fallback uses supplied course and supports accessible participant selection', () => {
  fixture.fail = true; const onSelect = vi.fn();
  render(<FlagshipMap scene={scene} participants={[vehicle]} onSelect={onSelect}/>);
  expect(screen.getByRole('img', {name: 'Offline schematic course; interactive map unavailable'})).toBeInTheDocument();
  expect(screen.getByText('Schematic fallback · interactive map unavailable')).toBeInTheDocument();
  expect(screen.getByText('Loading point')).toBeInTheDocument();
  expect(screen.getByText('Synthetic obstacle')).toBeInTheDocument();
  fireEvent.keyDown(screen.getByRole('button', {name: 'Select Vehicle A, fresh'}), {key: 'Enter'});
  expect(onSelect).toHaveBeenCalledWith('A');
  expect(screen.getByRole('button', {name: 'Follow Vehicle A'})).toBeDisabled();
});

test('unavailable mode never calls its geometry a live site or location fix', () => {
  render(<FlagshipMap scene={{...scene, source: 'UNAVAILABLE', roads: empty, route: empty}} participants={[]}/>);
  expect(screen.getByText('LOCATION UNAVAILABLE')).toBeInTheDocument();
  expect(screen.getByText('No live participant position supplied')).toBeInTheDocument();
  expect(fixture.maps[0].sources['flagship-route'].data.features).toEqual([]);
});

test.each([null, NaN, Infinity, -1, 3001])('invalid/old observation age %j cannot appear fresh', age_ms => {
  expect(participantFresh({...vehicle, age_ms})).toBe(false);
  expect(participantDirection({...vehicle, age_ms})).toBeNull();
});
test('unknown receiver state and stationary location-only heading cannot imply known direction', () => {
  expect(participantFresh({...vehicle, state: 'SEARCHING'})).toBe(false);
  expect(participantDirection({...vehicle, role: 'LOCATION_ONLY', heading_deg: 90, speed_mps: 0})).toBeNull();
  expect(participantDirection({...vehicle, role: 'LOCATION_ONLY', course_deg: 120})).toBe(120);
});

test('malformed geometry is rejected and display collections are bounded', () => {
  expect(validPosition([Infinity, 17])).toBe(false); expect(validPosition([78, 91])).toBe(false);
  for (const geometry of [{type: 'LineString', coordinates: [[78, 17]]}, {type: 'Polygon', coordinates: [[[78, 17], [78, 18], [79, 18], [79, 17]]]}, {type: 'MultiPolygon', coordinates: null}, {type: 'Point', coordinates: [NaN, 17]}]) {
    expect(safeCollection(collection(geometry as GeoJSON.Geometry)).features).toEqual([]);
  }
  expect(safeCollection({type: 'FeatureCollection', features: Array(500).fill(scene.hazards.features[0])}).features).toHaveLength(200);
});
