import {useLayoutEffect,useRef,useState} from 'react';
import {fitDescription} from './fitDescription.mjs';

export function CardDescription({description,tool,onOpen}){
 const ref=useRef(null),[result,setResult]=useState({text:description,clipped:false});
 useLayoutEffect(()=>{
  const node=ref.current;if(!node)return;
  let active=true,lastWidth=-1;
  const measure=()=>{
   if(!active||!node.clientWidth)return;
   const style=getComputedStyle(node),probe=document.createElement('p');
   Object.assign(probe.style,{position:'fixed',left:'-10000px',top:'0',visibility:'hidden',pointerEvents:'none',margin:'0',width:Math.max(0,parseFloat(style.width)-1)+'px',font:style.font,lineHeight:style.lineHeight,letterSpacing:style.letterSpacing,whiteSpace:'normal',overflowWrap:style.overflowWrap});
   const text=document.createTextNode(''),suffix=document.createElement('span');
   suffix.style.whiteSpace='nowrap';suffix.textContent='… Ver más';probe.append(text,suffix);document.body.append(probe);
   const limit=parseFloat(style.lineHeight)*3+.5;
   try{
    const next=fitDescription(description,(value,clipped)=>{text.textContent=value+(clipped?' ':'');suffix.hidden=!clipped;return probe.getBoundingClientRect().height<=limit;});
    setResult(old=>old.text===next.text&&old.clipped===next.clipped?old:next);
   }finally{probe.remove();}
  };
  measure();
  const observer=new ResizeObserver(()=>{if(node.clientWidth!==lastWidth){lastWidth=node.clientWidth;measure();}});observer.observe(node);
  document.fonts.ready.then(measure);document.fonts.addEventListener('loadingdone',measure);
  return()=>{active=false;observer.disconnect();document.fonts.removeEventListener('loadingdone',measure);};
 },[description]);
 return <p ref={ref} className="card-description">{result.text}{result.clipped&&<> <span className="card-description-more">… <a className="card-read-more" href={'#herramienta/'+tool.id} aria-label={'Ver descripción completa de '+tool.name} onClick={e=>{if(!e.metaKey&&!e.ctrlKey&&!e.shiftKey&&!e.altKey){e.preventDefault();onOpen(tool.id,e.currentTarget.closest('.tool-card').querySelector('.detail-link'));}}}>Ver más</a></span></>}</p>;
}
