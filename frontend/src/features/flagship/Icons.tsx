import type {CSSProperties} from 'react';
const paths:Record<string,string>={
  overview:'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  map:'m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3z M9 3v15 M15 6v15',
  sensors:'M4 9a8 8 0 0 1 16 0 M7 10a5 5 0 0 1 10 0 M10 11a2 2 0 0 1 4 0 M12 13v8 M7 21h10',
  safety:'m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z m-4 9 3 3 5-6',
  logs:'M6 3h12v18H6z M9 7h6 M9 11h6 M9 15h4',
  replay:'M4 11a8 8 0 1 1 2 7 M4 4v7h7 m0-4 6 5-6 4z',
  diagnostics:'M3 12h4l3-8 4 16 3-8h4',
  settings:'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M12 2v3 M12 19v3 M2 12h3 M19 12h3 M5 5l2 2 M17 17l2 2 M5 19l2-2 M17 7l2-2',
  arrow:'M5 12h14 m-5-5 5 5-5 5',
  radar:'M12 3a9 9 0 1 0 9 9 M12 7a5 5 0 1 0 5 5 M12 12l8-8',
  camera:'M3 6h12v12H3z m12 4 6-4v12l-6-4',
  truck:'M2 7h12v10H2z M14 11h4l4 4v2h-8 M5 17v3 M18 17v3',
  connection:'M3 8a14 14 0 0 1 18 0 M6 12a9 9 0 0 1 12 0 M9 16a4 4 0 0 1 6 0 M12 20h.01',
  expand:'M3 9V3h6 M15 3h6v6 M21 15v6h-6 M9 21H3v-6',
  sun:'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M12 2v2 M12 20v2 M2 12h2 M20 12h2 M5 5l1 1 M18 18l1 1 M5 19l1-1 M18 6l1-1',
  moon:'M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10',
  pin:'M12 21s7-7 7-12a7 7 0 0 0-14 0c0 5 7 12 7 12z M12 7a2 2 0 1 0 0 4 2 2 0 0 0 0-4',
  check:'m5 12 4 4L19 6',
  warning:'m12 3 10 18H2z M12 9v5 M12 17h.01',
  sound:'m3 9 5 0 5-5v16l-5-5H3z M16 8a6 6 0 0 1 0 8 M19 5a10 10 0 0 1 0 14'
};
export function Icon({name,size=20,style}:{name:string;size?:number;style?:CSSProperties}){return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={style}><path d={paths[name]??paths.overview}/></svg>;}
