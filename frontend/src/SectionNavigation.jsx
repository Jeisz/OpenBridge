import {useEffect,useRef,useState} from 'react';

export function SectionNavigation({paused,workspace}){
 const navRef=useRef(null);
 const [inCatalog,setInCatalog]=useState(false);
 useEffect(()=>{
  if(paused)return;
  const catalog=document.getElementById('catalogo');
  if(!catalog)return;
  let frame=0;
  const measure=()=>{
   frame=0;
   const header=navRef.current?.closest('header');
   if(header)header.dataset.scrolled=String(window.scrollY>24);
   setInCatalog(workspace?.mode!=='locked'&&catalog.getBoundingClientRect().top<=Math.max(100,window.innerHeight*.35));
  };
  const schedule=()=>{if(!frame)frame=requestAnimationFrame(measure);};
  const observer=new ResizeObserver(schedule);
  observer.observe(document.getElementById('asistente'));
  window.addEventListener('scroll',schedule,{passive:true});
  window.addEventListener('resize',schedule);
  schedule();
  return()=>{cancelAnimationFrame(frame);observer.disconnect();window.removeEventListener('scroll',schedule);window.removeEventListener('resize',schedule);};
 },[paused,workspace?.mode]);
 return <nav ref={navRef} aria-label="Principal"><a className="ui-button ui-button--secondary ui-button--compact section-switch" onClick={workspace?.navigate} href={inCatalog?'#asistente':'#catalogo'} aria-label={inCatalog?'Asistente':'Catálogo'}>
  <span className="section-switch-window" aria-hidden="true"><span className={'section-switch-labels'+(inCatalog?' is-catalog':'')}><span>Catálogo</span><span>Asistente</span></span></span>
 </a></nav>;
}
