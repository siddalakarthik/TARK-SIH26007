import {describe,expect,test} from 'vitest';
import {OPEN_FREE_MAP_FALLBACK_STYLE_URL,OPEN_FREE_MAP_STYLE_URL,resolveMapFallbackStyle,resolveMapProvider,resolveMapStyle} from './mapConfig';

describe('default key-free map configuration',()=>{
  test('uses OpenFreeMap Liberty when no provider is configured',()=>{
    expect(resolveMapStyle({})).toBe(OPEN_FREE_MAP_STYLE_URL);
    expect(resolveMapProvider({})).toContain('OpenFreeMap');
    expect(resolveMapFallbackStyle({})).toBe(OPEN_FREE_MAP_FALLBACK_STYLE_URL);
  });
  test('prefers explicit generic style then legacy MapTiler compatibility',()=>{
    expect(resolveMapStyle({VITE_MAP_STYLE_URL:'https://example.test/style.json',VITE_MAPTILER_STYLE_URL:'https://legacy.test/style.json'})).toBe('https://example.test/style.json');
    expect(resolveMapStyle({VITE_MAPTILER_STYLE_URL:'https://legacy.test/style.json'})).toBe('https://legacy.test/style.json');
    expect(resolveMapFallbackStyle({VITE_MAP_STYLE_URL:'https://example.test/style.json'})).toBeNull();
  });
});
