export const OPEN_FREE_MAP_STYLE_URL='https://tiles.openfreemap.org/styles/liberty';

type MapEnvironment=Record<string,string|boolean|undefined>;

export function resolveMapStyle(environment:MapEnvironment=import.meta.env):string{
  const primary=environment.VITE_MAP_STYLE_URL;
  const legacy=environment.VITE_MAPTILER_STYLE_URL;
  return typeof primary==='string'&&primary.trim()?primary.trim():typeof legacy==='string'&&legacy.trim()?legacy.trim():OPEN_FREE_MAP_STYLE_URL;
}

export function resolveMapProvider(environment:MapEnvironment=import.meta.env):string{
  if(typeof environment.VITE_MAP_STYLE_URL==='string'&&environment.VITE_MAP_STYLE_URL.trim())return 'Configured map style';
  if(typeof environment.VITE_MAPTILER_STYLE_URL==='string'&&environment.VITE_MAPTILER_STYLE_URL.trim())return 'Legacy MapTiler style';
  return 'OpenFreeMap Liberty (default)';
}
