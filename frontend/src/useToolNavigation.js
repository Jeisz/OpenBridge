import {restReturningCard} from './cardReturnState.mjs';
import {useEffect,useRef,useState} from 'react';
import {flushSync} from 'react-dom';
const readId=()=>location.hash.startsWith('#herramienta/')?location.hash.slice(13):null;
const ease='cubic-bezier(.22,1,.36,1)';
export function useToolNavigation(){
 const [id,setId]=useState(readId);
 const current=useRef(id),saved=useRef({focus:null}),busy=useRef(false),cleanup=useRef(()=>{}),returnCleanup=useRef(()=>{});
 function change(next){
  if(next===current.current)return;
  cleanup.current();returnCleanup.current();
  const opening=next!==null,previous=current.current;
  const card=document.querySelector(`[data-tool-id="${CSS.escape(opening?next:previous)}"].tool-card`);
  if(!opening)returnCleanup.current=restReturningCard(card);
  if(opening&&previous===null)saved.current.focus=document.activeElement;
  if(opening){current.current=next;flushSync(()=>setId(next));}
  const shell=document.querySelector('.tool-modal-shell'),overlay=document.querySelector('.tool-modal-overlay');
  const animations=[];let done=false;
  busy.current=true;
  const finish=()=>{
   if(done)return;done=true;animations.forEach(animation=>animation.cancel());busy.current=false;
   if(opening)document.querySelector('#detail-title')?.focus({preventScroll:true});
   else{
    current.current=null;flushSync(()=>setId(null));
    if(saved.current.focus?.isConnected)saved.current.focus.focus({preventScroll:true});
    else document.querySelector('#search')?.focus({preventScroll:true});
   }
  };
  cleanup.current=finish;
  if(matchMedia('(prefers-reduced-motion: reduce)').matches||!shell){finish();return;}
  const options={duration:opening?320:240,easing:ease,fill:'both'};
  const slide=shell.animate(opening?[{transform:'translateX(calc(100% + 32px))'},{transform:'translateX(0)'}]:[{transform:'translateX(0)'},{transform:'translateX(calc(100% + 32px))'}],options);
  animations.push(slide,overlay.animate(opening?[{backgroundColor:'#0000'},{backgroundColor:'#0008'}]:[{backgroundColor:'#0008'},{backgroundColor:'#0000'}],options));
  slide.finished.then(finish).catch(()=>{});
 }
 useEffect(()=>{
  const sync=()=>change(readId());window.addEventListener('hashchange',sync);
  return()=>{window.removeEventListener('hashchange',sync);cleanup.current();returnCleanup.current();};
 },[]);
 function open(next,focus){
  if(busy.current)return;
  focus?.focus({preventScroll:true});
  history.pushState({...history.state,openbridgeDetail:true},'',`#herramienta/${next}`);change(next);
 }
 function back(){
  if(busy.current)cleanup.current();
  if(current.current===null)return;
  if(history.state?.openbridgeDetail)history.back();
  else{history.replaceState(null,'','#catalogo');change(null);}
 }
 function toLanding(hash){
  if(busy.current)return;
  history.pushState(null,'',hash);change(null);
  if(!current.current)document.querySelector(hash)?.scrollIntoView({behavior:'instant'});
 }
 return {id,open,back,toLanding};
}
