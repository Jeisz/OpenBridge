import {useEffect,useRef,useState} from 'react';
import {ArrowUp,SlidersHorizontal,X} from 'lucide-react';
const defaults={color:'#30343a',distance:4,blur:10,light:12,dark:45,angle:135,inset:false};
const storageKey='openbridge-submit-appearance-v1';
function variables(p){
 const radians=p.angle*Math.PI/180,x=Math.round(Math.cos(radians)*p.distance),y=Math.round(Math.sin(radians)*p.distance),inside=p.inset?'inset ':'';
 return {'--submit-shadow-x':`${x}px`,'--submit-shadow-y':`${y}px`,'--submit-shadow-blur':`${p.blur}px`,'--submit-shadow-dark':p.dark/100,'--submit-shadow-light':p.light/100,'--submit-shadow-inset':inside||' ','--submit-surface':p.color,'--submit-shadow':`${inside}${x}px ${y}px ${p.blur}px rgb(0 0 0 / ${p.dark}%), ${inside}${-x}px ${-y}px ${p.blur}px rgb(255 255 255 / ${p.light}%)`};
}
function apply(p){for(const [key,value] of Object.entries(variables(p)))document.documentElement.style.setProperty(key,value);}
export function ButtonAppearance(){
 const dialog=useRef(null),trigger=useRef(null);
 const [local,setLocal]=useState(false),[saved,setSaved]=useState(defaults),[draft,setDraft]=useState(defaults),[background,setBackground]=useState('#111418');
 useEffect(()=>{
  setLocal(['localhost','127.0.0.1'].includes(location.hostname));
  let value=defaults;
  try{const stored=JSON.parse(localStorage.getItem(storageKey));if(stored&&/^#[0-9a-f]{6}$/i.test(stored.color)&&['distance','blur','light','dark','angle'].every(k=>Number.isFinite(stored[k])&&stored[k]>=0&&stored[k]<=360))value={...defaults,...stored};}catch{}
  setSaved(value);setDraft(value);apply(value);
 },[]);
 function open(){setDraft(saved);const composer=document.querySelector('.composer');if(composer)setBackground(getComputedStyle(composer).backgroundColor);dialog.current.showModal();}
 function close(){dialog.current.close();trigger.current?.focus({preventScroll:true});}
 function save(){apply(draft);setSaved(draft);try{localStorage.setItem(storageKey,JSON.stringify(draft));}catch{}close();}
 if(!local)return null;
 return <><button ref={trigger} className="submit-appearance-trigger" type="button" aria-label="Configurar estilo del botón" onClick={open}><SlidersHorizontal size={15}/></button>
 <dialog ref={dialog} className="submit-appearance-dialog" aria-labelledby="submit-appearance-title" onClick={e=>{if(e.target===e.currentTarget)close();}}>
 <div className="submit-appearance-heading"><h2 id="submit-appearance-title">Estilo del botón</h2><button type="button" aria-label="Cerrar configuración" onClick={close}><X size={20}/></button></div>
 <div className="submit-appearance-preview" style={{backgroundColor:background,...variables(draft)}}><button className="submit-appearance-sample" type="button" aria-label="Vista previa del botón"><ArrowUp size={24}/></button></div>
 <div className="submit-appearance-controls">
 <label>Color<input type="color" value={draft.color} onChange={e=>setDraft({...draft,color:e.target.value})}/></label>
 {[["distance","Distancia",0,12,"px"],["blur","Difuminado",0,30,"px"],["light","Luz",0,40,"%"],["dark","Sombra",0,80,"%"],["angle","Dirección",0,360,"°"]].map(([key,label,min,max,unit])=><label key={key}><span>{label} <output>{draft[key]}{unit}</output></span><input type="range" min={min} max={max} value={draft[key]} onChange={e=>setDraft({...draft,[key]:Number(e.target.value)})}/></label>)}
 <label className="submit-appearance-check">Relieve interior<input type="checkbox" checked={draft.inset} onChange={e=>setDraft({...draft,inset:e.target.checked})}/></label>
 </div><div className="submit-appearance-actions"><button className="ui-button" type="button" onClick={()=>setDraft(defaults)}>Restablecer</button><button className="ui-button ui-button--primary" type="button" onClick={save}>Aplicar y guardar</button></div>
 </dialog></>;
}
