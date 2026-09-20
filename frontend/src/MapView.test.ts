import {expect,test} from 'vitest';
import {deviceLocationMessage,radarLocalPoint,validAccuracy,validHeading,vehicleLocationLabel,vehicleLocationStatusLabel} from './mapUtils';

test('radar local scope is bounded independently of geographic map coordinates',()=>{
  expect(radarLocalPoint(3,.5)).toEqual({left:'71%',bottom:'53.5%'});
  expect(radarLocalPoint(100,-100)).toEqual({left:'95%',bottom:'5%'});
});
test('device geolocation errors remain clearly labelled',()=>{
  expect(deviceLocationMessage()).toBe('DEVICE LOCATION UNAVAILABLE');
  expect(deviceLocationMessage({code:1,PERMISSION_DENIED:1,POSITION_UNAVAILABLE:2,TIMEOUT:3,message:'denied'} as GeolocationPositionError)).toBe('DEVICE LOCATION PERMISSION DENIED');
  expect(deviceLocationMessage({code:2,PERMISSION_DENIED:1,POSITION_UNAVAILABLE:2,TIMEOUT:3,message:'missing'} as GeolocationPositionError)).toBe('DEVICE LOCATION UNAVAILABLE');
});
test('vehicle map labels remain separate from device data and only show valid optional fields',()=>{
  expect(vehicleLocationLabel('SIMULATION')).toBe('TARK VEHICLE — SIMULATION');
  expect(vehicleLocationLabel('GNSS')).toBe('TARK VEHICLE');
  expect(vehicleLocationStatusLabel('ONLINE','SIMULATION')).toBe('VEHICLE LOCATION ONLINE — TARK VEHICLE — SIMULATION');
  expect(vehicleLocationStatusLabel('STALE','GNSS')).toBe('STALE LOCATION');
  expect(validHeading(359.9)).toBe(true); expect(validHeading(360)).toBe(false);
  expect(validAccuracy(3.5)).toBe(true); expect(validAccuracy(0)).toBe(false);
});
