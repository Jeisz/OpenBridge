import {useCallback,useEffect,useLayoutEffect,useRef,useState} from 'react';
import {assistantStickyTop,assistantDepthProgress,atAssistantEnd,catalogWheelIntent,catalogGesturePause,catalogScrollEase} from './catalogSurface.mjs';

const reducedMotion=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
const excluded=target=>target?.closest?.('textarea,input,select,pre,[contenteditable="true"],[role="listbox"],[role="menu"],[role="dialog"],[role="scrollbar"]');

// Both surfaces stay mounted. Only the catalog's participation in document flow changes.
export function useWorkspaceView(pending,paused=false){
 const [mode,setMode]=useState('initial');
 const [covered,setCovered]=useState(false);
 const [travelRevision,setTravelRevision]=useState(0);
 const [offer,setOffer]=useState(false);
 const assistantRef=useRef(null),catalogRef=useRef(null),buttonRef=useRef(null);
 const modeRef=useRef(mode),returnY=useRef(0),opening=useRef(false),action=useRef(null);
 const cancelMotion=useRef(()=>{}),wasPending=useRef(false),pausedRef=useRef(paused);
 modeRef.current=mode;pausedRef.current=paused;
 const active=mode!=='initial',unlocked=mode==='catalog';
 const writeHash=useCallback(hash=>{
  if(location.hash!==hash)history.pushState(null,'',hash);
 },[]);
 const openCatalog=useCallback((history=true)=>{
  if(pausedRef.current)return;
  cancelMotion.current();setOffer(false);
  if(modeRef.current!=='catalog')returnY.current=window.scrollY;
  opening.current=true;action.current='open';
  if(history)writeHash('#catalogo');
  if(modeRef.current==='initial'){
   // Initial navigation uses the same measured scroll, without locking on return.
   setCovered(false);action.current=null;
   document.getElementById('catalogo')?.scrollIntoView({behavior:reducedMotion()?'instant':'smooth'});
   opening.current=false;
  }else{setMode('catalog');setTravelRevision(n=>n+1);}
 },[writeHash]);
 const returnToAssistant=useCallback((history=true)=>{
  if(history)writeHash('#asistente');
  action.current='return';setOffer(false);
  // A revision triggers the layout effect even when the catalog is already open.
  setTravelRevision(n=>n+1);
 },[writeHash]);
 const navigate=useCallback(event=>{
  event.preventDefault();
  const shell=catalogRef.current?.querySelector('.catalog-shell');
  const inCatalog=modeRef.current!=='locked'&&shell?.getBoundingClientRect().top<=Math.max(100,innerHeight*.35);
  if(inCatalog)returnToAssistant();else openCatalog();
 },[openCatalog,returnToAssistant]);
 const reset=useCallback(()=>{
  cancelMotion.current();action.current=null;opening.current=false;
  setOffer(false);setCovered(false);setMode('initial');
  history.replaceState(history.state,'','#asistente');
  window.scrollTo({top:0,behavior:'instant'});
 },[]);

 useLayoutEffect(()=>{
  if(pending&&!wasPending.current){
   cancelMotion.current();action.current=null;opening.current=false;
   if(modeRef.current==='catalog')window.scrollTo({top:returnY.current,behavior:'instant'});
   setMode('locked');setOffer(false);setCovered(false);
  }
  wasPending.current=pending;
 },[pending]);

 useLayoutEffect(()=>{
  const assistant=assistantRef.current,main=assistant?.parentElement;if(!assistant)return;
  let previousHeight=null;
  const measure=()=>{
   const height=assistant.getBoundingClientRect().height;
   if(previousHeight!==null&&modeRef.current==='catalog'&&!opening.current){
    const delta=height-previousHeight;
    if(Math.abs(delta)>1)window.scrollTo({top:window.scrollY+delta,behavior:'instant'});
   }
   previousHeight=height;
   assistant.style.setProperty('--assistant-sticky-top',`${assistantStickyTop(height,innerHeight)}px`);
   const dock=assistant.querySelector('.prompt-form-slot');
   main.style.setProperty('--catalog-offer-bottom',`${(dock?.getBoundingClientRect().height||100)+(innerWidth<=640?28:36)}px`);
  };
  const observer=new ResizeObserver(measure);observer.observe(assistant);
  const dock=assistant.querySelector('.prompt-form-slot');if(dock)observer.observe(dock);
  window.addEventListener('resize',measure);measure();
  return()=>{observer.disconnect();window.removeEventListener('resize',measure);};
 },[]);

 useLayoutEffect(()=>{
  const kind=action.current;if(!kind)return;action.current=null;
  const shell=catalogRef.current?.querySelector('.catalog-shell');if(!shell)return;
  cancelMotion.current();opening.current=true;
  shell.style.removeProperty('--catalog-drift');
  const from=window.scrollY;
  const header=document.querySelector('#root>header')?.getBoundingClientRect().height||66;
  const destination=()=>kind==='open'?window.scrollY+shell.getBoundingClientRect().top-header:mode==='initial'?0:returnY.current;
  let frame=0,start=null,finished=false;
  const finish=(interrupted=false,reconcile=false)=>{
   if(finished)return;finished=true;cancelAnimationFrame(frame);opening.current=false;
   if(interrupted&&reconcile){
    const top=shell.getBoundingClientRect().top;
    if(mode!=='initial'&&top>=innerHeight){setMode('locked');setCovered(false);}
    if(['#asistente','#catalogo'].includes(location.hash))history.replaceState(history.state,'',top<=Math.max(100,innerHeight*.35)?'#catalogo':'#asistente');
   }
   if(kind==='return'&&!interrupted&&mode!=='initial'){
    setCovered(false);setMode('locked');
    assistantRef.current?.querySelector('#prompt')?.focus({preventScroll:true});
   }
   if(kind==='open'&&!interrupted){
    const heading=document.querySelector('#catalogo h2');
    if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
   }
   window.removeEventListener('wheel',interrupt);window.removeEventListener('touchstart',interrupt);window.removeEventListener('keydown',interrupt);window.removeEventListener('resize',interrupt);motion.removeEventListener('change',interrupt);
  };
  const interrupt=event=>{if(event?.type==='keydown'&&!['ArrowUp','ArrowDown','PageUp','PageDown','Home','End','Escape',' '].includes(event.key))return;finish(true,true);};
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  const tick=now=>{
   if(start===null)start=now;
   const progress=Math.min(1,(now-start)/640);
   window.scrollTo({top:from+(destination()-from)*catalogScrollEase(progress),behavior:'instant'});
   if(progress<1)frame=requestAnimationFrame(tick);
   else finish();
  };
  cancelMotion.current=()=>finish(true);
  if(reducedMotion()){window.scrollTo({top:destination(),behavior:'instant'});finish();}
  else{
   frame=requestAnimationFrame(tick);
   window.addEventListener('wheel',interrupt,{passive:true});window.addEventListener('touchstart',interrupt,{passive:true});window.addEventListener('keydown',interrupt);window.addEventListener('resize',interrupt);motion.addEventListener('change',interrupt);
  }
  return()=>finish(true);
 },[mode,travelRevision]);

 useEffect(()=>{
  let frame=0,wasAtEnd=false,touch=null,endSince=Infinity,lastKey=-Infinity;
  let wheelIntent={last:performance.now(),armed:false,distance:0};
  const registerGesture=()=>setOffer(true);
  const atEnd=()=>atAssistantEnd(window.scrollY,document.documentElement.scrollHeight,innerHeight);
  const hideOffer=()=>{if(document.activeElement!==buttonRef.current)setOffer(false);};
  const measure=()=>{
   frame=0;if(pausedRef.current)return;
   const shell=catalogRef.current?.querySelector('.catalog-shell');
   const header=document.querySelector('#root>header')?.getBoundingClientRect().height||66;
   const top=shell?.getBoundingClientRect().top??Infinity;
   const depth=reducedMotion()?0:assistantDepthProgress(top,innerHeight,header,modeRef.current==='locked');
   assistantRef.current?.style.setProperty('--assistant-depth-scale',String(1-depth*.035));
   assistantRef.current?.style.setProperty('--assistant-depth-blur',`${(depth*3).toFixed(2)}px`);
   setCovered(modeRef.current!=='locked'&&top<=header+1);
   if(modeRef.current==='catalog'&&!opening.current&&scrollY<=returnY.current+2){
    setMode('locked');setCovered(false);hideOffer();
    if(location.hash==='#catalogo')history.replaceState(history.state,'','#asistente');
   }
   if(modeRef.current==='locked'){
    const end=atEnd();if(end&&!wasAtEnd)endSince=performance.now();
    wasAtEnd=end;if(!end){endSince=Infinity;wheelIntent.armed=false;wheelIntent.distance=0;hideOffer();}
   }
  };
  const schedule=()=>{if(!frame)frame=requestAnimationFrame(measure);};
  const eligible=event=>modeRef.current==='locked'&&!pausedRef.current&&!opening.current&&!excluded(event.target);
  const wheel=event=>{
   const now=performance.now();
   const delta=event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?innerHeight:1);
   wheelIntent=catalogWheelIntent(wheelIntent,{now,delta,eligible:eligible(event)&&!event.ctrlKey&&now-endSince>=catalogGesturePause,atEnd:atEnd(),wasAtEnd});
   if(wheelIntent.show)registerGesture();
  };
  const touchStart=event=>{touch=eligible(event)&&performance.now()-endSince>=catalogGesturePause?{y:event.touches[0]?.clientY,atEnd:atEnd()}:null;};
  const touchMove=event=>{if(touch?.atEnd&&eligible(event)&&atEnd()&&touch.y-event.touches[0]?.clientY>=40){registerGesture();touch=null;}};
  const key=event=>{
   if(!['ArrowDown','PageDown','End',' '].includes(event.key))return;
   const now=performance.now();
   if(eligible(event)&&!event.repeat&&!event.shiftKey&&now-endSince>=catalogGesturePause&&now-lastKey>=catalogGesturePause&&wasAtEnd&&atEnd()&&!(event.key===' '&&event.target.closest?.('button,a')))registerGesture();
   lastKey=now;
  };
  const sync=()=>{
   if(pausedRef.current)return;
   if(location.hash==='#catalogo'&&modeRef.current==='locked')openCatalog(false);
   else if(['#asistente','#',''].includes(location.hash)&&modeRef.current==='catalog')returnToAssistant(false);
  };
  const resize=new ResizeObserver(schedule);resize.observe(document.getElementById('landing-view'));
  window.addEventListener('resize',schedule);
  const depthMotion=matchMedia('(prefers-reduced-motion: reduce)');depthMotion.addEventListener('change',schedule);
  window.addEventListener('scroll',schedule,{passive:true});window.addEventListener('wheel',wheel,{passive:true});window.addEventListener('touchstart',touchStart,{passive:true});window.addEventListener('touchmove',touchMove,{passive:true});window.addEventListener('keydown',key);window.addEventListener('hashchange',sync);window.addEventListener('popstate',sync);schedule();
  return()=>{window.removeEventListener('resize',schedule);depthMotion.removeEventListener('change',schedule);cancelAnimationFrame(frame);resize.disconnect();window.removeEventListener('scroll',schedule);window.removeEventListener('wheel',wheel);window.removeEventListener('touchstart',touchStart);window.removeEventListener('touchmove',touchMove);window.removeEventListener('keydown',key);window.removeEventListener('hashchange',sync);window.removeEventListener('popstate',sync);};
 },[mode,paused,openCatalog,returnToAssistant]);
 useEffect(()=>{if(paused){cancelMotion.current();setOffer(false);}},[paused]);
 useEffect(()=>()=>cancelMotion.current(),[]);
 return {mode,active,unlocked,covered,offer,assistantRef,catalogRef,buttonRef,navigate,reset,openCatalog};
}
