import {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import {ApiError, calculateRoute, reverseGeocode, type AddressHierarchy, type GeographicPoint, type RouteResult, type VehicleLocationStatus} from './api';
import {resolveMapFallbackStyle,resolveMapProvider, resolveMapStyle} from './mapConfig';
import {radarLocalPoint,validAccuracy,validHeading,vehicleLocationLabel,vehicleLocationStatusLabel} from './mapUtils';
import type {Snapshot} from './types';

const INDIA={longitude:78.9629,latitude:20.5937,zoom:4.2};
const WORLD={longitude:0,latitude:20,zoom:1.5};
const INDIA_VIEW=INDIA;
type DeviceLocation={latitude:number;longitude:number;accuracy:number;timestamp:number};

function pointFromText(value:string):GeographicPoint|null{
  const [latText,lonText,...rest]=value.split(',').map(part=>part.trim());
  const latitude=Number(latText),longitude=Number(lonText);
  return rest.length===0&&Number.isFinite(latitude)&&Number.isFinite(longitude)&&latitude>=-90&&latitude<=90&&longitude>=-180&&longitude<=180?{latitude,longitude}:null;
}
function coordinateText(point:GeographicPoint|DeviceLocation):string{return `${point.latitude.toFixed(6)}, ${point.longitude.toFixed(6)}`;}
function addressText(address:AddressHierarchy|null):string{
  if(!address)return 'ADDRESS NOT RESOLVED';
  return [address.road,address.locality,address.city,address.district,address.state,address.country].filter(Boolean).join(', ')||address.display_name||'ADDRESS UNAVAILABLE';
}
function accuracyRing(location:DeviceLocation):GeoJSON.Feature<GeoJSON.Polygon>{
  const points:[number,number][]=[];
  const radius=Math.max(1,location.accuracy),latitudeRadians=location.latitude*Math.PI/180;
  for(let step=0;step<=32;step+=1){const angle=2*Math.PI*step/32;points.push([location.longitude+(radius*Math.cos(angle))/(111_320*Math.max(0.1,Math.cos(latitudeRadians))),location.latitude+(radius*Math.sin(angle))/110_540]);}
  return {type:'Feature',properties:{accuracy_m:location.accuracy},geometry:{type:'Polygon',coordinates:[points]}};
}
function vehicleAccuracyRing(location:NonNullable<VehicleLocationStatus['location']>):GeoJSON.Feature<GeoJSON.Polygon>{
  return accuracyRing({latitude:location.latitude_deg,longitude:location.longitude_deg,accuracy:location.horizontal_accuracy_m as number,timestamp:location.timestamp_ns});
}

type MapConfiguration={longitude:number;latitude:number;zoom:number;location_configured:boolean;location_status:string};
export default function MapView({snapshot,vehicleLocation,mapConfig}:{snapshot:Snapshot;vehicleLocation:VehicleLocationStatus|null;mapConfig?:MapConfiguration}){
  const container=useRef<HTMLDivElement>(null),map=useRef<maplibregl.Map|null>(null),marker=useRef<maplibregl.Marker|null>(null),vehicleMarker=useRef<maplibregl.Marker|null>(null),watch=useRef<number|null>(null),follow=useRef(false);
  const [mapState,setMapState]=useState<'LOADING'|'AVAILABLE'|'OFFLINE'>('LOADING'); const [mapReady,setMapReady]=useState(0),[mapDetail,setMapDetail]=useState('');
  const [device,setDevice]=useState<DeviceLocation|null>(null),[deviceStatus,setDeviceStatus]=useState('DEVICE LOCATION NOT REQUESTED');
  const [address,setAddress]=useState<AddressHierarchy|null>(null),[addressStatus,setAddressStatus]=useState('ADDRESS NOT RESOLVED');
  const [routeStart,setRouteStart]=useState(''),[routeDestination,setRouteDestination]=useState(''),[route,setRoute]=useState<RouteResult|null>(null),[routeStatus,setRouteStatus]=useState('ROUTING SERVICE UNAVAILABLE');
  const style=useMemo(()=>resolveMapStyle(),[]),fallbackStyle=useMemo(()=>resolveMapFallbackStyle(),[]),provider=useMemo(()=>resolveMapProvider(),[]);
  const initialMap=mapConfig?.location_configured?mapConfig:INDIA;

  const stopFollowing=useCallback(()=>{if(watch.current!==null){navigator.geolocation.clearWatch(watch.current);watch.current=null;}follow.current=false;},[]);
  useEffect(()=>()=>stopFollowing(),[stopFollowing]);

  useEffect(()=>{
    if(!container.current||map.current)return;
    let styleReady=false,fallbackAttempted=false,lastRequest=style;
    const instance=new maplibregl.Map({container:container.current,style,center:[initialMap.longitude,initialMap.latitude],zoom:initialMap.zoom,transformRequest:(url)=>{lastRequest=url;return {url};}});
    const resizeObserver=new ResizeObserver(()=>instance.resize());
    resizeObserver.observe(container.current);
    map.current=instance;instance.addControl(new maplibregl.NavigationControl({visualizePitch:true}),'top-right');instance.addControl(new maplibregl.ScaleControl({maxWidth:110,unit:'metric'}),'bottom-left');
    instance.once('style.load',()=>{styleReady=true;setMapState('AVAILABLE');setMapDetail(fallbackAttempted?'OPENFREEMAP FALLBACK STYLE ACTIVE':'');setMapReady(value=>value+1);});
    const onMapError=(event:{error?:unknown})=>{
      const error=event.error as {message?:unknown;url?:unknown}|undefined;
      const failedUrl=typeof error?.url==='string'?error.url:lastRequest;
      const detail=`MAP RESOURCE FAILED: ${failedUrl}`;
      if(!styleReady&&!fallbackAttempted&&fallbackStyle){fallbackAttempted=true;setMapState('LOADING');setMapDetail(`${detail} — RECOVERING WITH OPENFREEMAP FALLBACK`);instance.setStyle(fallbackStyle);return;}
      setMapState('OFFLINE');setMapDetail(detail);
    };
    instance.on('error',onMapError);
    const pauseFollow=()=>{if(follow.current){stopFollowing();setDeviceStatus('DEVICE FOLLOW PAUSED BY MAP PAN');}};
    instance.on('dragstart',pauseFollow);
    requestAnimationFrame(()=>instance.resize());
    return()=>{resizeObserver.disconnect();instance.off('dragstart',pauseFollow);instance.off('error',onMapError);marker.current?.remove();marker.current=null;vehicleMarker.current?.remove();vehicleMarker.current=null;instance.remove();map.current=null;};
  },[fallbackStyle,style,stopFollowing,initialMap.latitude,initialMap.longitude,initialMap.zoom]);

  const updateDeviceLayer=useCallback((location:DeviceLocation)=>{
    const instance=map.current;if(!instance||!instance.isStyleLoaded())return;
    const point:GeoJSON.Feature<GeoJSON.Point>={type:'Feature',properties:{label:'DEVICE LOCATION — NOT TARK VEHICLE'},geometry:{type:'Point',coordinates:[location.longitude,location.latitude]}};
    const data:GeoJSON.FeatureCollection={type:'FeatureCollection',features:[point,accuracyRing(location)]};
    const source=instance.getSource('tark-device-location') as maplibregl.GeoJSONSource|undefined;
    if(source)source.setData(data);else{instance.addSource('tark-device-location',{type:'geojson',data});instance.addLayer({id:'tark-device-accuracy-fill',type:'fill',source:'tark-device-location',filter:['==','$type','Polygon'],paint:{'fill-color':'#2ac5f4','fill-opacity':0.13}});instance.addLayer({id:'tark-device-accuracy-line',type:'line',source:'tark-device-location',filter:['==','$type','Polygon'],paint:{'line-color':'#2ac5f4','line-width':1}});}
    if(!marker.current)marker.current=new maplibregl.Marker({color:'#2ac5f4'}).setLngLat([location.longitude,location.latitude]).setPopup(new maplibregl.Popup({offset:18}).setText('DEVICE LOCATION — NOT TARK VEHICLE')).addTo(instance);else marker.current.setLngLat([location.longitude,location.latitude]);
  },[]);
  useEffect(()=>{const value=vehicleLocation?.location,instance=map.current;
    if(!instance)return;
    if(!value||vehicleLocation?.state!=='ONLINE'||value.status!=='ONLINE'){
      vehicleMarker.current?.remove();vehicleMarker.current=null;
      if(instance.isStyleLoaded()){
        for(const id of ['tark-vehicle','tark-vehicle-trail']){
          const source=instance.getSource(id) as maplibregl.GeoJSONSource|undefined;
          source?.setData({type:'FeatureCollection',features:[]});
        }
      }
      return;
    }
    if(!instance.isStyleLoaded())return;const label=vehicleLocationLabel(value.source);const point:GeoJSON.Feature<GeoJSON.Point>={type:'Feature',properties:{label},geometry:{type:'Point',coordinates:[value.longitude_deg,value.latitude_deg]}};const features:GeoJSON.Feature[]=[point];if(validAccuracy(value.horizontal_accuracy_m))features.push(vehicleAccuracyRing(value));const data:GeoJSON.FeatureCollection={type:'FeatureCollection',features};const source=instance.getSource('tark-vehicle') as maplibregl.GeoJSONSource|undefined;if(source)source.setData(data);else{instance.addSource('tark-vehicle',{type:'geojson',data});instance.addLayer({id:'tark-vehicle-accuracy-fill',type:'fill',source:'tark-vehicle',filter:['==','$type','Polygon'],paint:{'fill-color':'#f1b84a','fill-opacity':0.1}});instance.addLayer({id:'tark-vehicle-accuracy-line',type:'line',source:'tark-vehicle',filter:['==','$type','Polygon'],paint:{'line-color':'#f1b84a','line-width':1}});instance.addLayer({id:'tark-vehicle-dot',type:'circle',source:'tark-vehicle',filter:['==','$type','Point'],paint:{'circle-radius':10,'circle-color':value.source==='SIMULATION'?'#f1b84a':'#3dbd89','circle-stroke-color':'#08111d','circle-stroke-width':2}});}if(!vehicleMarker.current){const element=document.createElement('div'),direction=document.createElement('span'),labelElement=document.createElement('span');element.className='tark-vehicle-marker';direction.className='vehicle-direction';direction.textContent='▲';labelElement.className='vehicle-marker-label';labelElement.textContent=label;element.append(direction,labelElement);element.setAttribute('aria-label',label);vehicleMarker.current=new maplibregl.Marker({element,anchor:'bottom'}).setLngLat([value.longitude_deg,value.latitude_deg]).addTo(instance);}else{vehicleMarker.current.setLngLat([value.longitude_deg,value.latitude_deg]);const element=vehicleMarker.current.getElement(),labelElement=element.querySelector('.vehicle-marker-label');if(labelElement)labelElement.textContent=label;element.setAttribute('aria-label',label);}const markerElement=vehicleMarker.current.getElement(),headingElement=markerElement.querySelector<HTMLElement>('.vehicle-direction');if(headingElement){
      const known=validHeading(value.heading_deg);
      headingElement.textContent=known?'▲':'●';
      headingElement.style.transform=known?`rotate(${value.heading_deg}deg)`:'none';
      headingElement.setAttribute('aria-label',known?'Vehicle heading':'Heading unknown');
    }const breadcrumbs=vehicleLocation?.breadcrumbs||[];const trailData:GeoJSON.FeatureCollection={type:'FeatureCollection',features:breadcrumbs.length>1?[{type:'Feature',properties:{source:value.source},geometry:{type:'LineString',coordinates:breadcrumbs.map(item=>[item.longitude_deg,item.latitude_deg])}} as GeoJSON.Feature<GeoJSON.LineString>]:[]};const trailSource=instance.getSource('tark-vehicle-trail') as maplibregl.GeoJSONSource|undefined;if(trailSource)trailSource.setData(trailData);else{instance.addSource('tark-vehicle-trail',{type:'geojson',data:trailData});instance.addLayer({id:'tark-vehicle-trail-line',type:'line',source:'tark-vehicle-trail',paint:{'line-color':'#f1b84a','line-width':3,'line-opacity':.8}});}},[vehicleLocation,mapReady]);
  useEffect(()=>{if(device)updateDeviceLayer(device);},[device,mapReady,updateDeviceLayer]);
  const showDevice=useCallback((location:DeviceLocation,center:boolean)=>{setDevice(location);setAddress(null);setAddressStatus('ADDRESS NOT RESOLVED');updateDeviceLayer(location);if(center)map.current?.flyTo({center:[location.longitude,location.latitude],zoom:Math.max(map.current.getZoom(),15),essential:true});},[updateDeviceLayer]);
  const locate=useCallback(()=>{
    if(!navigator.geolocation){setDeviceStatus('DEVICE LOCATION UNAVAILABLE');return;}setDeviceStatus('REQUESTING DEVICE LOCATION');
    navigator.geolocation.getCurrentPosition(position=>{const location={latitude:position.coords.latitude,longitude:position.coords.longitude,accuracy:position.coords.accuracy,timestamp:position.timestamp};showDevice(location,true);setDeviceStatus(`DEVICE LOCATION — ±${Math.round(location.accuracy)} m — NOT TARK VEHICLE`);},error=>setDeviceStatus(error.code===error.PERMISSION_DENIED?'DEVICE LOCATION PERMISSION DENIED':'DEVICE LOCATION UNAVAILABLE'),{enableHighAccuracy:true,timeout:10_000,maximumAge:30_000});
  },[showDevice]);
  const toggleFollow=useCallback(()=>{
    if(follow.current){stopFollowing();setDeviceStatus('DEVICE FOLLOW STOPPED');return;}if(!navigator.geolocation){setDeviceStatus('DEVICE LOCATION UNAVAILABLE');return;}follow.current=true;setDeviceStatus('FOLLOWING DEVICE LOCATION — NOT TARK VEHICLE');watch.current=navigator.geolocation.watchPosition(position=>{const location={latitude:position.coords.latitude,longitude:position.coords.longitude,accuracy:position.coords.accuracy,timestamp:position.timestamp};showDevice(location,true);},()=>{stopFollowing();setDeviceStatus('DEVICE FOLLOW UNAVAILABLE');},{enableHighAccuracy:true,maximumAge:15_000,timeout:15_000});
  },[showDevice,stopFollowing]);
  const resolveAddress=useCallback(async()=>{if(!device)return;setAddressStatus('RESOLVING ADDRESS');try{setAddress(await reverseGeocode(device));setAddressStatus('ADDRESS RESOLVED — PROVIDER DATA');}catch{setAddressStatus('ADDRESS UNAVAILABLE — COORDINATES RETAINED');}},[device]);
  const drawRoute=useCallback((result:RouteResult)=>{const instance=map.current;if(!instance||!instance.isStyleLoaded())return;const data={type:'Feature',properties:{provider:result.provider},geometry:{type:'LineString',coordinates:result.coordinates}} as GeoJSON.Feature<GeoJSON.LineString>;const source=instance.getSource('tark-route') as maplibregl.GeoJSONSource|undefined;if(source)source.setData(data);else{instance.addSource('tark-route',{type:'geojson',data});instance.addLayer({id:'tark-route-line',type:'line',source:'tark-route',paint:{'line-color':'#f1b84a','line-width':4,'line-opacity':0.9}});}if(result.coordinates.length>1){const bounds=result.coordinates.reduce((box,coordinate)=>box.extend(coordinate),new maplibregl.LngLatBounds(result.coordinates[0],result.coordinates[0]));instance.fitBounds(bounds,{padding:70,maxZoom:16});}},[]);
  const requestRoute=useCallback(async()=>{const start=pointFromText(routeStart),destination=pointFromText(routeDestination);if(!start||!destination){setRouteStatus('ENTER START AND DESTINATION AS latitude, longitude');return;}setRouteStatus('REQUESTING ROUTE');try{const result=await calculateRoute(start,destination);if(result.coordinates.length<2)throw new Error('Route geometry unavailable');setRoute(result);drawRoute(result);setRouteStatus(`ROUTE AVAILABLE — ${result.provider}`);}catch(error){setRoute(null);setRouteStatus(error instanceof ApiError&&error.status===503?'ROUTING SERVICE UNAVAILABLE':`ROUTE UNAVAILABLE — ${error instanceof Error?error.message:'INVALID RESPONSE'}`);}},[drawRoute,routeDestination,routeStart]);
  const clearRoute=useCallback(()=>{setRoute(null);setRouteStatus('ROUTING SERVICE UNAVAILABLE');const instance=map.current;if(instance?.getLayer('tark-route-line'))instance.removeLayer('tark-route-line');if(instance?.getSource('tark-route'))instance.removeSource('tark-route');},[]);
  const tracks=snapshot.tracks.slice(0,12);

  return <section className="map-page" aria-label="Map and route monitoring">
    <header className="page-heading"><div><p className="eyebrow">MAP / ROUTE / LOCAL RADAR</p><h1>Operational map</h1><p>Browser device location, future vehicle GNSS, route data and local radar are deliberately separate data layers.</p>{mapDetail&&<p className="map-resource-status" role="status">{mapDetail}</p>}</div><span className={`pill ${mapState==='AVAILABLE'?'ok':'warn'}`}>MAP {mapState}</span></header>
    <div className="map-toolbar"><button onClick={()=>map.current?.flyTo({center:[INDIA_VIEW.longitude,INDIA_VIEW.latitude],zoom:INDIA_VIEW.zoom,essential:true})}>INDIA OVERVIEW</button><button onClick={()=>map.current?.flyTo({center:[WORLD.longitude,WORLD.latitude],zoom:WORLD.zoom,essential:true})}>WORLD VIEW</button><button onClick={locate}>Locate me</button><button onClick={toggleFollow}>{follow.current?'STOP DEVICE FOLLOW':'FOLLOW DEVICE'}</button><span>{provider}</span></div>
    <div className="map-layout"><div className="map-canvas-wrap"><div ref={container} className="map-canvas"/><div className="map-overlay"><strong>RADAR LOCAL FRAME — VEHICLE RELATIVE</strong><small>Not geographic coordinates; not placed on the global map.</small>{tracks.map(track=>{const p=radarLocalPoint(track.x_m,track.y_m);const distance=Math.hypot(track.x_m,track.y_m);const label=`Track ${track.track_id}: ${distance.toFixed(1)} m`;return <span aria-label={label} className="radar-dot" style={p} key={track.track_id} title={label}><b aria-hidden="true">{track.track_id}</b></span>;})}</div></div>
      <aside className="map-sidebar"><section><h2>Device location</h2><p className="status-line">{deviceStatus}</p><p>{device?coordinateText(device):'No browser coordinates retained.'}</p><p>{device?`Accuracy: ±${Math.round(device.accuracy)} m`:'Browser location is only requested by the operator.'}</p><button disabled={!device} onClick={()=>void resolveAddress()}>RESOLVE ADDRESS</button><p>{addressStatus}</p><p>{addressText(address)}</p></section><section><h2>TARK vehicle location</h2><p className="status-line">{vehicleLocationStatusLabel(vehicleLocation?.state,vehicleLocation?.location?.source)}</p><p>{vehicleLocation?.location?`${vehicleLocation.state==='ONLINE'?'':'LAST KNOWN — '}${vehicleLocation.location.latitude_deg.toFixed(6)}, ${vehicleLocation.location.longitude_deg.toFixed(6)}`:vehicleLocation?.reason||'VEHICLE LOCATION NOT AVAILABLE'}</p>{vehicleLocation?.location&&<><p>{vehicleLocationLabel(vehicleLocation.location.source)} · {vehicleLocation.location.fix_type} · ±{validAccuracy(vehicleLocation.location.horizontal_accuracy_m)?vehicleLocation.location.horizontal_accuracy_m:'UNKNOWN'} m</p><p>Heading: {validHeading(vehicleLocation.location.heading_deg)?vehicleLocation.location.heading_deg.toFixed(0):'UNKNOWN'}° · Freshness: {vehicleLocation.location.freshness_ms?.toFixed(0)??'UNKNOWN'} ms</p></>}<small>Vehicle GNSS is a separate hardware contract. Browser location never becomes vehicle telemetry.</small></section><section><h2>Route / navigation</h2><label>Route start coordinates<input aria-label="Route start coordinates" value={routeStart} onChange={event=>setRouteStart(event.target.value)} placeholder="latitude, longitude"/></label><label>Route destination coordinates<input aria-label="Route destination coordinates" value={routeDestination} onChange={event=>setRouteDestination(event.target.value)} placeholder="latitude, longitude"/></label><div className="button-row"><button onClick={()=>void requestRoute()}>CALCULATE ROUTE</button><button onClick={clearRoute}>CLEAR ROUTE</button></div><p className="status-line">{routeStatus}</p>{route&&<p>{(route.distance_m/1000).toFixed(2)} km · {(route.duration_s/60).toFixed(1)} min · provider: {route.provider}</p>}<small>Only provider-returned geometry is drawn. Navigation is not a safety input.</small></section></aside></div>
  </section>;
}
