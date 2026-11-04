import {restReturningCard} from './cardReturnState.mjs';
import {settleModalOnScrollIntent} from './modalTransitionInput.mjs';
import {captureCover,animateCover,bounds} from './coverTransition';
import {useEffect,useRef,useState} from 'react';
import {flushSync} from 'react-dom';
const readId=()=>location.hash.startsWith('#herramienta/')?location.hash.slice(13):null;
const ease='cubic-bezier(.22,1,.36,1)';
const visible=r=>r&&r.top<innerHeight&&r.top+r.height>0;
const geometry=r=>({left:`${r.left}px`,top:`${r.top}px`,width:`${r.width}px`,height:`${r.height}px`});
export function useToolNavigation(){
 const [id,setId]=useState(readId);
 const current=useRef(id),saved=useRef({focus:null}),busy=useRef(false),cleanup=useRef(()=>{}),returnCleanup=useRef(()=>{});
 function change(next){
  if(next===current.current)return;
  cleanup.current();returnCleanup.current();
  const opening=next!==null,previous=current.current;
  const card=document.querySelector(`[data-tool-id="${CSS.escape(opening?next:previous)}"].tool-card`);
  if(!opening)returnCleanup.current=restReturningCard(card);
  const cardCover=card?.querySelector('.tool-card-intro');
  const source=opening?cardCover:document.querySelector('.detail-cover');
  const start=captureCover(source),sourceRect=source?bounds(source):null;
  if(opening&&previous===null)saved.current.focus=document.activeElement;
  if(opening){current.current=next;flushSync(()=>setId(next));}
  const frame=document.querySelector('.tool-modal-frame'),overlay=document.querySelector('.tool-modal-overlay');
  const cardDetails=card?.querySelector('.tool-card-details');
  const cardActions=card?.querySelectorAll('.tool-actions>a,.tool-actions>button')??[];
  const target=opening?document.querySelector('.detail-cover'):cardCover;
  const end=captureCover(target);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const animations=[];let disposeCover=()=>{},stopScrollIntent=()=>{},done=false;
  const interrupted=()=>finish();
  busy.current=true;
  const finish=()=>{
   if(done)return;done=true;stopScrollIntent();
   window.removeEventListener('resize',interrupted);document.removeEventListener('visibilitychange',interrupted);
   disposeCover();animations.forEach(a=>a.cancel());
   if(frame){frame.style.removeProperty('position');frame.style.removeProperty('left');frame.style.removeProperty('top');}
   if(card)card.style.visibility='';
   if(cardDetails){cardDetails.style.removeProperty('visibility');cardDetails.style.removeProperty('pointer-events');}
   if(source)source.style.visibility='';
   busy.current=false;
   if(opening)document.querySelector('#detail-title')?.focus({preventScroll:true});
   else{
    current.current=null;flushSync(()=>setId(null));
    if(saved.current.focus?.isConnected)saved.current.focus.focus({preventScroll:true});
    else document.querySelector('#search')?.focus({preventScroll:true});
   }
  };
  cleanup.current=finish;
  if(opening)stopScrollIntent=settleModalOnScrollIntent(overlay,document.querySelector('.tool-modal-scroll'),finish);
  window.addEventListener('resize',interrupted,{once:true});document.addEventListener('visibilitychange',interrupted,{once:true});
  const animate=(node,frames,options)=>{if(!node)return null;const a=node.animate(frames,{easing:ease,fill:'both',...options});animations.push(a);return a;};
  if(reduced){finish();return;}
  const duration=opening?560:460;
  animate(overlay,[{backgroundColor:opening?'#0000':'#0009'},{backgroundColor:opening?'#0009':'#0000'}],{duration});
  const canMorph=start&&end&&visible(sourceRect)&&visible(end.rect)&&frame&&card&&(opening||document.querySelector('.tool-modal-scroll').scrollTop<1);
  const canReturnScrolled=!opening&&frame&&card&&visible(bounds(card))&&!canMorph;
  if(canReturnScrolled){
   // Preserve the scrolled viewport and shrink its rounded shell toward the card.
   // The cover may be offscreen; bringing it back would visibly reset the scroll.
   const frameRect=bounds(frame),cardRect=bounds(card);
   const scaleX=cardRect.width/frameRect.width,scaleY=cardRect.height/frameRect.height;
   const dx=cardRect.left+cardRect.width/2-frameRect.left-frameRect.width/2;
   const dy=cardRect.top+cardRect.height/2-frameRect.top-frameRect.height/2;
   animate(document.querySelector('.tool-modal-rail'),[{opacity:1},{opacity:0}],{duration:110});
   animate(card,[{opacity:0},{opacity:1}],{duration:200,delay:duration-200});
   const returning=animate(frame,[
    {transform:'translate(0,0) scale(1)',opacity:1},
    {transform:`translate(${dx}px,${dy}px) scale(${scaleX},${scaleY})`,opacity:0}
   ],{duration});
   returning.finished.then(finish).catch(()=>{});
  }else if(canMorph){
   const frameRect=bounds(frame),cardRect=bounds(card),radius=getComputedStyle(frame).borderRadius;
   // Animate the actual rounded bounds, not a mask intersecting a fixed rectangle.
   frame.style.position='fixed';frame.style.left=`${frameRect.left}px`;frame.style.top=`${frameRect.top}px`;
   const from={...geometry(cardRect),borderRadius:'24px'},to={...geometry(frameRect),borderRadius:radius};
   animate(frame,opening?[from,to]:[to,from],{duration});
   animate(document.querySelector('.tool-modal-rail'),[{opacity:0},{opacity:0}],{duration});
   // Fade the real card footer beneath the expanding shell, then hand it back
   // before the return finishes. No duplicate controls or delayed navigation.
   animate(frame,opening?[{opacity:0},{opacity:1}]:[{opacity:1},{opacity:0}],{duration:opening?120:180,delay:opening?0:duration-180});
   if(cardDetails){
    cardDetails.style.visibility='visible';cardDetails.style.pointerEvents='none';
    animate(cardDetails,opening?[{opacity:1},{opacity:0}]:[{opacity:0},{opacity:1}],{duration:opening?120:200,delay:opening?0:duration-200});
    cardActions.forEach((button,index)=>animate(button,opening?[{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(3px)'}]:[{opacity:0,transform:'translateY(4px)'},{opacity:1,transform:'translateY(0)'}],{duration:opening?100:160,delay:opening?index*12:duration-190+index*24}));
   }
   card.style.visibility='hidden';
   if(source)source.style.visibility='hidden';
   const outerStart=opening?{rect:cardRect,radius:'24px'}:{rect:frameRect,radius};
   const outerEnd=opening?{rect:frameRect,radius}:{rect:cardRect,radius:'24px'};
   disposeCover=animateCover(start,end,target,{opening,onFinish:finish,outerStart,outerEnd});
  }else{
   const a=animate(frame,opening?[{opacity:0,transform:'translateY(12px)'},{opacity:1,transform:'translateY(0)'}]:[{opacity:1},{opacity:0,transform:'translateY(8px)'}],{duration:220});
   a?.finished.then(finish).catch(()=>{});if(!a)finish();
  }
  animate(document.querySelector('.detail-body'),opening?[{opacity:0,transform:'translateY(10px)'},{opacity:1,transform:'translateY(0)'}]:[{opacity:1},{opacity:0}],{duration:opening?260:120,delay:opening&&canMorph?280:0});
  animate(document.querySelector('.tool-modal-close'),opening?[{opacity:0,transform:'translateY(-5px) scale(.96)'},{opacity:1,transform:'translateY(0) scale(1)'}]:[{opacity:1,transform:'translateY(0) scale(1)'},{opacity:0,transform:'translateY(-3px) scale(.97)'}],{duration:opening?200:110,delay:opening&&canMorph?300:0});
  document.querySelectorAll('.detail-actions>a').forEach((button,index)=>animate(button,opening?[{opacity:0,transform:'translateY(6px)'},{opacity:1,transform:'translateY(0)'}]:[{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(3px)'}],{duration:opening?180:90,delay:opening&&canMorph?320+index*24:0}));
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
