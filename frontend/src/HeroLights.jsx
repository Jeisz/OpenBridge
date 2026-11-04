import {memo,useCallback,useEffect,useRef,useState} from 'react';
import {SlidersHorizontal,X} from 'lucide-react';
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
 const root=useRef(null),dialog=useRef(null),trigger=useRef(null);
 const [local,setLocal]=useState(false),[settings,setSettings]=useState(defaults),[saved,setSaved]=useState(defaults),[saveError,setSaveError]=useState(false);
 useEffect(()=>{setLocal(['localhost','127.0.0.1'].includes(location.hostname));const value=load();setSettings(value);setSaved(value);},[]);
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
 function close(){dialog.current.close();trigger.current?.focus({preventScroll:true});}
 function cancel(){setSettings(saved);setSaveError(false);close();}
 function save(){try{localStorage.setItem(storageKey,JSON.stringify(settings));setSaved(settings);setSaveError(false);close();}catch{setSaveError(true);}}
 function change(key,value){setSettings(current=>({...current,[key]:value}));setSaveError(false);}
 return <><div ref={root} className="hero-directional-light hero-light-rays" aria-hidden="true"><LightRays {...settings} raysColor={settings.color} cursorShadow={false} clickPulse={false} maxDevicePixelRatio={1} onLightDirection={syncBorderLight}/></div>
 {local&&<><button ref={trigger} type="button" className="light-settings-trigger ui-button" aria-label="Configurar luz del fondo" onClick={()=>dialog.current.showModal()}><SlidersHorizontal size={16}/></button>
 <dialog ref={dialog} className="submit-appearance-dialog light-settings-dialog" aria-labelledby="light-settings-title" onCancel={e=>{e.preventDefault();cancel();}} onClick={e=>{if(e.target===e.currentTarget)cancel();}}>
 <div className="submit-appearance-heading"><h2 id="light-settings-title">Luz del fondo</h2><button type="button" aria-label="Cerrar configuración de luz" onClick={cancel}><X size={20}/></button></div>
 <div className="light-settings-body"><label className="light-color-control">Color de la luz<input type="color" value={settings.color} onChange={e=>change('color',e.target.value)}/><span>{settings.color.toUpperCase()}</span></label>
 <label className="light-color-control">Origen<select aria-label="Origen" value={settings.raysOrigin} onChange={e=>change('raysOrigin',e.target.value)}>{Object.entries(origins).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
 {groups.map(([title,fields])=><fieldset key={title} className="light-settings-group"><legend>{title}</legend><div className="submit-appearance-controls">{fields.map(([key,label,min,max,unit,step])=><label key={key}><span>{label}<output>{settings[key]}{unit}</output></span><input aria-label={label} type="range" min={min} max={max} step={step} value={settings[key]} onChange={e=>change(key,Number(e.target.value))}/></label>)}</div></fieldset>)}
 </div>{saveError&&<p role="alert">No pudimos guardar la configuración en este navegador.</p>}
 <div className="submit-appearance-actions"><button type="button" className="ui-button" onClick={()=>setSettings({...defaults})}>Restablecer</button><button type="button" className="ui-button ui-button--primary" onClick={save}>Guardar</button></div>
 </dialog></>}
 </>;
});
