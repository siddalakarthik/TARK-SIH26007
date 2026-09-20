export function radarLocalPoint(xMeters:number,yMeters:number):{left:string;bottom:string}{const clamp=(value:number)=>Math.max(5,Math.min(95,value));return {left:`${clamp(50+xMeters*7)}%`,bottom:`${clamp(50+yMeters*7)}%`};}
export function deviceLocationMessage(error?:{code:number;PERMISSION_DENIED:number}):string{return !error?'DEVICE LOCATION UNAVAILABLE':error.code===error.PERMISSION_DENIED?'DEVICE LOCATION PERMISSION DENIED':'DEVICE LOCATION UNAVAILABLE';}
export function vehicleLocationLabel(source:string|undefined):string{return source==='SIMULATION'?'TARK VEHICLE — SIMULATION':'TARK VEHICLE';}
export function vehicleLocationStatusLabel(state:string|undefined,source:string|undefined):string{
  const labels:Record<string,string>={NO_RECEIVER:'VEHICLE LOCATION NOT AVAILABLE',SEARCHING:'SEARCHING FOR GNSS',NO_FIX:'NO FIX',"2D_FIX":'2D FIX',"3D_FIX":'3D FIX',STALE:'STALE LOCATION',ERROR:'GNSS ERROR',ONLINE:'VEHICLE LOCATION ONLINE'};
  const base=labels[state||'']||'VEHICLE LOCATION NOT AVAILABLE';
  return source==='SIMULATION'?`${base} — TARK VEHICLE — SIMULATION`:source==='REPLAY'?`${base} — TARK VEHICLE — REPLAY`:base;
}
export function validHeading(value:number|null|undefined):value is number{return typeof value==='number'&&Number.isFinite(value)&&value>=0&&value<360;}
export function validAccuracy(value:number|null|undefined):value is number{return typeof value==='number'&&Number.isFinite(value)&&value>0;}
