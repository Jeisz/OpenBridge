import {memo,useCallback,useEffect,useRef,useState} from 'react';
import LightRays from './components/LightRays/LightRays';

import defaults from './data/background-light.json';

const storageKey='openbridge-light-rays-v1';
const origins={'top-left':'Arriba izquierda','top-center':'Arriba centro','top-right':'Arriba derecha',left:'Izquierda',right:'Derecha','bottom-left':'Abajo izquierda','bottom-center':'Abajo centro','bottom-right':'Abajo derecha'};
const groups=[
 ['Luz',[['intensity','Intensidad',0,2,'',.05],['glow','Resplandor',0,2,'',.05],['haze','Neblina',0,1,'',.05],['atmosphere','Atmósfera',0,1,'',.05],['saturation','Saturación',0,2,'',.05]]],
 ['Forma y dirección',[['tilt','Dirección',-60,60,'°',1],['lightSpread','Apertura',.1,2,'',.01],['rayLength','Alcance',.5,4,'',.1],['rayDensity','Densidad',.3,4,'',.1],['raySharpness','Definición',0,1,'',.05],['fadeDistance','Desvanecimiento',.3,2,'',.05]]],
 ['Movimiento y textura',[['raysSpeed','Velocidad',0,3,'',.05],['mouseInfluence','Influencia del cursor',0,1,'',.05],['noiseAmount','Grano',0,.5,'',.01]]],
];
const ranges=groups.flatMap(([,fields])=>fields);
function load(){
 try{
  const stored=JSON.parse(localStorage.getItem(storageKey)),next={...defaults};
  if(!stored)return next;
  if(Object.hasOwn(origins,stored.raysOrigin))next.raysOrigin=stored.raysOrigin;
  if(/^#[0-9a-f]{6}$/i.test(stored.color))next.color=stored.color;
  for(const [key,,min,max] of ranges)if(Number.isFinite(stored[key]))next[key]=Math.max(min,Math.min(max,stored[key]));
  return next;
 }catch{return {...defaults};}
}
export const HeroLights=memo(function HeroLights(){
 const root=useRef(null);
 const [settings,setSettings]=useState(defaults);
 useEffect(()=>{setSettings(load());},[]);
 const lighting=useRef({gradient:null,x:null,y:null,intensity:null});
 const syncBorderLight=useCallback((x,y,intensity)=>{
  const state=lighting.current;
  if(!state.gradient?.isConnected)state.gradient=root.current?.closest('.hero')?.querySelector('#prompt-background-light');
  if(!state.gradient)return;
  // Quantize updates: share the shader's direction without another animation loop.
  const qx=Math.round(x*50),qy=Math.round(y*50),power=Math.round(intensity*20)/20;
  if(state.x===qx&&state.y===qy&&state.intensity===power)return;
  Object.assign(state,{x:qx,y:qy,intensity:power});
  const form=state.gradient.closest('form');
  form?.style.setProperty('--input-light-angle',`${Math.atan2(y,x)*180/Math.PI+90}deg`);
  form?.style.setProperty('--input-light-strength',String(Math.min(.12,power*.055)));
  state.gradient.setAttribute('x1',`${50-qx}%`);state.gradient.setAttribute('y1',`${50-qy}%`);
  state.gradient.setAttribute('x2',`${50+qx}%`);state.gradient.setAttribute('y2',`${50+qy}%`);
  state.gradient.firstElementChild.setAttribute('stop-opacity',Math.min(.7,.16+power*.36));
  state.gradient.lastElementChild.setAttribute('stop-opacity',Math.min(.22,.08+power*.06));
 },[]);
 return <div ref={root} className="hero-directional-light hero-light-rays" aria-hidden="true"><LightRays {...settings} raysColor={settings.color} cursorShadow={false} clickPulse={false} maxDevicePixelRatio={1} onLightDirection={syncBorderLight}/></div>;
});
