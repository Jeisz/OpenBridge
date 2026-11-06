import {useEffect} from 'react';
const defaults={color:'#30343a',distance:4,blur:10,light:12,dark:45,angle:135,inset:false};
const storageKey='openbridge-submit-appearance-v1';
function variables(p){
 const radians=p.angle*Math.PI/180,x=Math.round(Math.cos(radians)*p.distance),y=Math.round(Math.sin(radians)*p.distance),inside=p.inset?'inset ':'';
 return {'--submit-shadow-x':`${x}px`,'--submit-shadow-y':`${y}px`,'--submit-shadow-blur':`${p.blur}px`,'--submit-shadow-dark':p.dark/100,'--submit-shadow-light':p.light/100,'--submit-shadow-inset':inside||' ','--submit-surface':p.color,'--submit-shadow':`${inside}${x}px ${y}px ${p.blur}px rgb(0 0 0 / ${p.dark}%), ${inside}${-x}px ${-y}px ${p.blur}px rgb(255 255 255 / ${p.light}%)`};
}
function apply(p){for(const [key,value] of Object.entries(variables(p)))document.documentElement.style.setProperty(key,value);}
export function ButtonAppearance(){
 useEffect(()=>{
  let value=defaults;
  try{const stored=JSON.parse(localStorage.getItem(storageKey));if(stored&&/^#[0-9a-f]{6}$/i.test(stored.color)&&['distance','blur','light','dark','angle'].every(k=>Number.isFinite(stored[k])&&stored[k]>=0&&stored[k]<=360))value={...defaults,...stored};}catch{}
  apply(value);
 },[]);
 return null;
}
