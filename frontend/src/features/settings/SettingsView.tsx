import type {ConnectionState} from '../../api';
import {resolveMapProvider,resolveMapStyle} from '../../mapConfig';
import {Panel} from '../../components/Panel';

export type DiagnosticsData={software_version:string;firmware_version:string;protocol_version:number;configuration_hash:string;mode:string;phase_2_hardware:string;deployment_environment?:string;auth_mode?:string;map?:{longitude:number;latitude:number;zoom:number;location_configured:boolean;location_status:string};capabilities?:{browser_device_location:boolean;browser_camera_preview:boolean}};

function Row({label,value}:{label:string;value:string|number}){return <div className="settings-row"><dt>{label}</dt><dd>{value}</dd></div>}

export function SettingsView({diagnostics,connection,lastTelemetry}:{diagnostics:DiagnosticsData|null;connection:ConnectionState;lastTelemetry:number|null}){
  const map=diagnostics?.map;
  return <main className="settings-grid" aria-label="TARK settings">
    <Panel title="System"><dl><Row label="Environment" value={diagnostics?.deployment_environment??'UNAVAILABLE'}/><Row label="Software version" value={diagnostics?.software_version??'UNAVAILABLE'}/><Row label="Firmware version" value={diagnostics?.firmware_version??'UNAVAILABLE'}/><Row label="Protocol version" value={diagnostics?.protocol_version??'UNAVAILABLE'}/><Row label="Configuration" value={diagnostics?.configuration_hash??'UNAVAILABLE'}/><Row label="Mode" value={diagnostics?.mode??'UNAVAILABLE'}/><Row label="Phase 2 hardware" value={diagnostics?.phase_2_hardware??'NOT CONNECTED'}/><Row label="Traction" value="DISABLED_PHASE_1"/></dl></Panel>
    <Panel title="Map"><dl><Row label="Provider" value={resolveMapProvider()}/><Row label="Style" value={resolveMapStyle()}/><Row label="Location" value={map?.location_configured?`${map.longitude}, ${map.latitude}`:'INDIA OVERVIEW — no vehicle location configured'}/><Row label="Default zoom" value={map?.zoom??'UNAVAILABLE'}/><Row label="Routing" value="NOT CONNECTED"/></dl><p>Map provider configuration is display-only. No external URL or secret can be changed from the HMI.</p></Panel>
    <Panel title="Display"><dl><Row label="Density" value="Comfortable (release default)"/><Row label="Map labels" value="Provider controlled"/><Row label="Telemetry display" value="Backend authoritative"/><Row label="Device location" value="User-request only; local browser data"/><Row label="Browser camera preview" value={diagnostics?.capabilities?.browser_camera_preview?'Enabled development capability':'Disabled by default'}/></dl><p>Display preferences never alter safety logic, simulation mode, or traction state.</p></Panel>
    <Panel title="Connection"><dl><Row label="REST status" value={diagnostics?'AVAILABLE':'UNAVAILABLE'}/><Row label="WebSocket" value={connection}/><Row label="Telemetry freshness" value={connection==='CONNECTED'?'CURRENT':'UNAVAILABLE'}/><Row label="Last browser receipt" value={lastTelemetry?new Date(lastTelemetry).toLocaleTimeString():'NOT RECEIVED'}/><Row label="Authentication mode" value={diagnostics?.auth_mode??'UNAVAILABLE'}/></dl><p>Connection state is monitoring information only; it grants no vehicle authority.</p></Panel>
    <Panel title="Simulation"><p><strong>{diagnostics?.mode??'SIMULATION'}</strong> — backend authoritative and read-only in this HMI.</p><p>Hardware mode cannot be selected in the browser. Traction stays disabled in Phase 1.</p></Panel>
    <Panel title="About"><p><strong>TARK SIH26007</strong></p><p>Research Prototype · Not Physically Validated</p><p>Browser: monitoring only. Physical E-stop: independent.</p></Panel>
  </main>;
}
